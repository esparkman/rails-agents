# Tomes catalog (template)

Optional. Tomes let the architect / story-writer agents consult a Rails
bookshelf for how/why patterns. **Books are not shipped** — they're
copyrighted; you supply your own epubs.

## Setup

1. Put your `.epub` files anywhere, then point the reader at them:
   ```sh
   export TOMES_DIR="$HOME/books"        # colon-separate multiple dirs
   ```
   (`~/Documents/books` and the macOS Books/iCloud folders are also scanned.)
2. Confirm they're visible:
   ```sh
   <harness-dir>/reference/tomes/tome.sh list
   ```
3. Fill in the topic → book map below with the titles you actually have, so the
   agents know which book to open for which question.

If you skip this, the agents simply don't use tomes — nothing breaks.

## Topic → book map (fill in your own)

| Topic / question | Book (fuzzy name for `tome.sh`) |
|---|---|
| _e.g. idiomatic Rails 8 patterns_ | _<your book>_ |
| _e.g. sustainable architecture_ | _<your book>_ |
| _e.g. PostgreSQL performance_ | _<your book>_ |

Usage: `tome.sh search "<book>" "<regex>"` or `tome.sh chapter "<book>" "<toc-text>"`;
quote the source line you rely on. `rails-mcp`, when present, stays the
authority for a given app's actual schema/routes/models — tomes are for the
"how/why," not this app's facts.
