# Order By Frequency Config

This page explains what you can change in [`config.json`](../config.json).

In Anki, open `Tools -> Add-ons -> Order By Frequency -> Config` to edit these settings.

## Quick Start

The default config is safe:

- `dry_run` starts as `true`, so the add-on only previews changes
- `reschedule_existing_cards` starts as `false`, so only new cards are affected
- the bundled French frequency list is used by default

If you only want to try the add-on, you usually only need to check:

- `deck_name`
- `field_priority`
- `frequency_sources`

## Full Example

```json
{
  "enabled": true,
  "deck_name": "French",
  "dry_run": true,
  "reschedule_existing_cards": false,
  "new_card_starting_position": 1,
  "new_card_step_size": 1,
  "shift_existing_new_cards": true,
  "new_card_due_start_day": 0,
  "existing_card_due_start_day": 0,
  "preview_limit": 20,
  "field_priority": [
    "French",
    "Word",
    "Expression",
    "Lemma",
    "Term",
    "Front",
    "Vocabulary",
    "Vocab"
  ],
  "frequency_sources": [
    {
      "path": "data/french-frequency/fr_full.txt",
      "format": "word_count"
    }
  ]
}
```

## Settings

### `enabled`

Turns the add-on on or off globally.

- `true`: the menu action works normally
- `false`: the add-on stays installed, but does nothing when triggered

### `deck_name`

The default deck shown in the deck picker when the add-on opens.

This does not force the add-on to use that deck. It only preselects it in the chooser.

### `dry_run`

Controls whether the add-on only previews the ranking or actually writes changes.

- `true`: show the preview only
- `false`: allow the add-on to reorder cards after confirmation

Recommended: keep this as `true` until the preview looks correct.

### `reschedule_existing_cards`

Controls whether existing non-new cards also get assigned due dates in frequency order.

- `false`: only new cards are reordered
- `true`: existing cards are changed too

This is the highest-impact setting in the file. Most users should leave it off unless they explicitly want to rewrite review order.

### `new_card_starting_position`

The starting new-card position when Anki supports direct new-card repositioning.

Example:

- `1`: put the highest-ranked new card at position 1
- `100`: start inserting the reordered cards at position 100

### `new_card_step_size`

The gap between reordered new cards when direct repositioning is available.

Example:

- `1`: cards are packed tightly in order
- `10`: cards are spaced out with gaps between them

Most users should keep this at `1`.

### `shift_existing_new_cards`

Controls whether Anki should shift other new cards when the reordered cards are inserted.

- `true`: existing new-card positions move to make room
- `false`: reordered cards are inserted without shifting the rest

If you are unsure, keep this at `true`.

### `new_card_due_start_day`

Fallback start day used only if direct new-card repositioning is unavailable and the add-on has to assign due dates instead.

Most users will never need to change this.

### `existing_card_due_start_day`

Start day used when `reschedule_existing_cards` is enabled.

Example:

- `0`: the top-ranked existing card gets due day 0
- `7`: the top-ranked existing card starts one week later

### `preview_limit`

How many ranked cards and unmatched cards are shown in the preview window.

Higher values give you more context, but make the preview longer.

### `field_priority`

An ordered list of note fields the add-on should inspect when looking for a word to match against the frequency list.

The add-on checks these in order and uses the first field that exists on the note.

Example:

```json
["French", "Word", "Front"]
```

If your target word is stored in a field called `Expression`, move `Expression` earlier in the list.

### `frequency_sources`

A list of frequency files to merge in order.

Each entry is an object with at least:

- `path`: the file path
- `format`: how the file should be read

Supported formats:

- `word_count`
- `word_list`
- `ranked_csv`
- `ranked_tsv`

Sources are merged from top to bottom. The first source that introduces a word determines that word's rank.

Example with multiple sources:

```json
[
  {
    "path": "data/french-frequency/fr_full.txt",
    "format": "word_count"
  },
  {
    "path": "/absolute/path/to/custom_words.tsv",
    "format": "ranked_tsv",
    "word_column": "word"
  }
]
```

For `ranked_csv` and `ranked_tsv`, you can also set `word_column` if the word column is not named `word`.

## Common Tweaks

### Use a Different Deck by Default

```json
"deck_name": "Spanish"
```

### Match a Different Field First

```json
"field_priority": ["Expression", "Front", "Word"]
```

### Use Your Own Frequency List

```json
"frequency_sources": [
  {
    "path": "/absolute/path/to/my-list.txt",
    "format": "word_list"
  }
]
```

## Practical Advice

- Start with `dry_run: true`
- Check the preview before writing changes
- Leave `reschedule_existing_cards` off unless you really want to change review due dates
- If too many cards are unmatched, your `field_priority` or `frequency_sources` probably need adjustment
