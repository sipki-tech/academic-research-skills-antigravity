---
description: Full ARS pipeline — research → write → integrity → review → revise → final integrity → finalize, orchestrated by @orchestrator with adaptive checkpoints, two-stage review, and conflict-resolution.
---

# /ars-full — Full Academic Pipeline

This workflow runs the complete ARS pipeline end-to-end via @orchestrator. It enforces all Iron Rules, blocking integrity gates, two-stage review with a max of 2 revision loops, and the adaptive checkpoint system. Use this when the user says "take my topic to a finished reviewed paper" or gives an explicit `/ars-full` command.

**Before starting:** load `skills/academic-pipeline/SKILL.md` and `/AGENTS.md`. Read the Iron Rules and Anti-Confabulation Guardrails. Read `.agents/docs/orchestration.md` for the full conflict-resolution contract.

---

## Step 0 — Intake & Stage Detection

Act as @orchestrator and perform intake:

1. **Analyze the user's input.** Determine which materials are already available:
   - No materials → entry at Stage 1 (RESEARCH)
   - Research data (RQ Brief / Bibliography / Synthesis) → Stage 2 (WRITE)
   - Paper draft → Stage 2.5 (INTEGRITY)
   - Verified paper → Stage 3 (REVIEW)
   - Review comments → Stage 4 (REVISE)
   - Revised draft → Stage 3' (RE-REVIEW)
   - Final draft for formatting → Stage 5 (FINALIZE)

2. **Budget transparency (v3.2).** Estimate token cost based on paper length, mode, and cross-model toggle. Present the estimate to the user and wait for confirmation before Stage 1 begins.

3. **Recommend modes.** Based on user's experience level and time constraints:
   - Novice / wants guidance → `socratic` (S1) + `plan` (S2) + `guided` (S3)
   - Experienced / direct → `full` (S1) + `full` (S2) + `full` (S3)
   - Time-limited → `quick` (S1) + `full` (S2) + `quick` (S3)

4. **Confirm with user.** State the entry point, recommended modes, and estimated scope. Wait for explicit go-ahead.

5. Act as @state-tracker: initialize the run ledger with entry point, modes, and timestamp.

---

## Stage 1 — RESEARCH

Act as @orchestrator and dispatch `deep-research`:

1. Load `skills/deep-research/SKILL.md`. Launch `deep-research` in the selected mode (default: `full` or `socratic`).
2. Monitor phase completion: Phase 1 (Scoping) → user confirmation → Phases 2–6.
3. Collect deliverables: RQ Brief + Methodology Blueprint + Annotated Bibliography + Synthesis Report (+ INSIGHT collection if socratic mode).
4. Act as @state-tracker: record Stage 1 complete + deliverables list.

**CHECKPOINT (FULL):**

```
━━━ Stage 1 RESEARCH Complete ━━━
Deliverables: RQ Brief / Methodology Blueprint / Annotated Bibliography / Synthesis Report
Flagged: [any DA CRITICAL or ethics issues, or "None"]
Ready to proceed to Stage 2 (WRITE)?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Inject core-principles reinforcement:
> Iron Rule 1 — every claim in the paper must be cited to sources verified in Stage 1.
> Anti-Pattern — do not carry unverified sources forward into Stage 2.

Wait for user confirmation.

---

## Stage 2 — WRITE

Act as @orchestrator and dispatch `academic-paper`:

1. Load `skills/academic-paper/SKILL.md`. Pass Stage 1 deliverables to @intake (auto-detected; @intake skips redundant phases when materials are present). Launch in `plan` or `full` mode per user choice.
2. Monitor all 8 phases (0 → 7). Enforce the v3.6.6 Generator-Evaluator contract on Phase 4/6 in `full` mode.
3. Collect deliverable: complete paper draft.
4. Act as @state-tracker: record Stage 2 complete.

**CHECKPOINT (FULL):**

```
━━━ Stage 2 WRITE Complete ━━━
Metrics:
- Word count: [N] (target: [T] ±10%)     [OK/OVER/UNDER]
- References: [N] (min: [M])              [OK/LOW]
- Coverage: [N]/[T] sections drafted      [COMPLETE/PARTIAL]
Deliverables: Paper Draft
Flagged: [any CRITICAL peer-review issues, or "None"]
Ready to proceed to Stage 2.5 (INTEGRITY)?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Inject reinforcement:
> Iron Rule 1 — zero citations can enter Stage 2.5 unverified.
> Anti-Pattern — never skip Stage 2.5, even if the draft looks clean.

Wait for user confirmation.

---

## Stage 2.5 — INTEGRITY (Blocking Gate)

Act as @orchestrator and dispatch @integrity-verification. This is a **MANDATORY** checkpoint — cannot be auto-skipped.

