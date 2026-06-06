# Skill: Orchestration

Full decomposition / delegation / conflict-resolution contract for the ARS Antigravity agent team. Referenced by `/AGENTS.md` and by @orchestrator in `.agents/workflows/ars-full.md`.

---

## 1. Manager-Surface Model

Antigravity's Manager Surface spawns and observes multiple agents asynchronously. ARS uses it as follows:

### Roles

| Layer | Who | Responsibility |
|---|---|---|
| **Orchestrator** | @orchestrator (workflow files in `.agents/workflows/`) | Task decomposition, persona dispatch, checkpoint presentation, conflict resolution, early-stopping, budget transparency |
| **Specialist personas** | Defined in `.agents/agents.md` | One deliverable, one phase. Write only to the assigned artifact. |
| **State tracker** | @state-tracker | Append-only ledger of all completed stages and artifacts; enables cross-session resume |
| **Integrity gatekeeper** | @integrity-verification | Blocking gate at Stages 2.5 and 4.5 |
| **Compliance auditor** | @compliance | PRISMA-trAIce + RAISE check at integrity gates; mode-aware block semantics |

### Async Dispatch

The orchestrator dispatches specialists concurrently where the phase allows. Constrained by the independence rules:
- **Phase 1 of `academic-paper-reviewer`:** all 5 reviewers run in parallel with no cross-referencing (Iron Rule 2).
- **Phases 5a/5b of `academic-paper`:** @citation-compliance and @abstract-bilingual run in parallel.
- **Within Stage 2 of the pipeline:** @visualization can begin figure generation once the outline is complete, simultaneously with @argument-builder building claim-evidence chains; @draft-writer waits for both.

### Filesystem Handoff

Agents drop artifacts into the run's working directory for the next agent to read. This mirrors the original Material Passport handoff pattern:

```
run/
  rq_brief.md                  ← @research-question output
  methodology_blueprint.md     ← @research-architect output
  annotated_bibliography.md    ← @bibliography output
  synthesis_report.md          ← @synthesis output
  paper_draft.md               ← @draft-writer output
  integrity_report_2-5.md      ← @integrity-verification Stage 2.5 output
  review_panel/
    eic_report.md
    methodology_report.md
    domain_report.md
    perspective_report.md
    devils_advocate_report.md
  editorial_decision.md        ← @editorial-synthesizer output
  revision_roadmap.md
  paper_revised.md             ← @draft-writer revision output
  integrity_report_4-5.md      ← @integrity-verification Stage 4.5 output
  final_paper.*                ← @formatter output
  process_summary.md           ← @orchestrator Stage 6 output
```

Agents read upstream artifacts; they write only to their own assigned file. Multi-phase agents (e.g., @report-compiler at Phases 4 and 6, @devils-advocate-research at Phases 1/3/5) produce one artifact per invocation — no extension to other phases in the same call.

---

## 2. How the Orchestrator Decomposes a Request

```
User request received
        │
        ▼
1. CLASSIFY intent (routing discipline from /AGENTS.md):
   - Explicit slash command → run that workflow
   - Single clear intent → route to matching workflow directly
   - Cross-phase materials, no named skill → ask for clarification; never auto-route
   - End-to-end request → /ars-full

2. DETECT stage (for pipeline entry):
   No materials → Stage 1
   Research data → Stage 2
   Paper draft → Stage 2.5
   Verified paper → Stage 3
   Review comments → Stage 4
   Revised draft → Stage 3'
   Final draft → Stage 5

3. ESTIMATE budget (v3.2):
   Token cost estimate based on paper length + mode + cross-model toggle.
   Present to user; wait for confirmation before Stage 1.

4. DECOMPOSE into persona tasks:
   For each stage, identify:
   - Which skill to dispatch (deep-research / academic-paper / academic-paper-reviewer)
   - Which mode (socratic / full / plan / revision / re-review / etc.)
   - Which agents are active and their phase order
   - What checkpoint type follows (FULL / SLIM / MANDATORY)

5. DISPATCH asynchronously where allowed; sequential otherwise.

6. COLLECT deliverables; update @state-tracker.

7. PRESENT checkpoint; wait for user confirmation.

8. TRANSITION: pass deliverables as input to next stage.
```

