<!-- guardrails v1 | adapted from github.com/TheColliny/FableClaudeMDForOpus (TRAPS.md). Language-level; unchanged by OS. -->
You are here because you are touching one of the trap categories below. Find your section, follow its rows. No row covers your case and the behavior is load-bearing? Run a one-line REPL probe (`node -e` / `ruby -e` / `python3 -c` / `php -r`) and paste the output — never guess.

## Dates & times
- Never add 86400s/24h for "next day" where local time matters -> use tz-aware arithmetic / `addDays` / `timedelta(days=1)` / Ruby `+ 1.day` (DST breaks fixed offsets).
- Month arithmetic overflows on day 31: state in a comment what Jan 31 + 1 month must produce, then pick the API.
- JS: months are 0-indexed (`new Date(2024, 0, 15)` = Jan 15); `getDay()` = weekday, `getDate()` = day-of-month.
- JS parsing: `new Date('2024-01-15')` = UTC midnight; `new Date(2024, 0, 15)` = LOCAL midnight — mixing shifts dates a day.
- Year format token depends on the library family: Java/date-fns/Luxon (LDML): `yyyy`, never `YYYY` (uppercase = week-numbering year, wrong near New Year). Moment/Day.js: `YYYY` IS the calendar year. Python strftime: `%Y` (`%G` is ISO week-year). Ruby strftime: `%Y`. Unsure? Probe 2024-12-30 with both tokens and paste the output.
- Python: never compare naive and aware datetimes; `datetime.utcnow()` is naive -> use `datetime.now(timezone.utc)`.
- Rails: prefer `Time.current` / `Time.zone.now` over `Time.now` (respects app tz); `Date.current` over `Date.today`.
- Date-range filters on timestamps: `ts >= day AND ts < nextDay`, never `<= endOfDay`; annotate every range's inclusivity as `[a, b)`.
- Computed loop/slice/range bounds (pagination, chunking, windows): write a one-line trace for len=0,1,3 as a comment before the code, e.g. `# len=10,size=3 -> [0:3][3:6][6:9][9:10] = 4 chunks`; code disagrees with trace -> fix the code.
- After writing date arithmetic, trace three dates in a comment: Jan 31, Dec 31, a DST transition (e.g. 2024-03-10 US).

## Epochs & units
- Digit count: 10 = seconds, 13 = ms, 16 = µs, 19 = ns. JS `Date.now()`/`getTime()` = ms; `new Date(n)` expects ms; Python `time.time()` = s; Ruby `Time.now.to_i` = s; PHP `time()` = s; JWT exp/iat = s; `System.currentTimeMillis()` = ms.
- Name the unit into the variable: `expiresAtSec`, `timeoutMs`, `maxBytes`, `amountCents`. Every `*1000` or `/1000` gets a comment naming both units.

## Mutation vs copy
- JS mutating: `sort`, `reverse`, `splice`, `push/pop/shift/unshift`, `fill`. Copying: `toSorted`, `toReversed`, `toSpliced` (ES2023 — Node 20+; older targets `[...x].sort()`), `slice`, `concat`, spread.
- Python: `list.sort()`/`.reverse()` mutate AND return `None`. `sorted()` returns a NEW list; `reversed()` returns a lazy ONE-SHOT iterator over the ORIGINAL -> `list(reversed(x))` or `x[::-1]` for a real copy.
- Python: `x = y` never copies; `.copy()`/`list(y)`/`y[:]` are SHALLOW -> `copy.deepcopy` for nested structures.
- Ruby: `map`/`select`/`reject`/`sort` return new; `map!`/`select!`/`sort!`/`<<`/`concat` mutate in place. `dup`/`clone` are SHALLOW.
- `def f(x, acc=[])` (Python) and default arg mutation persist across calls -> `acc=None` sentinel. `[[0]*n]*m` aliases every row -> comprehension. JSON round-trip drops Dates/undefined -> `structuredClone` (Node 17+).
- Before mutating anything that arrived as a parameter or came from shared state: write one line naming who else holds a reference; if anyone might, copy first.

