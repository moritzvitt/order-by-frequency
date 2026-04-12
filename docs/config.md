# Order By Frequency Config

This add-on stores its configuration as a JSON dictionary.

## Keys

### `enabled`

Global on/off switch for the add-on.

### `deck_name`

Default deck shown when the add-on opens its deck picker.

### `dry_run`

When `true`, the add-on only shows a preview and does not write changes.

### `reschedule_existing_cards`

When `true`, existing non-new cards are assigned new due dates in frequency order.

### `new_card_starting_position`

Start position for reordered new cards.

### `new_card_step_size`

Spacing between reordered new cards.

### `shift_existing_new_cards`

Whether Anki should shift other new cards when inserting the reordered ones.

### `new_card_due_start_day`

Fallback start day if Anki does not support direct new-card repositioning.

### `existing_card_due_start_day`

Start day used when rescheduling existing cards.

### `preview_limit`

How many ranked and unmatched cards to show in the preview window.

### `field_priority`

Ordered list of note fields to inspect when matching words against the frequency list.

### `frequency_sources`

List of frequency files to merge in order. Supported formats are `word_count`, `word_list`, `ranked_csv`, and `ranked_tsv`.

Example:

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
  "field_priority": ["French", "Word", "Front"],
  "frequency_sources": [
    {
      "path": "data/french-frequency/fr_full.txt",
      "format": "word_count"
    }
  ]
}
```
