from __future__ import annotations

from collections.abc import Callable

from aqt import gui_hooks
from aqt.editor import Editor
from aqt.utils import showInfo

EditorButtonHandler = Callable[[Editor], None]


def register_editor_buttons() -> None:
    """Register the editor toolbar button template with Anki's editor hooks."""
    if hasattr(gui_hooks, "editor_did_init_buttons"):
        gui_hooks.editor_did_init_buttons.append(_add_editor_buttons)


def make_editor_button(
    buttons: list[str],
    editor: Editor,
    *,
    cmd: str,
    handler: EditorButtonHandler,
    tip: str,
    label: str,
    button_id: str,
    rightside: bool = True,
    toggleable: bool = False,
    icon: str | None = None,
) -> str:
    """Small wrapper around ``editor.addButton`` for reusable toolbar buttons."""
    button = editor.addButton(
        icon=icon,
        cmd=cmd,
        func=lambda current_editor: handler(current_editor),
        tip=tip,
        label=label,
        id=button_id,
        rightside=rightside,
        toggleable=toggleable,
    )
    buttons.append(button)
    return button


def _add_editor_buttons(buttons: list[str], editor: Editor) -> None:
    make_editor_button(
        buttons,
        editor,
        cmd="starter_repo_sample_editor_action",
        handler=_show_sample_editor_message,
        tip="Starter template for editor toolbar actions",
        label="Starter Action",
        button_id="starter-repo-editor-action",
    )


def _show_sample_editor_message(editor: Editor) -> None:
    note = getattr(editor, "note", None)
    note_type = ""
    if note is not None:
        try:
            note_type = note.model().get("name", "")
        except Exception:
            note_type = ""

    if note_type:
        showInfo(f"Starter editor button clicked for note type: {note_type}")
        return

    showInfo("Starter editor button clicked. Replace this handler with your add-on logic.")
