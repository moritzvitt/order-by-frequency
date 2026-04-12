# Order By Frequency

This Anki add-on orders a deck by local word-frequency data through a simple menu-driven workflow inside Anki.

It ranks cards in a target deck against one or more local frequency lists and then:

- previews the ranking inside Anki
- repositions new cards so higher-frequency words come first
- optionally reschedules existing cards by assigning due dates in the same order

## Usage

Use `Tools -> Order Deck By Frequency` inside Anki.

The action:

1. opens a deck picker, defaulting to the configured deck
2. reads the configured frequency files from [`data/french-frequency`](./data/french-frequency)
3. scans the configured deck
4. picks a note field using the configured field priority
5. generates a preview of matched and unmatched cards
6. applies the reorder only if `dry_run` is `false` and you confirm it

## Default Setup

The default configuration targets:

- deck: `French`
- source file: [`data/french-frequency/fr_full.txt`](./data/french-frequency/fr_full.txt)
- safe mode: `dry_run: true`

That means the add-on will preview results first and will not write changes until you flip `dry_run` to `false`.

## Configuration

The most important settings in [`config.json`](./config.json) are:

- `deck_name`: the default deck highlighted in the picker
- `dry_run`: preview-only mode
- `reschedule_existing_cards`: whether non-new cards also get reassigned due dates
- `field_priority`: which note fields are checked first for a frequency match
- `frequency_sources`: one or more local frequency files merged in order

## Development

For local Anki dev setups, this repo can be symlinked into an `addons21/` directory so Anki loads it directly from your working tree.

The packaging task intentionally excludes:

- `.git/`
- `.vscode/`
- `__pycache__/`
- `.ipynb` notebooks

## Files

- [`addon.py`](./addon.py): main Anki integration and ranking logic
- [`config.json`](./config.json): runtime settings
- [`docs/config.md`](./docs/config.md): config reference
- [`docs/`](./docs/): user-facing docs, release copy, and architecture notes
- [`data/french-frequency`](./data/french-frequency): bundled frequency lists

## Packaging

The VS Code task creates a `.ankiaddon` archive named after the repository folder.

Manual packaging:

```bash
zip -r order-by-frequency.ankiaddon . -x './.git/*' './.vscode/*' './__pycache__/*' './.DS_Store' './*.ipynb'
```