---

## 3. Full ARS Pipeline Flow

```
Stage 1: deep-research (socratic|full|quick)
         ↓ [RQ Brief + Methodology + Bibliography + Synthesis]
Stage 2: academic-paper (plan|full)
         ↓ [Paper Draft]
Stage 2.5: @integrity-verification [BLOCKING] + @compliance
         ↓ [PASS — Verified Paper] / [FAIL — fix and re-verify, max 3 rounds]
Stage 3: academic-paper-reviewer (full — 5-panel)
         ↓ [Editorial Decision + Revision Roadmap]
         → Accept → skip to Stage 4.5
         → Minor|Major Revision → Stage 4
         → Reject → return to Stage 2 or end
Stage 4: academic-paper (revision)
         ↓ [Revised Draft + Response to Reviewers]
Stage 3': academic-paper-reviewer (re-review)
         ↓ [Traceability Matrix + new Decision]
         → Accept|Minor → Stage 4.5
         → Major → Stage 4' (one re-revise only)
Stage 4': academic-paper (revision) [one round — no return to review]
         ↓ [Second Revised Draft]
Stage 4.5: @integrity-verification [BLOCKING — zero-issue PASS required] + @compliance
         ↓ [PASS]
Stage 5: academic-paper (format-convert)
         MD → DOCX (Pandoc) → LaTeX → PDF (tectonic)
         ↓
Stage 6: @orchestrator — Process Summary (MD + LaTeX → PDF, bilingual)
         AI Self-Reflection Report (incl. failure-mode audit log from 2.5/4.5)
```

**Parallelization opportunity (Stage 2):** Once the outline is complete, @visualization can begin figure generation simultaneously with @argument-builder building claim-evidence chains. @draft-writer waits for both.

**Revision loop hard cap:** Stage 4 + Stage 4' = maximum 2 full revision rounds in the pipeline context.

**Early-stopping:** if delta < 3 points on the 0–100 rubric AND no P0 issues remain after a revision round, suggest stopping. User can override.

---

## 4. Checkpoint Types & Decision Dashboard

### Checkpoint Types

