# 🗺️ Roadmap — Code Assembler Pro

Four themes, in priority order. Everything here either protects the user from
a demonstrated failure mode, or completes the core loop:

```
Code ↔ [code-assembler] ↔ Markdown ↔ [LLM]
```

Anything that doesn't serve that loop is in [Non-Goals](#-non-goals).

---

## 1. 🛡️ Make the round-trip trustworthy

**Why this is first:** `--rebuild` writes over real source files. Today it does
so blindly — no integrity check, no preview, no way to tell a faithful
reconstruction from a silently mangled one.

This is not theoretical. Running v4.5.2 on a real 136-file snapshot silently
corrupted 4 files (a fence-parsing bug, fixed in 4.6.0). Nothing in the tool
noticed: it reported `[OK] 136 file(s) reconstructed`. The corruption was only
found by compiling every output file by hand. A user applying an AI refactor
would have committed four broken files and trusted the green message.

Until rebuild is verifiable, every other feature sits on sand.

### 1.1 Integrity manifest
Store a content hash per file in the `CODE_ASSEMBLER_METADATA` block at assembly
time. On rebuild, hash each reconstructed file and report any mismatch.

- Catches parser bugs, truncated LLM responses, and copy-paste damage **automatically**.
- Note the semantics: a mismatch after an *intentional* AI edit is expected —
  the signal is "this file changed", which is exactly what the user wants
  surfaced before it lands on disk. Pair with 1.3.
- Backward compatible: snapshots without hashes rebuild as they do today.

### 1.2 `--verify` self-check
```bash
code-assembler --verify snapshot.md
```
Assemble → rebuild in memory → compare against the source tree. Reports any file
that doesn't survive the round trip byte-for-byte.

Highest value-to-effort ratio on this list: it turns the entire class of bugs
found in 4.6.0/4.6.1 into a one-command check, for any project, without needing
to think of the edge case first.

### 1.3 Rebuild preview & guardrails
- `--rebuild --diff`: show a unified diff of what would change, before writing.
- Refuse (unless `--force`) to overwrite a file when the incoming version is
  drastically shorter — the signature of a truncated LLM response.
- Existing `--dry-run` shows *which* files would be written; this shows *what
  would happen to them*.

---

## 2. 🔒 Secret scanning (`--scan-secrets`)

**The tool's single worst-case outcome:** a user assembles a project, pastes it
into a cloud LLM, and ships an AWS key, a `.env`, or a private token to a third
party. Irreversible, and entirely the tool's fault for making the paste so easy.

- Regex detection for common credential formats, plus a configurable allow-list.
- Default to **excluding** the offending file with a loud warning; `--fail-on-secret`
  for CI.
- Should also run on `--clip`, which is the fastest path to a leak.

Carried over from the previous roadmap unchanged, and still the right call — it
just never shipped. Worth committing to a release this time.

---

## 3. 🎯 Token budgeting (`--max-tokens`)

The core promise is "your codebase, in the context window". `--compress` and
`--since` are two partial answers; this is the general one.

```bash
code-assembler . --ext py --max-tokens 100000
```

Select files to fit a stated budget, with an explicit strategy rather than blind
truncation:
- `recent` — most recently modified first
- `entry` — entry points and their imports first
- `small` — maximise file count

Report what was left out and why, so the omission is visible rather than silent.
Composes with `--compress`: compress first, then select.

---

## 4. 🤖 Native agent integration (MCP server / Claude Skill)

Today an agent can *read* a generated snapshot but has no idea the tool exists.
The 4.6.0 frontmatter (`rebuild:` command, `agents_doc:` URL) closed the
discovery gap; this closes the execution gap.

Expose assemble / delta / rebuild as MCP tools so Claude Code, Cursor, and
friends can run the full loop natively — read the codebase, propose changes,
apply them through `--rebuild` — without the user shuttling files by hand.

Depends on theme 1: an agent applying rebuilds unattended makes integrity
verification a prerequisite, not a nice-to-have.

---

## 🚫 Non-Goals

Stated explicitly, because each is a reasonable-sounding idea that would dilute
the tool:

| Not doing | Why |
|---|---|
| Knowledge graph / import graph | That's [Graphify](https://github.com/Graphify-Labs/graphify)'s fight, with far more resources. This tool bets on *full context*, not structured retrieval — a different and, for corpora that fit the window, often better answer. |
| Vector store / RAG / embeddings | Same reason. Retrieval only pays once the corpus can't fit; below that it adds failure modes for nothing. |
| Multi-file OKF bundle | The single portable file *is* the product. Frontmatter borrows OKF's conventions; the bundle structure would defeat the purpose. |
| Web UI (viewer + chat) | A separate product, not a feature of a CLI tool. |
| Watch mode | `--since` already covers incremental workflows; the extra process is complexity for a rare case. |
| Named profiles | `--config file.json` already does this. A second lookup mechanism is not a feature. |
| Dependency summary | Manifests (`pyproject.toml`, `package.json`) are already included when their extension is selected — the LLM reads them directly. |

---

## 🔧 Maintenance (not roadmap items)

Real, but small enough to land in any patch release rather than gate one:

- **Compression polish** — `pass` → `...` normalisation, decorator edge cases
  (`@property`, `@dataclass`, stacked decorators), `TypedDict` / `Protocol` /
  `match`-`case`.
- **Compression ratio in summary** — `Original: X → Compressed: Y (Z% reduction)`.
  Without it, there's no feedback that `--compress` did anything.
- **`validate_config_keys()`** — a typo like `"extentions"` currently surfaces as
  a cryptic `TypeError`. More pressing since the README now ships a JSON template
  people will copy by hand.
- **tree-sitter gaps** — Kotlin, Swift, and Scala aren't reliably published for the
  0.21 API. Consider a `compress-compat` extra wrapping the monolithic 0.20 package.

---

## 🐛 Known issues

- **Metadata paths are relative to the CWD, not the assembled root.** Running from
  a different directory than the analysed tree produces manifest entries like
  `"../../../../AppData/Local/Temp/tmp.../db/config.py"`. Harmless today (full and
  delta runs agree with each other), but fragile, and it makes snapshots
  non-portable across machines.

---

## ✅ Shipped

| Version | Feature |
|---------|---------|
| **v4.4.0** | Rebuild Mode (`--rebuild`), Delta Mode (`--since`), Clipboard (`--clip`) |
| **v4.5.x** | Code compression (`--compress`), per-language tree-sitter extras, robustness pass |
| **v4.6.0** | YAML frontmatter (agent-discoverable rebuild instructions), README-context fence fix, docs consolidation |
| **v4.6.1** | Metadata/truncation false-positive fixes (found by running the tool on itself) |

---

## 🧪 Release gate

**Run code-assembler on code-assembler before every release**, and rebuild the
result.

One such run on 4.6.0 surfaced two real bugs that 106 passing tests had not:
a self-referential metadata match and four false truncation warnings. Both only
appear when the analysed codebase documents code-assembler's own markers — which
no synthetic fixture had thought to do. Once `--verify` (1.2) exists, this becomes
a single command.

---
*Last updated: August 2026 — v4.6.1*