1. Load `skills/academic-pipeline/agents/integrity_verification_agent.md`. Run 5-phase verification: references → citation context → statistical data → originality → claims.
2. Also run @compliance (PRISMA-trAIce + RAISE, mode-aware block semantics). Load `skills/_shared/agents/compliance_agent.md`.
3. Run the **7-mode AI Research Failure Mode Checklist** (load `skills/academic-pipeline/references/ai_research_failure_modes.md`). If any mode is `SUSPECTED`, or Modes 1/3/5/6 are `INSUFFICIENT EVIDENCE`, **block the pipeline** and present the issue to the user. The user must confirm / override with reasoning / revise. There is no `--no-block` escape.
4. On FAIL: fix and re-verify; max 3 correction rounds. If still failing after 3 rounds, list unverifiable items; user decides whether to continue.
5. On PASS: act as @state-tracker and record integrity verdict.

**CHECKPOINT (MANDATORY):**

```
━━━ Stage 2.5 INTEGRITY — MANDATORY ━━━
Integrity verdict: [PASS / FAIL]
Compliance: [PRISMA-trAIce: PASS/BLOCK | RAISE: PASS/WARN]
Failure-mode checklist: [CLEAR / SUSPECTED: mode N]
Issues: [list, or "None"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait for explicit user confirmation before Stage 3.

---

## Stage 3 — REVIEW

Act as @orchestrator and dispatch `academic-paper-reviewer`:

1. Load `skills/academic-paper-reviewer/SKILL.md`. Pass verified paper. Launch in `full` mode (5-panel: EIC + R1 + R2 + R3 + Devil's Advocate).
2. Enforce Phase 0: @field-analyst configures 5 reviewers; present Reviewer Configuration to user; wait for confirmation or adjustments.
3. Enforce Phase 1 independence: all 5 reviewers run with **no cross-referencing** (Iron Rule 2). If any reviewer agent attempts to read another's draft, stop and redirect.
4. Enforce Phase 2: @editorial-synthesizer sees all reports; builds cross-reviewer matrix; resolves severity precedence; DA CRITICAL findings block "Accept" (Iron Rule 4).
5. Collect deliverables: 5 review reports + Editorial Decision + Revision Roadmap.
6. If Decision ≠ Accept: trigger Phase 2.5 Revision Coaching via @eic (Socratic dialogue). User may skip by saying "just fix it."

**CHECKPOINT (MANDATORY):**

```
━━━ Stage 3 REVIEW — MANDATORY ━━━
Decision: [Accept / Minor Revision / Major Revision / Reject]
DA CRITICAL issues: [list, or "None"]
Revision Roadmap: [N items — P0: x / P1: y / P2: z]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Decision routing:**
- Accept → proceed directly to Stage 4.5.
- Minor / Major Revision → Stage 4.
- Reject → return to Stage 2 (major restructuring) or end.

Wait for explicit user confirmation.

---

## Stage 4 — REVISE

Act as @orchestrator and dispatch `academic-paper` revision mode:

1. Load `skills/academic-paper/SKILL.md`. Pass Revision Roadmap as input to @draft-writer (revision mode). Every roadmap item must be addressed; use R&R tracking table.
2. Iron Rule 5 applies: @peer-reviewer is READ-ONLY; it does not rewrite the paper during the in-pair review cycle.
3. Collect deliverables: Revised Draft + Response to Reviewers document.
4. Act as @state-tracker: record Stage 4 complete + revision loop count (1 of max 2).

**CHECKPOINT (FULL):**

```
━━━ Stage 4 REVISE Complete ━━━
Revision loop: 1 of max 2
Items addressed: [N of M from Roadmap]
Items unresolved: [list, or "None"]
Deliverables: Revised Draft / Response to Reviewers
Ready to proceed to Stage 3' (RE-REVIEW)?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Inject reinforcement:
> Anti-Pattern — do not silently drop reviewer concerns; every item must have explicit status in the R&R table.
> Anti-Pattern — no scope creep; revision addresses roadmap items only.

Wait for user confirmation.

---

## Stage 3' — RE-REVIEW

Act as @orchestrator and dispatch `academic-paper-reviewer` re-review mode:

1. Load `skills/academic-paper-reviewer/SKILL.md`. Pass: original Revision Roadmap + Revised Draft + Response to Reviewers. Launch `re-review` mode.
2. @eic + @editorial-synthesizer verify each roadmap item against the revised manuscript. Every item is independently verified — rubber-stamp approval is an anti-pattern.
3. Collect deliverables: Traceability Matrix (Schema 11) + new Decision + Residual Issues list.

**CHECKPOINT (MANDATORY):**

```
━━━ Stage 3' RE-REVIEW — MANDATORY ━━━
New decision: [Accept / Minor / Major / Reject]
Items verified-addressed: [N of M]
Residual issues: [list, or "None"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Decision routing:**
- Accept / Minor → Stage 4.5.
- Major → Stage 4' (one re-revise only; no return to review after Stage 4').

