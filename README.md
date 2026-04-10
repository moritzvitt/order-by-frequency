# Order By Frequency

This Anki add-on turns the notebook workflow in [`reschedule_french_by_frequency.ipynb`](./reschedule_french_by_frequency.ipynb) into a menu-driven add-on.

It ranks cards in a target deck against one or more local frequency lists and then:

- previews the ranking inside Anki
- repositions new cards so higher-frequency words come first
- optionally reschedules existing cards by assigning due dates in the same order

## How It Works

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

## Files

- [`addon.py`](./addon.py): main Anki integration and ranking logic
- [`config.json`](./config.json): runtime settings
- [`config.md`](./config.md): config reference
- [`data/french-frequency`](./data/french-frequency): bundled frequency lists
- [`docs/architecture/overview.md`](./docs/architecture/overview.md): runtime design notes
- [`docs/release-description.md`](./docs/release-description.md): release text draft

## Packaging

The VS Code task creates a `.ankiaddon` archive named after the repository folder.

Manual packaging:

```bash
zip -r order-by-frequency.ankiaddon . -x './.git/*' './.vscode/*' './__pycache__/*' './.DS_Store' './*.ipynb'
```
