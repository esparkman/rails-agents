<!-- guardrails v1 | runtime-verification playbook. macOS/zsh + Rails/Laravel. Mirrored at ~/IOU/IOU/Claude Code/guardrails/RUNTIME.md -->
You are here because you are about to describe a code path as live/running, blame it for a production symptom, size its cost/impact/priority, or scope work around it as a current problem.

Reading code tells you what CAN run, not what DOES. Liveness, volume, and cost are runtime facts — confirm them before you assert them. A dormant path (flag off, route disabled, job unscheduled, integration not turned on) has zero impact today no matter how the code reads.

Echo protocol: for each item write one line — `R<n>: PASS — <source> -> <quoted figure>` | `R<n>: FAIL — <what's missing>` | `R<n>: N/A — <reason>`. Any liveness / cost / priority claim without a PASS line beside it in THIS turn is not allowed to ship: label it `RUNTIME-UNVERIFIED` and treat volume as unknown.

- R1. Liveness: before calling a path live/active/current, quote runtime evidence from this turn that it executes in the target env — an APM throughput number, a log line, a job-run count, a request count. Zero or absent evidence -> the path is `RUNTIME-UNVERIFIED`. Code that exists is not proof it runs.
- R2. Attribution: before pinning a prod symptom (cost spike, error, latency) on a specific path, confirm that path carries the traffic — not a sibling with the same shape. Name the exact action/endpoint/job you checked and its figure.
- R3. Sizing: before quoting a cost/impact/frequency, cite the number's source (usage/cost dashboard, APM, a COUNT query) and its window. No source -> state it as an estimate bounded by a stated ceiling, never as fact.
- R4. Split the two claims: write "Exists in code: <file:line>" and "Runs in prod: <figure + window>" as SEPARATE lines. A cost/priority claim inherits the weaker of the two. "0 traffic" is a valid, in-voice answer for the second line.
- R5. Source of truth (this shop): AppSignal -> Performance -> Actions throughput per action (nucleus prod site `682b380382ce018e9ba7e408`); the org usage/cost dashboard (`claude-dash`) for Anthropic spend; `Delayed::Job` / GoodJob tables for job-run counts. Prefer these over inference from the code.

--- reference ---

## The recurring failure this prevents
Tracing a code path and asserting it as a live behavior/problem without confirming execution. Instances (Nucleus, 2026-08): bug-location premise asserted from code before tracing evidence; "warm-cache job erroring in prod" claimed from code before the AppSignal record confirmed it; the document-AI "double-processing" spike scoped around an email-ingestion path that carried ZERO prod traffic (classify = 0, ISO-parse = 0 over 30 days) while everything actually ran through SmartSubmit (6,834). Code shows structure; runtime shows reality.

## Zero is a finding
0 throughput / 0 occurrences over a real window is a positive result: the path is dormant. Report it as dormant — do not treat it as a live problem, and do not "fix" or optimize a cost that isn't being incurred. The revisit trigger is "when the path goes live," not "now."

## Cheapest check first
Most liveness/volume questions are answered by one APM throughput lookup or one dashboard read — seconds, no DB access. Do that BEFORE writing the analysis, not after someone corrects the premise.
