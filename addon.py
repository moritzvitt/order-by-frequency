from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import TYPE_CHECKING
import csv
import re
import unicodedata

from anki.consts import CARD_TYPE_NEW, QUEUE_TYPE_SUSPENDED
from aqt import mw
from aqt.qt import QAction, QInputDialog, QMessageBox
from aqt.utils import showInfo, showText, tooltip
from . import shared_menu

if TYPE_CHECKING:
    from anki.cards import Card
    from aqt.studydeck import StudyDeck

ADDON_NAME = "Order By Frequency"
ADDON_MENU_NAME = "Order By Frequency"
ADDON_DIR = Path(__file__).resolve().parent
BRACKET_RE = re.compile(r"\[[^\]]*\]|\([^\)]*\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[\w'’À-ÿ-]+")

DEFAULT_FIELD_PRIORITY = [
    "French",
    "Word",
    "Expression",
    "Lemma",
    "Term",
    "Front",
    "Vocabulary",
    "Vocab",
]

BUNDLED_LANGUAGE_SOURCES = [
    ("French", [{"path": "data/french-frequency/fr_full.txt", "format": "word_count"}]),
    ("English", [{"path": "data/english-frequency/en_full.txt", "format": "word_count"}]),
    ("Spanish", [{"path": "data/spanish-frequency/es_full.txt", "format": "word_count"}]),
    ("Italian", [{"path": "data/italian-frequency/it_full.txt", "format": "word_count"}]),
    ("German", [{"path": "data/german-frequency/de_full.txt", "format": "word_count"}]),
    ("Japanese", [{"path": "data/japanese-frequency/ja_full.txt", "format": "word_count"}]),
    (
        "Chinese (Simplified)",
        [{"path": "data/chinese-frequency/zh_cn_full.txt", "format": "word_count"}],
    ),
    (
        "Chinese (Traditional)",
        [{"path": "data/chinese-frequency/zh_tw_full.txt", "format": "word_count"}],
    ),
]


@dataclass
class RankedCard:
    card_id: int
    note_id: int
    deck_name: str
    field_name: str
    field_value: str
    matched_word: str | None
    rank: int
    is_new: bool
    is_suspended: bool


@dataclass
class RankingResult:
    ranked_cards: list[RankedCard]
    unknown_rank: int
    new_sorted_ids: list[int]


def register() -> None:
    """Register the Tools menu action for frequency-based reordering."""
    if mw is None:
        return

    shared_menu.add_action_to_addon_menu(
        addon_name=ADDON_MENU_NAME,
        action_text="Order Deck By Frequency",
        callback=_run_from_menu,
    )


def _run_from_menu() -> None:
    if mw is None or mw.col is None:
        return

    config = _load_config()
    if not config.get("enabled", True):
        tooltip("Order By Frequency is disabled in the add-on config.", parent=mw)
        return

    _prompt_for_deck(config)


def _prompt_for_deck(config: dict) -> None:
    assert mw is not None
    from aqt.studydeck import StudyDeck

    current_deck = config.get("deck_name") or mw.col.decks.current()["name"]

    def callback(dialog: StudyDeck) -> None:
        if not dialog.name:
            return
        _run_for_deck(config, dialog.name)

    StudyDeck(
        mw,
        current=current_deck,
        accept="Choose",
        title="Choose Deck For Frequency Ordering",
        cancel=True,
        parent=mw,
        geomKey="orderByFrequencyDeck",
        callback=callback,
        dyn=True,
    )


