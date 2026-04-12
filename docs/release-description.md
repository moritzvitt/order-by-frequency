# Order By Frequency

Order cards in an Anki deck by external word-frequency lists so the most common vocabulary appears first.

## Features

- previews ranked results before writing anything
- lets you choose the target deck at runtime
- repositions new cards by frequency
- can optionally reschedule existing cards too
- supports multiple local frequency sources
- includes bundled frequency data for French, English, Spanish, Italian, German, Japanese, and Chinese
- lets you choose which note fields are inspected first

## Default Behavior

The bundled config highlights a deck named `French` by default and uses the included `fr_full.txt` frequency list.

The add-on starts in `dry_run` mode, so the first run only shows a preview. Turn `dry_run` off in the add-on config when you are ready to apply changes.

## Good Fit

This is useful when your deck contains vocabulary cards and you want study order to follow real-world frequency instead of import order.

It is especially handy when you already have a large deck and want a safer, more transparent way to improve study order without hand-editing card positions.
