# Skill: MCP Integration

How the ARS Antigravity agent team uses MCP (Model Context Protocol) servers. Referenced by `/AGENTS.md` and by @bibliography, @citation-compliance, @source-verification, @draft-writer, @report-compiler, and @formatter.

> **Hard rule:** External / cross-model verification is **never silently simulated.** If a tool is unavailable, the agent emits `[MCP UNAVAILABLE: <tool>]` and degrades gracefully. Fabricating a verification result is a direct violation of Anti-Confabulation Guardrail G3 and Iron Rule 1.

---

## Setup

1. Copy `mcp_config.example.json` (repo root) to `~/.gemini/antigravity/mcp_config.json`.
2. Fill in placeholder tokens (`<YOUR_ZOTERO_API_KEY>`, `<YOUR_SERPER_API_KEY>`, etc.).
3. Restart Antigravity to pick up the configuration.
4. The workspace is opened in Antigravity; it auto-reads `AGENTS.md` and `.agents/` on every conversation.

All MCP server entries use the format defined in `mcp_config.example.json`. Do not add comments to the JSON file; guidance is in this document.

---

## Tool 1: Reference Manager MCP (Zotero / Mendeley)

**Purpose:** Pull BibTeX records, resolve citation keys, assemble the final bibliography from the user's reference library.

**Used by:** @bibliography, @citation-compliance, @formatter

**Operations:**
- `zotero_get_collection(collection_id)` — fetch all items in a Zotero collection; returns BibTeX entries.
- `zotero_search(query, fields)` — search user's library by author, title, year, DOI, or keyword.
- `zotero_resolve_key(cite_key)` — resolve a BibTeX cite key to a full record; used to verify citation-key integrity before the formatter stamps the final file.
- `mendeley_get_references(group_id)` — equivalent for Mendeley-connected libraries.

**Behavior contract:**
- @bibliography uses `zotero_search` in Phase 2 before falling back to external index searches. Corpus-first when a user library is supplied.
- @citation-compliance uses `zotero_resolve_key` in Phase 5a to set `lookup_verified = true / false`. Any entry where `lookup_verified == false` is flagged in the Citation Audit Report.
- @formatter uses `zotero_get_collection` to assemble the final bibliography in Phase 7.
- If the reference manager MCP is unavailable: all agents work from user-supplied sources only; flag all citations as `lookup_verified = false (mcp_unavailable)`; emit `[MCP UNAVAILABLE: reference-manager]` at the start of the affected phase.

**APA 7.0 requirement:** Every entry in the assembled bibliography must include a DOI when one exists. Entries without a DOI are flagged with `[NO DOI — verify manually]`.

---

## Tool 2: Filesystem MCP

**Purpose:** Write draft artifacts — `.tex`, `.md`, `.docx` — directly to the run's working directory, enabling persistent cross-session artifact management.

**Used by:** @draft-writer, @report-compiler, @formatter

**Operations:**
- `fs_write(path, content)` — write or overwrite a file at the specified path within the run directory.
- `fs_read(path)` — read a file from the run directory; used by agents to load upstream artifacts.
- `fs_list(dir)` — list files in the run directory; used by @orchestrator and @state-tracker to verify deliverables are present.
- `fs_append(path, content)` — append to an existing file; used by @state-tracker for the append-only ledger.

**Behavior contract:**
- Agents write only to their assigned artifact. @draft-writer writes `paper_draft.md`; @formatter writes `final_paper.*`. Cross-artifact writes are prohibited.
- @state-tracker uses `fs_append` exclusively — never `fs_write` (preserves append-only ledger integrity).
- If the filesystem MCP is unavailable: deliver artifacts as inline Markdown in the conversation; emit `[MCP UNAVAILABLE: filesystem]` at the start of the affected phase; note the limitation at the next checkpoint.

---

## Tool 3: Web Search / Scholar MCP

**Purpose:** Live novelty checks and citation-existence verification across arXiv, Semantic Scholar, OpenAlex, and Crossref. This tool backs **Anti-Confabulation Guardrail G3**.

**Used by:** @source-verification, @bibliography, @citation-compliance

**Operations:**
- `scholar_search(query, database)` — search academic indexes; `database` one of: `arxiv`, `semantic_scholar`, `openalex`, `crossref`, `pubmed`.
- `scholar_lookup_doi(doi)` — resolve a DOI to a full metadata record; returns title, authors, year, abstract, venue, citation count.
- `scholar_lookup_arxiv(arxiv_id)` — resolve an arXiv ID.
- `web_search(query, n_results)` — general web search (Serper or equivalent); used for predatory journal screening, fact-checking, and gray-literature retrieval.
- `crossref_check(doi)` — verify DOI existence and metadata against Crossref API; returns `found: true/false`.

**Behavior contract (Guardrail G3):**
- Every ID-keyed citation (DOI, arXiv ID) must be verified via `scholar_lookup_doi` or `scholar_lookup_arxiv` before the citation can be marked as confirmed.
- A citation that no index matches is flagged: `[UNVERIFIED CITATION — no index match for <id>]`. It is never presented as confirmed.
- @source-verification uses `scholar_search` + `web_search` for evidence-hierarchy grading and predatory journal screening in Phase 2.
- @bibliography uses `scholar_search` for systematic search (Phase 2) and `crossref_check` for existence verification.
- @citation-compliance uses `scholar_lookup_doi` and `crossref_check` in Phase 5a; sets `lookup_verified = true` only on positive match.
- If the web-search / Scholar MCP is unavailable: Guardrail G3 cannot run; all citations are flagged `[CITATION EXISTENCE UNVERIFIED — MCP UNAVAILABLE]`; emit `[MCP UNAVAILABLE: web-search]` at the top of the affected phase; this is a MANDATORY disclosure at Stages 2.5 and 4.5.

---

## Degradation Summary

| Tool | If unavailable | Severity |
|---|---|---|
| Reference manager (Zotero/Mendeley) | Work from user-supplied sources; flag `lookup_verified = false (mcp_unavailable)` | Advisory — pipeline continues with notice |
| Filesystem MCP | Deliver artifacts inline in conversation | Advisory — pipeline continues with notice |
| Web search / Scholar MCP | G3 cannot run; all citations flagged `[CITATION EXISTENCE UNVERIFIED]` | MANDATORY disclosure at 2.5 / 4.5; pipeline continues with user aware |

No degradation is silent. Every tool unavailability is announced before the affected phase begins and recorded by @state-tracker.

---

## Configuration Reference

See `mcp_config.example.json` for the complete server configuration template. The live config lives at `~/.gemini/antigravity/mcp_config.json` (gitignored — never commit credentials).

The JSON structure follows the Claude Desktop / Antigravity `{ "mcpServers": { ... } }` schema with `command` + `args` + optional `env` per server.

---

## Security Notes

- Tokens in `mcp_config.json` grant access to your reference library and web-search quota. Never commit the live config to version control.
- The `.gitignore` at repo root excludes `~/.gemini/` and any `*_config.json` files outside the example.
- MCP tool calls are logged by @state-tracker alongside pipeline artifacts for reproducibility auditing.
