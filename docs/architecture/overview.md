# Architecture Overview

## User Flow

The add-on registers a single Tools menu action: `Order Deck By Frequency`.

When triggered, the add-on:

1. loads its JSON config through `mw.addonManager.getConfig(__name__)`
2. opens Anki's native `StudyDeck` dialog so the user can choose a deck
3. reads and merges the configured frequency lists
4. searches the chosen deck for all cards, new cards, and suspended cards
5. inspects each card's note fields using the configured field priority
6. ranks cards by the best frequency match it can find
7. shows a preview window with matched and unmatched examples
8. optionally applies the new-card reorder and existing-card due-date rewrite

The runtime keeps the chosen deck in-memory for that invocation only. The stored config deck name is used as the default picker selection rather than being silently applied.

## Runtime Structure

- `__init__.py` loads the add-on and calls `register()`.
- `addon.py` contains registration, config loading, ranking, preview generation, and writes.
- `docs/` holds release-facing docs plus this architecture note.

## Ranking Strategy

The ranking logic is a direct port of the notebook workflow into Anki-native APIs.

- HTML is stripped and text is normalized before matching.
- Multiple candidate forms are generated from each chosen field value.
- The first configured frequency source to introduce a word determines that word's rank.
- Cards with no match are pushed to the end as `unmatched`.

The preview shows both the top-ranked cards and the first unmatched cards so you can spot bad field choices or missing source data before writing changes.

## Data Sources

Frequency files are bundled under `data/french-frequency/`.

The default source is `data/french-frequency/fr_full.txt`, but the config supports multiple sources and multiple formats:

- `word_count`
- `word_list`
- `ranked_csv`
- `ranked_tsv`

Sources are merged in order, and the first time a word appears determines its rank.

## Write Behavior

Safe defaults matter here:

- `dry_run: true` means preview only
- new cards are reordered by scheduler position
- existing cards stay untouched unless `reschedule_existing_cards` is enabled

If direct new-card repositioning is unavailable, the add-on falls back to assigning due dates to the new cards.

## Development Notes

The repo is designed to work well in two modes:

- packaged as a `.ankiaddon` archive for installation
- symlinked into an Anki dev profile's `addons21/` folder for live iteration

Packaging excludes `.ipynb` files so the shipped add-on stays focused on runtime assets and documentation.