def _run_for_deck(config: dict, deck_name: str) -> None:
    config = dict(config)
    config["deck_name"] = deck_name
    selected_sources = _prompt_for_language_sources(config)
    if selected_sources is None:
        return

    config["frequency_sources"] = selected_sources["sources"]
    config["_selected_frequency_label"] = selected_sources["label"]

    try:
        result = _rank_cards(config)
    except Exception as exc:
        showInfo(f"{ADDON_NAME} could not build the ranking.\n\n{exc}", parent=mw)
        return

    preview = _build_preview_text(config, result)
    showText(
        preview,
        parent=mw,
        title=ADDON_NAME,
        copyBtn=True,
        plain_text_edit=True,
    )

    if config.get("dry_run", True):
        tooltip("Dry run mode is enabled. No changes were written.", parent=mw)
        return

    if not result.new_sorted_ids:
        tooltip("Nothing to reorder for the current configuration.", parent=mw)
        return

    if not _confirm_apply_ranking():
        return

    try:
        summary = _apply_ranking(config, result)
    except Exception as exc:
        showInfo(f"{ADDON_NAME} could not apply changes.\n\n{exc}", parent=mw)
        return

    mw.reset()
    showInfo(summary, parent=mw, title=ADDON_NAME)


def _load_config() -> dict:
    assert mw is not None
    config = mw.addonManager.getConfig(__name__)
    if config is None:
        raise RuntimeError("Could not load add-on config.")
    return config


def _prompt_for_language_sources(config: dict) -> dict[str, object] | None:
    assert mw is not None

    options: list[tuple[str, list[dict]]] = []
    default_label = "Use Config Sources"
    configured_sources = [dict(source) for source in config.get("frequency_sources", [])]
    if configured_sources:
        options.append((default_label, configured_sources))

    for label, sources in BUNDLED_LANGUAGE_SOURCES:
        if all(_resolve_source_path(source["path"]).exists() for source in sources):
            options.append((label, [dict(source) for source in sources]))

    if not options:
        showInfo(
            "No frequency sources are available.\n\n"
            "Add a valid source to config.json or bundle a frequency list first.",
            parent=mw,
            title=ADDON_NAME,
        )
        return None

    current_sources = config.get("frequency_sources", [])
    current_label = default_label
    for label, sources in options:
        if _same_sources(current_sources, sources):
            current_label = label
            break

    labels = [label for label, _ in options]
    current_index = labels.index(current_label) if current_label in labels else 0
    selected_label, accepted = QInputDialog.getItem(
        mw,
        ADDON_NAME,
        "Which language or source should this run use?",
        labels,
        current=current_index,
        editable=False,
    )
    if not accepted:
        return None

    for label, sources in options:
        if label == selected_label:
            return {"label": label, "sources": sources}

    return None


def _same_sources(left: list[dict], right: list[dict]) -> bool:
    left_paths = [(item.get("path"), item.get("format"), item.get("word_column")) for item in left]
    right_paths = [(item.get("path"), item.get("format"), item.get("word_column")) for item in right]
    return left_paths == right_paths


