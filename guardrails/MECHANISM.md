<!-- guardrails v1 | mechanism/premise-verification playbook. macOS/zsh + Rails/Laravel. Mirrored at ~/IOU/IOU/Claude Code/guardrails/MECHANISM.md -->
You are here because you are about to: conclude existing code is wrong / dead / unnecessary; override a stated rationale (a code comment, the author's intent, a ticket, a vendor/framework doc); build a removal, migration, or multi-step plan on a claim about how an external system/API/framework behaves; or call a primary-source claim wrong or "fiction."

Reading code tells you what it does, not why it exists or whether your model of the mechanism is right. The expensive failures come from confidently building on a misidentified mechanism — pattern-matching "cache/queue/retry/auth/webhook" to the feature you happen to know, then interpreting every signal (including disconfirming ones) through that wrong frame.

Echo protocol: for each item write one line — `M<n>: PASS — <source/quote>` | `M<n>: FAIL — <what's missing>` | `M<n>: N/A — <reason>`. Any conclusion that overrides a primary source, or any plan built on an external-system claim, without a PASS on M1 and M2 is not allowed to proceed — label it `MECHANISM-UNVERIFIED` and treat the plan as a hypothesis, not a decision.

- M1. Name the exact mechanism/feature you believe is in play, in one line, and verify it against ITS OWN authoritative doc — not an adjacent feature you pattern-matched to. Quote the doc. Reading the wrong doc thoroughly is still wrong (e.g. reading prompt-caching docs when the feature is structured-output grammar caching).
- M2. Before calling a primary-source claim wrong/outdated/"fiction" — a code comment, the author's stated intent, a ticket, a vendor doc — cite the authoritative source that CONTRADICTS it. Disconfirmation needs a source, same as confirmation. A claim you can't explain within your current frame is a signal the frame is wrong; widen the search before you dismiss it.
- M3. Before concluding deliberate code is dead/broken/removable, reconstruct WHY it was built (author via git blame, the commit, the comment, the ticket). For any non-obvious removal, ask the author. Someone chose to write it; assume a reason until you've found or ruled it out.
- M4. Scale verification to blast radius. The bigger the thing you're about to build on a premise — a removal, a migration, a multi-step investigation, a PR, a stakeholder claim — the more that premise needs an independent second source or the domain expert BEFORE you proceed. Never stack an edifice on one unverified foundation.
- M5. State the single load-bearing assumption in one sentence: "This whole plan is correct only if ___." If that sentence is wrong, does everything collapse? If yes, that sentence is what you verify first — not the details built on top of it.

--- reference ---

## The case this prevents (2026-08, DS-1684 / Nucleus)
`LoanApplication::WarmParserCacheJob` had a comment: "keep the schema cache warm… cached for 24 hours." I pattern-matched "cache" to **prompt caching**, read the prompt-caching docs (5-min/1h TTL, 4096-token floor), and concluded the comment's "24h" was fiction and the job was dead code — then built a delete + investigation + cost-spike + PR + Jira moves on it. The author (Andrew) corrected it: the job warms the **structured-output grammar cache**, which Anthropic's structured-outputs docs document as "cached for 24 hours from last use," with a compile-latency hit on a cold schema. The comment was accurate; I never read the doc for the actual mechanism. One M1 check (verify the feature the comment named against its own doc) would have caught it before any of the edifice was built.

## Disconfirming evidence is the signal, not the noise
When a primary source contradicts your working model (the comment said 24h; my frame said 5min), the model is the thing on trial — not the source. "This must be wrong" about someone's deliberate artifact is a hypothesis that requires the same burden of proof as any other claim. Cite what disproves it, or treat your frame as unconfirmed.

## Cheapest check first
Verifying the mechanism is usually one doc fetch or one question to the author — seconds to minutes. Building and then unwinding a wrong plan (a PR, a spike, a Jira trail, a teammate's review time) costs hours and credibility. Do M1/M2 before the plan, not after someone corrects it.