Wait for explicit user confirmation.

---

## Stage 4' — RE-REVISE (if needed)

Act as @orchestrator and dispatch `academic-paper` revision mode (second round):

1. Pass Stage 3' Traceability Matrix + new Revision Roadmap to @draft-writer.
2. This is the final revision round. After Stage 4' completes, the pipeline proceeds directly to Stage 4.5 — **there is no return to review.**
3. Mark any remaining unresolved issues as "Acknowledged Limitations."
4. Act as @state-tracker: record Stage 4' complete + revision loop count (2 of max 2).

**Early-stopping check:** if delta < 3 points on the 0–100 rubric AND no P0 issues remain, suggest stopping revision. User can override; hard cap is 2 full revision rounds.

**CHECKPOINT (FULL):**

```
━━━ Stage 4' RE-REVISE Complete ━━━
Revision loop: 2 of max 2 (final round)
Acknowledged Limitations added: [N items]
Deliverables: Second Revised Draft
Proceeding to Stage 4.5 (FINAL INTEGRITY).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Stage 4.5 — FINAL INTEGRITY (Blocking Gate)

Act as @orchestrator and dispatch @integrity-verification. This is a **MANDATORY** checkpoint — cannot be auto-skipped.

1. Load `skills/academic-pipeline/agents/integrity_verification_agent.md`. Run 5-phase verification **from scratch independently** — do not re-check only Stage 2.5 findings. Revision may have introduced new issues.
2. Also run @compliance (PRISMA-trAIce + RAISE).
3. Also run the 7-mode AI Research Failure Mode Checklist.
4. **Stage 4.5 must achieve zero-issue PASS to proceed to Stage 5.** On FAIL: fix and re-verify (max 3 rounds).

**CHECKPOINT (MANDATORY):**

```
━━━ Stage 4.5 FINAL INTEGRITY — MANDATORY ━━━
Integrity verdict: [PASS (zero issues) / FAIL]
Compliance: [PRISMA-trAIce / RAISE]
Failure-mode checklist: [CLEAR / SUSPECTED]
Issues: [list, or "None — ZERO ISSUES CONFIRMED"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait for explicit user confirmation. Only proceed on zero-issue PASS.

---

## Stage 5 — FINALIZE

Act as @orchestrator and dispatch `academic-paper` format-convert mode:

1. Ask user which academic formatting style (APA 7.0 / Chicago / IEEE / etc.).
2. Load `skills/academic-paper/SKILL.md`. Dispatch @formatter.
3. Output sequence:
   - Step 1: Produce Markdown draft.
   - Step 2: Generate DOCX via Pandoc when available (otherwise provide conversion instructions).
   - Step 3: Ask user about LaTeX output.
   - Step 4: After user confirms content is correct, compile PDF via tectonic.
   - ⚠️ IRON RULE: PDF must be compiled from LaTeX. HTML-to-PDF is prohibited.
   - Fonts: Times New Roman (English) + Source Han Serif TC VF (Chinese) + Courier New (monospace).

**CHECKPOINT (MANDATORY):**

```
━━━ Stage 5 FINALIZE — MANDATORY ━━━
Final paper delivered: [format list]
User confirmation of content accuracy required before PDF compile.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Stage 6 — PROCESS SUMMARY

Act as @orchestrator:

1. Ask user which language version to produce (default: follows user's language setting).
2. Generate the Paper Creation Process Record in Markdown: pipeline journey, all stage decisions, all conflict resolutions, all degradations.
3. Run Collaboration Quality Evaluation: 6 dimensions, 1–100, evidence-based. No score inflation.
4. Generate AI Self-Reflection Report (includes full failure-mode audit log from Stages 2.5 and 4.5).
5. Compile to LaTeX → PDF (bilingual).
6. Act as @state-tracker: close the run ledger.

---

## Conflict Resolution

When any two personas disagree during this workflow, resolve per `.agents/docs/orchestration.md` §5:

1. Iron Rules win over style / brevity.
2. Higher severity wins; ties break by ordinal position.
3. Independence preserved — minority findings remain visible.
4. Document every resolution in the run ledger.

## Graceful Degradation

On any tool unavailability, follow `.agents/docs/orchestration.md` §6:
- Emit `[MCP UNAVAILABLE: <tool>]` before the affected phase.
- Never simulate a tool's output.
- Log all degradations for Stage 6 Process Summary.