def _confirm_apply_ranking() -> bool:
    assert mw is not None

    while True:
        dialog = QMessageBox(mw)
        dialog.setWindowTitle(ADDON_NAME)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setText("Apply this frequency order to the deck now?")
        dialog.setInformativeText(
            "This will change the order of new cards in the selected deck."
        )

        apply_button = dialog.addButton("Apply Now", QMessageBox.ButtonRole.AcceptRole)
        backup_button = dialog.addButton("Make Backup First", QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(apply_button)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked == apply_button:
            return True
        if clicked == backup_button:
            if _trigger_anki_backup():
                continue
            return False
        return False


def _trigger_anki_backup() -> bool:
    assert mw is not None

    action = getattr(getattr(mw, "form", None), "actionCreateBackup", None)
    if action is None or not hasattr(action, "trigger"):
        showInfo(
            "Could not trigger Anki's built-in backup action automatically.\n\n"
            "Please use File -> Create Backup, then run Order By Frequency again.",
            parent=mw,
            title=ADDON_NAME,
        )
        return False

    action.trigger()
    tooltip("Requested an Anki backup. Review the dialog, then choose how to proceed.", parent=mw)
    return True


def _rank_cards(config: dict) -> RankingResult:
    assert mw is not None
    deck_name = config["deck_name"]
    field_priority = config.get("field_priority") or DEFAULT_FIELD_PRIORITY
    rank_map = _build_frequency_rank_map(config["frequency_sources"])
    unknown_rank = len(rank_map) + 1_000_000

    all_card_ids = list(mw.col.find_cards(f'deck:"{deck_name}"'))
    new_card_id_set = set(mw.col.find_cards(f'deck:"{deck_name}" is:new'))
    suspended_card_id_set = set(mw.col.find_cards(f'deck:"{deck_name}" is:suspended'))

    note_cache: dict[int, object] = {}
    ranked_cards: list[RankedCard] = []

    for card_id in all_card_ids:
        card = mw.col.get_card(card_id)
        note_id = int(card.nid)
        note = note_cache.get(note_id)
        if note is None:
            note = mw.col.get_note(card.nid)
            note_cache[note_id] = note

        field_names = list(note.keys())
        field_name = _choose_primary_field(field_names, field_priority)
        field_value = note[field_name] if field_name else ""
        normalized_field_value = normalize_text(field_value)

        matched_word = None
        matched_rank = unknown_rank
        for candidate in candidate_forms(field_value):
            rank = rank_map.get(candidate)
            if rank is not None and rank < matched_rank:
                matched_rank = rank
                matched_word = candidate

        is_new = card_id in new_card_id_set or int(card.type) == int(CARD_TYPE_NEW)
        is_suspended = card_id in suspended_card_id_set or int(card.queue) == int(QUEUE_TYPE_SUSPENDED)

        ranked_cards.append(
            RankedCard(
                card_id=int(card_id),
                note_id=note_id,
                deck_name=_safe_deck_name(card),
                field_name=field_name,
                field_value=normalized_field_value,
                matched_word=matched_word,
                rank=matched_rank,
                is_new=is_new,
                is_suspended=is_suspended,
            )
        )

    ranked_cards.sort(
        key=lambda item: (
            item.rank,
            item.matched_word or "",
            item.field_value,
            item.card_id,
        )
    )

    new_sorted_ids = [
        item.card_id for item in ranked_cards if item.is_new and not item.is_suspended
    ]
    return RankingResult(
        ranked_cards=ranked_cards,
        unknown_rank=unknown_rank,
        new_sorted_ids=new_sorted_ids,
    )


def _apply_ranking(config: dict, result: RankingResult) -> str:
    assert mw is not None

    lines: list[str] = []

    if result.new_sorted_ids:
        _reposition_new_cards(config, result.new_sorted_ids)
        lines.append(
            f"Repositioned {len(result.new_sorted_ids)} new cards in deck '{config['deck_name']}'."
        )
    else:
        lines.append("No new cards needed reordering.")

    return "\n".join(lines)


def _reposition_new_cards(config: dict, card_ids: list[int]) -> None:
    assert mw is not None

    if hasattr(mw.col.sched, "reposition_new_cards"):
        mw.col.sched.reposition_new_cards(
            card_ids=card_ids,
            starting_from=int(config.get("new_card_starting_position", 1)),
            step_size=int(config.get("new_card_step_size", 1)),
            randomize=False,
            shift_existing=bool(config.get("shift_existing_new_cards", True)),
        )
        return

    start_day = int(config.get("new_card_due_start_day", 0))
    for offset, card_id in enumerate(card_ids, start=start_day):
        mw.col.sched.set_due_date([card_id], str(offset))


def _build_preview_text(config: dict, result: RankingResult) -> str:
    preview_limit = max(1, int(config.get("preview_limit", 20)))
    matched_cards = [
        item for item in result.ranked_cards if item.rank < result.unknown_rank
    ]
    unmatched_cards = [
        item for item in result.ranked_cards if item.rank >= result.unknown_rank
    ]

    lines = [
        ADDON_NAME,
        "",
        f"Deck: {config['deck_name']}",
        f"Language/source: {config.get('_selected_frequency_label', 'Configured Sources')}",
        f"Dry run: {config.get('dry_run', True)}",
        f"Frequency sources: {len(config.get('frequency_sources', []))}",
        "",
        f"All cards: {len(result.ranked_cards)}",
        f"Matched cards: {len(matched_cards)}",
        f"Unmatched cards: {len(unmatched_cards)}",
        f"New cards to reorder: {len(result.new_sorted_ids)}",
        "",
        f"Top {min(preview_limit, len(result.ranked_cards))} ranked cards:",
    ]

    lines.extend(_format_ranked_rows(result.ranked_cards[:preview_limit], result.unknown_rank))
    lines.append("")
    lines.append(f"First {min(preview_limit, len(unmatched_cards))} unmatched cards:")
    lines.extend(_format_ranked_rows(unmatched_cards[:preview_limit], result.unknown_rank))
    return "\n".join(lines)


def _format_ranked_rows(rows: list[RankedCard], unknown_rank: int) -> list[str]:
    if not rows:
        return ["  (none)"]

    formatted = []
    for item in rows:
        rank = item.rank if item.rank < unknown_rank else "unmatched"
        matched = item.matched_word or "-"
        kind = "new" if item.is_new else "existing"
        suspended = " suspended" if item.is_suspended else ""
        formatted.append(
            f"  {item.card_id} | {rank} | {kind}{suspended} | "
            f"{item.field_name}: {item.field_value} | matched: {matched}"
        )
    return formatted


def _choose_primary_field(field_names: list[str], field_priority: list[str]) -> str:
    for candidate in field_priority:
        if candidate in field_names:
            return candidate
    return field_names[0] if field_names else ""


def _build_frequency_rank_map(sources: list[dict]) -> dict[str, int]:
    rank_map: dict[str, int] = {}
    next_rank = 1
    for source in sources:
        words = _load_frequency_words(source)
        for word in words:
            if word not in rank_map:
                rank_map[word] = next_rank
                next_rank += 1
    return rank_map


def _load_frequency_words(source: dict) -> list[str]:
    path = _resolve_source_path(source["path"])
    if not path.exists():
        raise FileNotFoundError(f"Frequency source not found: {path}")

    source_format = source["format"]
    if source_format == "word_count":
        words = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            word = normalize_text(line.rsplit(" ", 1)[0])
            if word:
                words.append(word)
        return words

    if source_format == "word_list":
        return [
            word
            for word in (normalize_text(line) for line in path.read_text(encoding="utf-8").splitlines())
            if word
        ]

    if source_format in {"ranked_csv", "ranked_tsv"}:
        delimiter = "," if source_format == "ranked_csv" else "\t"
        word_column = source.get("word_column", "word")
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            words = [normalize_text(row.get(word_column, "")) for row in reader]
        return [word for word in words if word]

    raise ValueError(f"Unsupported frequency source format: {source_format}")


def _resolve_source_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (ADDON_DIR / path).resolve()


def normalize_text(text: str) -> str:
    text = unescape(text or "")
    text = HTML_TAG_RE.sub(" ", text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'")
    text = WHITESPACE_RE.sub(" ", text).strip().lower()
    return text


def candidate_forms(text: str) -> list[str]:
    text = normalize_text(text)
    if not text:
        return []

    forms: list[str] = []

    def add(value: str) -> None:
        value = normalize_text(value)
        if value and value not in forms:
            forms.append(value)

    add(text)
    add(text.split("\n", 1)[0])
    add(BRACKET_RE.sub("", text))

    first_chunk = re.split(r"[;,/|]", text, maxsplit=1)[0]
    add(first_chunk)

    tokens = TOKEN_RE.findall(text)
    if tokens:
        add(tokens[0])
        if len(tokens) >= 2:
            add(" ".join(tokens[:2]))

    return forms


def _safe_deck_name(card: Card) -> str:
    if hasattr(card, "deck_name"):
        try:
            return str(card.deck_name())
        except Exception:
            return ""
    return ""