## Async
- Every async call is awaited, `return await`-ed inside try/catch, `.then`-chained, or explicitly `void`-ed with `// fire-and-forget`. After editing async code: Grep the file for each async function name; for every hit not preceded by `await`/`return`/`void` on that line, justify it in one line.
- Never pass an async callback to `forEach`/`filter`/`reduce` -> `for..of` + await (sequential) or `await Promise.all(items.map(...))` (parallel); state which one and why.
- Never branch on an un-awaited call: `if (asyncFn())` is always truthy.
- A value read BEFORE an await and written AFTER it may be stale — re-read after the await or comment why no concurrent writer exists.

## Floats & money
- Never `==`/`===` computed floats -> tolerance (`Math.abs(a-b) < 1e-9`, `math.isclose`, `pytest.approx`) or integers.
- Money is ALWAYS integer minor units or Decimal/BigDecimal; before finishing, grep the diff for arithmetic on `price/amount/total/fee/balance` and confirm no binary floats. JS `toFixed()` returns a STRING. Rails: use `_cents` integer columns or the `money-rails` gem, never a float column.

## Sort
- JS `.sort()` without a comparator is lexicographic: `[10,9,1].sort()` -> `[1,10,9]`. Always pass a comparator (or comment `// lexicographic intended`).
- Comparators return NUMBERS, never booleans: rewrite bare `>` as `a - b` (finite numbers), `localeCompare` (user-facing strings), or -1/0/1. `.sort()` MUTATES -> `toSorted` for a copy.

## Division & modulo
- Python `//` and `%` FLOOR (`-1 % 5 = 4`); Ruby `%` also floors (`-1 % 5 = 4`); JS/Java/C/Go/PHP `%` TRUNCATES (`-1 % 5 = -1`). Dividend can be negative? Trace one concrete negative value in a comment; nonnegative modulo in truncating languages = `((x % n) + n) % n`.
- JS numbers corrupt integers above 2^53: 64-bit IDs travel as STRINGS through JSON and JS.

## Regex & strings
- After writing any non-literal regex: probe it with `node -e`/`python3 -c`/`ruby -e` against one intended match, one near-miss, and the empty string — paste the outputs. Real inputs from the repo, not invented ones.
- Escape literal dots; anchor validations `^...$` (Python `re.match` anchors start only -> `re.fullmatch`; Ruby `\A...\z`, NOT `^...$` which match line boundaries and allow newline injection); JS `str.replace(string, x)` replaces FIRST only -> `replaceAll` or `/g`; a reused `/g` regex keeps `lastIndex` state; `$` in replacements is special -> `$$`.
- Python `str.split()` (no arg) collapses whitespace runs — not `split(' ')`. JS `'👍'.length === 2` — use `[...str]` for user-visible truncation.

## Familiar-API traps
- JS `['1','7','11'].map(parseInt)` -> `[1, NaN, 3]` (index becomes radix) -> use `Number` or `x => parseInt(x, 10)`.
- `typeof null === 'object'`; `NaN !== NaN` -> `Number.isNaN`. `JSON.stringify` drops undefined/functions; NaN/Infinity become null; Dates do not round-trip.
- Python `is` only for `None`/`True`/`False` (int/str interning passes in tests, fails in prod). `Array(3).map(f)` does nothing (holes) -> `Array.from({length: 3}, f)`.
- Ruby: `"0"`, `""`, `[]`, `0` are ALL truthy — only `nil` and `false` are falsy. `.blank?`/`.present?` (ActiveSupport) ≠ truthiness. `&&`/`||` return operands, not booleans.

## Closures in loops
- Deferred execution captures VARIABLES, not values: JS -> `let` in the for-header, never `var`; Python -> `lambda i=i: ...` or `functools.partial`; Go <1.22 -> `i := i`. State in one line which value each closure sees at CALL time.

## Boolean logic
- Negation mixed with `&&`/`||` (or `not` with `and`/`or`), or 3+ clauses: write the truth-table rows where the expression is TRUE (up to 4; more -> decompose into named booleans first); parenthesize every group; prefer naming the positive concept (`const isVisible = !hidden && !archived`).
- Branching on a negatively named flag (`noCache`, `disabled`, `exclude*`, `skip*`): comment what the TRUE branch does in positive words, or introduce a positively named local first.
- Mixed operator categories in one expression (bitwise+comparison, arithmetic in string concat, `??` with `||`): parenthesize every subexpression — `(flags & MASK) == 0`.