| Type | When used | Content |
|---|---|---|
| **FULL** | First checkpoint; after integrity boundaries; before finalization; after 4+ consecutive "continue" | Full deliverables list + Decision Dashboard + all options |
| **SLIM** | After 2+ consecutive "continue" on non-critical stages (user has said "just continue" or "fully automatic") | One-line status + explicit continue/pause prompt |
| **MANDATORY** | Integrity FAIL; Review decision (Stage 3 / 3'); Stage 5 finalization | Cannot be skipped; explicit user input required |

### Decision Dashboard (FULL checkpoints)

```
━━━ Stage [X] [Name] Complete ━━━
Metrics:
- Word count: [N] (target: [T] ±10%)     [OK/OVER/UNDER]
- References: [N] (min: [M])              [OK/LOW]
- Coverage: [N]/[T] sections drafted      [COMPLETE/PARTIAL]
- Quality indicators: [score if available]
Deliverables: [list]
Flagged: [issues, or "None"]
Ready to proceed to Stage [Y]?
  1) View full progress dashboard (say "status")
  2) Adjust mode or settings
  3) Pause pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Orchestrator Self-Check (before every FULL checkpoint)

1. Are there unverified citations in the latest output?
2. Did the latest stage uncritically accept all feedback without pushback?
3. Is latest output quality ≥ previous stage? If declining, PAUSE and flag.
4. Did the latest stage add content not requested by the user or the revision roadmap?
5. Are all required deliverables for this stage present?

If any answer raises concern, include it in the checkpoint presentation.

---

## 5. Conflict-Resolution Rules

When personas disagree, the orchestrator resolves — it **never silently averages**:

### Rule 1 — Iron Rules win
Integrity, reproducibility, citation faithfulness, and Devil's Advocate CRITICALs outrank style, brevity, and any other considerations. There is no combination of votes or reviewer consensus that overrides an Iron Rule.

### Rule 2 — Severity precedence
Higher-severity failure conditions win. Ties break by ordinal position (sprint-contract rule: F1 > F2 > F3 … by declared severity order). The orchestrator applies the severity ladder mechanically; it does not negotiate.

### Rule 3 — Independence preserved
Reviewer disagreement is reported, not collapsed. Minority findings remain visible in the Editorial Decision Package. @editorial-synthesizer builds a cross-reviewer matrix; it does not erase divergent views to create false consensus.

### Rule 4 — Document the call
Every resolved conflict records what was retained, what was downgraded, what was rejected, and why. This record enters the @state-tracker ledger and appears in the Stage 6 Process Summary.

### Worked Example: Editor vs. Methodology Reviewer

**Scenario:** @editor-in-chief (research) recommends cutting the "Analytical Framework" subsection for conciseness. @methodology-reviewer insists it must stay for reproducibility.

**Resolution:**
- Rule 1 applies: reproducibility is an Iron Rule anchor (Rule 1 — every claim is backed; methodology transparency enables claim verification). Brevity is a style preference.
- Rule 2 applies: a reproducibility failure ranks higher in severity than a word-count concern.
- **Decision:** retain the Analytical Framework subsection. The @editor-in-chief's brevity concern is downgraded to a "suggested condensation" note, not a cut instruction.
- **Record:** `{ retained: "Analytical Framework subsection", downgraded: "EIC brevity recommendation → editorial suggestion", reason: "Iron Rule 1 / reproducibility > brevity; Rule 2 severity precedence" }`

---

## 6. Graceful Degradation

When a sub-agent or MCP tool is unavailable:

1. **Declare it.** Emit a visible notice: `[TOOL UNAVAILABLE: <tool_name> — <reason>]`. Never simulate the tool's output.
2. **Degrade the function, not the integrity.** Describe what verification or action cannot be performed. Offer a manual alternative path.
3. **Do not block unnecessarily.** If the unavailable tool is advisory (e.g., @collaboration-depth, citation-existence check in a non-systematic-review context), proceed with the degraded notice in the deliverable. If the unavailable tool is blocking (e.g., integrity gate verification, Guardrail G3 citation existence), pause and ask the user how to proceed.
4. **Log the degradation.** @state-tracker records all degradations in the run ledger. Stage 6 Process Summary reports them.

**Specific degradation behaviors:**

| Tool / Agent unavailable | Behavior |
|---|---|
| MCP reference manager (Zotero/Mendeley) | Emit `[MCP UNAVAILABLE: reference-manager]`; @bibliography and @citation-compliance work from user-supplied sources only; flag all citations as `lookup_verified = false (mcp_unavailable)` |
| MCP filesystem | Emit `[MCP UNAVAILABLE: filesystem]`; deliver artifacts as inline Markdown in the conversation instead of filesystem writes; note this limitation at the checkpoint |
| MCP web-search / Scholar | Emit `[MCP UNAVAILABLE: web-search]`; Guardrail G3 cannot run; flag all citations as `[CITATION EXISTENCE UNVERIFIED — MCP UNAVAILABLE]`; this is a MANDATORY notification at Stage 2.5 / 4.5 |
| @collaboration-depth | Emit notice; omit collaboration-depth advisory block from checkpoint; pipeline continues |
| @monitoring | Omit post-pipeline monitoring plan; inform user |
| cross-model toggle (`ARS_CROSS_MODEL`) | Emit notice; proceed single-model; note in Process Summary |

**Cross-model verification is never silently simulated.** If a tool is unavailable, the agent says so explicitly and degrades rather than fabricating a verification result. This is an absolute rule with no exceptions.
