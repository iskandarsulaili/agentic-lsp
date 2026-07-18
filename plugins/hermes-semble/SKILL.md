---
name: hermes-semble
description: "Hermes plugin that wraps Semble for hybrid BM25+semantic code search. Complements grep+read: Semble for semantic/concept search, grep for exact patterns, read for full context."
trigger: semble_search, semble_find_related, semble_stats, semble_reindex
---

# hermes-semble

A Hermes plugin wrapping [Semble](https://github.com/MinishLab/semble) — fast hybrid code search using BM25 + Model2Vec static embeddings with tree-sitter AST chunking.

## Architecture

Semble's 4-stage pipeline:

1. **Chunking** — tree-sitter splits code at AST boundaries into ~750-char chunks
2. **Dual indexing** — BM25 (lexical) + Model2Vec static embeddings (semantic)
3. **Fusion** — Reciprocal Rank Fusion (RRF) blends the two result sets
4. **Reranking** — definition boost, file coherence, path penalties, identifier stems, adaptive weighting

All runs on CPU in milliseconds. No GPU, no API keys.

## Complement with grep+read

| Search type | Tool | When |
|-------------|------|------|
| Natural language concepts | `semble_search` | "how is auth handled?" |
| Symbol lookup | `semble_search` | "where is UserService.createUser?" |
| Find related code | `semble_find_related` | "all implementations of this interface" |
| Exact pattern/regex | `grep` via terminal | "grep -rn 'TODO' src/" |
| Full file contents | `read_file` | Get complete file after Semble finds the location |

## Tools

- `semble_search(query, repo, top_k, max_snippet_lines, filter_languages, filter_paths)` — code search
- `semble_find_related(file_path, line, repo, top_k, max_snippet_lines, filter_languages, filter_paths)` — similar code
- `semble_stats(repo)` — index statistics
- `semble_reindex(repo)` — force rebuild
- `semble_status()` — engine state

## Auto-indexing

On session start, the plugin resolves the current working directory to its git repo root (walks up looking for `.git/`). If a git repo is found, a background thread builds the search index. Non-git directories are silently skipped — no timeout, no crash.

After file writes (`write_file`, `patch`, `terminal` with write commands), a debounced reindex is scheduled (10s coalescing window). Rapid writes to the same repo are batched into a single reindex.

Thread safety: 5 independent locks with consistent acquisition ordering. Index builds release the main lock during the build wait so concurrent searches on other cached repos are not blocked.

## Configuration via .env

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_SEMBLE_CACHE_SIZE` | 10 | Max cached indexes (LRU eviction) |
| `HERMES_SEMBLE_TOP_K` | 5 | Default results per search |
| `HERMES_SEMBLE_SNIPPET_LINES` | 10 | Default snippet line count |
| `HERMES_SEMBLE_INDEX_TIMEOUT` | 120 | Max seconds to wait for index build |

## Known limitations

- Cross-repo auto-indexing only triggers on session start or `/new` (no `cd` detection)
- Index builds are CPU-bound on the embedding model; large monorepos may approach the 120s timeout
- `_auto_indexed` guard set grows with each unique cwd across sessions (no eviction — ~50-100 bytes per entry, harmless)
