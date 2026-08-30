# rails-agents — Review Lessons (append-only)

Rules distilled from code reviews/audits. **High-signal only** — each entry changes a decision; this is not a dumping ground (bloated reference degrades decisions). Consult before implementing; a rule here is **not optional**.

## Controllers / Active Record

- **Eager-load Active Storage attachments in index/list actions that render the attachment.** Use `Model.with_attached_<name>` (or `includes(<name>_attachment: :blob)`). A bare `Model.all` / `.order(...)` that then renders an attachment is an N+1 (one query per row). — *Depot A1 audit, 2026-08-30: index used `Product.order(:title)` with no `with_attached_image`.*
- **Strong params: prefer Rails 8 `params.expect(model: [...])`** over `params.require(:model).permit(...)`. `expect` rejects tampered or malformed param structures instead of silently permitting. — *Depot A1 audit, 2026-08-30.*

## Mechanical gates (adopt in the project, so these become failing checks not memos)

- Add **`bullet`** (dev + test groups); set `Bullet.raise = true` in the test environment so an N+1 **fails the suite**. A red test beats a remembered rule.
- Enable **rubocop-rails** and keep idiom cops on (e.g. `Rails/StrongParametersExpect`) so lint enforces the rules above.

---
*How this file works: an audit finds a repeated miss → add a tight rule here (+ a mechanical gate where possible) → agents read it and stop repeating → the reviewer/auditor catches less over time. If a lesson doesn't take (the miss recurs), that's the signal to escalate from this prose rule to a hard mechanical gate.*
</content>
