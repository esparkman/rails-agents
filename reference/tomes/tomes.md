# Reference Tomes — curated catalog

A shelf of Rails/Ruby reference books the agents may consult for the **how/why**
behind a pattern — idiom, design, testing strategy, PostgreSQL behavior. Books are
the author's own epubs (not shipped in this repo).

## How to read a tome (all agents — you have Bash)

```sh
TOME=~/Development/rails-agents/reference/tomes/tome.sh
"$TOME" list                         # every book the shelf can see
"$TOME" find "rails 8 way"           # locate a book by fuzzy name
"$TOME" toc  "poodr"                 # table of contents
"$TOME" search "99 bottles" "shameless green"   # de-tagged grep, with context
"$TOME" chapter "eloquent ruby" "Writing Specs"  # print a section by TOC text
```

- `<book>` is a fuzzy name fragment; first match wins. Quote multi-word names.
- The shelf resolves via `$TOMES_DIR` (colon-separated) plus standard fallbacks
  (`~/Documents/books`, the vault `harness_engineering/Reference/books`, Apple Books).
  If a title lists as `[not downloaded]`, it's an iCloud stub — skip it.

## When to reach for a tome

Consult a tome when a decision turns on idiom or design judgment, not on this app's
facts. **`rails-mcp` stays the authority for THIS app's actual schema/routes/models**
— tomes are for "how/why," never for what this codebase currently contains. Prefer a
tome over training-memory when you're about to assert an idiom, a Rails 8 convention,
a testing approach, or a PostgreSQL behavior. **Quote the source line you rely on** so
the claim is checkable (per the global verify-before-asserting rule).

## Topic → book map

| Topic / question | Book (fuzzy name for `tome.sh`) |
|---|---|
| Rails 8 conventions & the modern "Rails way" | `The Rails 8 Way` |
| Idiomatic, expressive Ruby | `Eloquent Ruby` · `Polished Ruby Programming` · `Programming Ruby` (Pickaxe) |
| OO design, refactoring, small methods, naming | `Practical Object-Oriented Design` (POODR) · `99 Bottles of OOP` · `Design Patterns in Ruby` |
| Sustainable / layered app architecture | `Sustainable Web Development with Ruby on Rails` · `Layered Design for Ruby on Rails Applications` · `Growing Rails Applications in Practice` |
| Testing (Minitest + fixtures — this project's stack) | `Test Driving Rails Taking Minitest and Fixtures for a spin` · `The Minitest Cookbook` · `Rails 4 Test Prescriptions` |
| PostgreSQL performance & SQL | `High Performance PostgreSQL for Rails` · `The Art Of PostgreSQL` |
| Hotwire / Turbo / Stimulus / front-end | `The Rails and Hotwire Codex` · `Modern Front-End Development for Rails` · `Hotwire Native for Rails Developers` |
| Tailwind CSS | `Tailwind CSS Craft Beautiful Flexible and Responsive Designs` |
| Deployment / Docker / Kamal | `Docker for Rails Developers` · `Reliably Deploying Rails Applications` |
| Scaling & performance | `Rails Scales` · `High Performance PostgreSQL for Rails` |
| Robustness / edge cases | `Bulletproof Ruby on Rails Applications` |
| Craft & engineering practice | `The Pragmatic Programmer` |
| Rails internals / metaprogramming | `Crafting Rails Applications` · `Rebuilding Rails` |
| AI-assisted development patterns | `Patterns of Application Development Using AI` |

> Titles are what the shelf currently holds (dupes/editions collapse under a fuzzy
> match). If a book isn't found, `tome.sh find <name>` shows what's actually there.
