<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/iskandarsulaili/agentic-lsp/main/assets/logo-dark.svg">
    <img src="https://raw.githubusercontent.com/iskandarsulaili/agentic-lsp/main/assets/logo-light.svg" alt="agentic-lsp" width="480">
  </picture>
</p>

<p align="center">
  <b>Ultimate vibe coding plugins for Hermes AI agent.</b>
</p>

<p align="center">
  Effect-ts functional architecture • LSP code intelligence • Semble semantic code search • Graphify knowledge graph • 23 tools • Zero external deps
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-the-vibe-coding-stack">The Stack</a> •
  <a href="#-comparison">Comparison</a>
</p>

<p align="center">
  <a href="https://github.com/iskandarsulaili/agentic-lsp"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-agentic--lsp-2ea44f?style=flat-square&logo=github"></a>
  <a href="https://github.com/iskandarsulaili/agentic-lsp/blob/main/LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square"></a>
  <a href="#"><img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python"></a>
  <a href="#"><img alt="Zero deps" src="https://img.shields.io/badge/dependencies-zero-success?style=flat-square"></a>
  <a href="https://github.com/sponsors/iskandarsulaili"><img alt="Sponsor" src="https://img.shields.io/badge/sponsor-30363D?style=flat-square&logo=GitHub-Sponsors&logoColor=EA4AAA"></a>
</p>

---

**agentic-lsp** is the ultimate vibe coding stack for [Hermes AI agent](https://hermes-agent.nousresearch.com). Four plugins, 23 tools, zero external dependencies. Everything you need to turn Hermes into a self-correcting, codebase-aware AI coding agent:

**1. Effect-ts functional architecture** — Typed errors, DI container with cycle detection, structured concurrency via Scope + Fiber. Every operation is composable, typed, and error-tracked. No silent failures.

**2. LSP code intelligence** — Real-time diagnostics after every edit, completions, hover, go-to-definition, auto-fix. The agent self-corrects before shipping broken code. 14 languages. Cross-repo fallback.

**3. Semble semantic code search** — Hybrid BM25 + semantic embeddings. Find code by what it *does*, not just by what characters it contains. ~98% fewer tokens than grep+read.

**4. Graphify knowledge graph** — Dependency graphs, call chains, subsystem detection, shortest paths between concepts. Understand how everything connects.

All four plugins are **pure Python, zero external dependencies** (stdlib only). They install in seconds and survive Hermes updates because they live in `~/.hermes/plugins/`, not in Hermes's core. All timeouts, limits, and cache sizes are configurable via `.env` — no hardcoded settings.

## ✨ Features

### Effect-ts Architecture — in Python

| What OpenCode has | What agentic-lsp provides |
|-------------------|--------------------------|
| Effect-ts `Effect<A, E, R>` | `Effect[T, E]` — compose, map, flatMap, catch, retry, withTimeout |
| Effect-ts `Schema.TaggedError` | `TypedError` — tagged errors with `_tag` discriminator, JSON round-trip |
| Effect-ts `Layer` (DI) | `ServiceContainer` — register services with deps, resolve graphs, detect cycles at register time |
| Effect-ts `Scope` + `Fiber` | `Scope` + `Fiber` — async `fork`, `join`, `interrupt`, auto-cancel on scope exit |
| Effect-ts `Logger` | Python `logging` — all configurable via env |
| TypeScript runtime | Python 3.11+ — no transpilation, no bundling |

4 Hermes tools:

| Tool | What it does |
|------|-------------|
| `effect_run` | Execute a chain of operations as a typed effect. Each step validated, errors tracked by type, stops on first typed failure. |
| `effect_scope` | Fork concurrent fibers, join results, cancel, or list running fibers. Auto-cancels on scope exit. |
| `effect_service` | Register services with explicit dependencies, resolve them, or inspect the graph. Cycle detection at register time. |
| `effect_inspect` | Inspect the service graph, tool registry, and known error types. |

### LSP Code Intelligence — 14 Languages

| Tool | What it does |
|------|-------------|
| `lsp_verify` | Opens file, gets diagnostics, returns pass/fail. Agent self-corrects before shipping. |
| `lsp_completions` | Method names, imports, documentation |
| `lsp_hover` | Type signatures, documentation for any symbol |
| `lsp_definition` | File + line number, with cross-repo fallback |
| `lsp_auto_fix` | Quick-fix suggestions (like the IDE lightbulb) |
| `lsp_servers` | List available servers and running clients |
| `lsp_diagnostics` | Get diagnostics for a specific file |

**Cross-repo resolution** — when `goto_definition` can't find a symbol in the current repo, it automatically queries all other running LSP servers of the same language. Self-adapting: discovers related repos organically as you open files. No config needed.

**14 languages** — C, C++, Python, TypeScript, JavaScript, JSON, YAML, Rust, Go, HTML, CSS, Bash, Dockerfile, SQL.

7 Hermes tools + `/lsp` slash command.

### Semble Semantic Code Search

Search your whole codebase using natural language or symbol names. Complements grep+read:

| Search type | Tool | Example |
|-------------|------|---------|
| Concept/semantic | `semble_search` | "how is authentication handled?" |
| Symbol lookup | `semble_search` | "where is UserService.createUser?" |
| Find related code | `semble_find_related` | "all implementations of IRepository" |
| Exact pattern | `grep` (terminal) | "grep -rn 'TODO' src/" |
| Full context | `read_file` | After Semble finds the right file |

5 Hermes tools + `/semble` slash command.

### Graphify Knowledge Graph

Structural code understanding via dependency graphs. Complements LSP (per-file depth) and Semble (semantic search) with structural relationships.

| Query type | Tool | Example |
|-------------|------|---------|
| Concept relationships | `graphify_query` | "how does auth connect to the database?" |
| Shortest path | `graphify_path` | "UserService → DatabasePool" |
| Explain a symbol | `graphify_explain` | "what does RateLimiter connect to?" |
| Most connected nodes | `graphify_god_nodes` | "what are the core abstractions?" |
| Graph statistics | `graphify_stats` | node/edge/community counts |
| Find nodes | `graphify_find` | "find LSPClient in the graph" |
| Subsystem contents | `graphify_community` | "what's in community 0?" |

7 Hermes tools + `/graphify` slash command.

### What OpenCode Doesn't Have

| Feature | agentic-lsp | OpenCode |
|---------|-------------|----------|
| **Idle client eviction** | ✓ — clients auto-evicted after TTL | ✗ — clients live forever |
| **Server availability cache** | ✓ — caches binary checks for 60s | ✗ — checks every time |
| **Project root cache** | ✓ — caches root discovery | ✗ — re-discovers every file |
| **Thread safety** | ✓ — every shared state has a lock | ✗ — single-threaded only |
| **Timeouts on every I/O** | ✓ — reads, writes, stops all have configurable timeouts | Partial |
| **.env configuration** | ✓ — 25+ env vars for all timeouts/limits | ✗ — hardcoded |
| **Cross-repo LSP fallback** | ✓ — queries other repos on miss | ✗ — single workspace only |
| **Survives agent updates** | ✓ — lives in user plugin dir | ✗ — bundled in monorepo |
| **Agent-agnostic** | ✓ — works with Hermes, OpenCode, Cline, any plugin system | ✗ — OpenCode only |

## ⚡ Quick Start

### Prerequisites

- **Hermes Agent** — plugins auto-discover from `~/.hermes/plugins/`
- **Python 3.11+** — no other dependencies
- **Language servers** — install the ones you need (see [Supported Languages](#-supported-languages))

### Install

```bash
git clone https://github.com/iskandarsulaili/agentic-lsp.git /tmp/agentic-lsp

# Install all 4 plugins
cp -r /tmp/agentic-lsp/plugins/hermes-lsp ~/.hermes/plugins/hermes-lsp
cp -r /tmp/agentic-lsp/plugins/hermes-effect-engine ~/.hermes/plugins/hermes-effect-engine
cp -r /tmp/agentic-lsp/plugins/hermes-semble ~/.hermes/plugins/hermes-semble
cp -r /tmp/agentic-lsp/plugins/hermes-graphify ~/.hermes/plugins/hermes-graphify

# Clean up
rm -rf /tmp/agentic-lsp
```

> **Important:** Each plugin must be a direct subdirectory of `~/.hermes/plugins/`. Cloning the whole repo into `~/.hermes/plugins/agentic-lsp/` will NOT work.

### Enable Plugins

```bash
hermes config set plugins.enabled '["hermes-lsp","hermes-effect-engine","hermes-semble","hermes-graphify"]'
```

### Install Optional Dependencies

```bash
# For Semble semantic code search
pip install semble

# For Graphify knowledge graph
pip install graphifyy
```

### Restart & Verify

```bash
# In Hermes:
/lsp servers
/effect
/semble status
/graphify status
```

## 🎯 The Vibe Coding Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hermes AI Agent Loop                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│   │  hermes-lsp     │   │ hermes-semble│   │hermes-graphify   │  │
│   │  (per-file      │   │ (semantic    │   │ (structural      │  │
│   │   depth)        │   │  search)     │   │  understanding)  │  │
│   │                 │   │              │   │                  │  │
│   │ lsp_verify      │   │ semble_search│   │ graphify_query   │  │
│   │ lsp_completions │   │ find_related │   │ graphify_path    │  │
│   │ lsp_hover       │   │ stats        │   │ graphify_explain │  │
│   │ lsp_definition  │   │ reindex      │   │ god_nodes        │  │
│   │ lsp_auto_fix    │   │ status       │   │ stats            │  │
│   │ lsp_servers     │   │              │   │ find             │  │
│   │ lsp_diagnostics │   │              │   │ community        │  │
│   └─────────────────┘   └──────────────┘   └──────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │  hermes-effect-engine (functional core for all tools)    │   │
│   │  effect_run • effect_scope • effect_service • inspect   │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Workflow:                                                      │
│   1. Semble → find the right file/concept semantically           │
│   2. Graphify → explain how it connects to everything else      │
│   3. LSP → verify correctness after every edit                  │
│   4. Effect engine → compose operations with typed error safety │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Self-Correcting Loop

```
1. Agent edits file.py
2. Agent calls lsp_verify(filepath="file.py", content="<new content>")
3. LSP server returns diagnostics (errors, warnings)
4. If errors found:
   a. Agent calls lsp_auto_fix(filepath="file.py")
   b. Agent applies suggested fixes
   c. Agent re-verifies
5. Only when passed=true does the agent proceed
```

This eliminates the most common failure mode of AI coding agents: **silently shipping broken code**.

## 🗺️ Supported Languages

| Language | Server | Install |
|----------|--------|---------|
| Python | Pyright / basedpyright | `pip install pyright` |
| TypeScript / JavaScript | typescript-language-server | `npm i -g typescript-language-server` |
| Rust | rust-analyzer | `rustup component add rust-analyzer` |
| Go | gopls | `go install golang.org/x/tools/gopls@latest` |
| C / C++ | clangd | `apt install clangd` / `brew install llvm` |
| JSON | vscode-json-languageserver | `npm i -g vscode-json-languageserver` |
| YAML | yaml-language-server | `npm i -g yaml-language-server` |
| HTML | vscode-html-languageserver | `npm i -g vscode-html-languageserver` |
| CSS | vscode-css-languageserver | `npm i -g vscode-css-languageserver` |
| Bash | bash-language-server | `npm i -g bash-language-server` |
| Dockerfile | dockerfile-language-server-nodejs | `npm i -g dockerfile-language-server-nodejs` |
| SQL | sql-language-server | `npm i -g sql-language-server` |

## 🏗️ Architecture

```
~/.hermes/plugins/
├── hermes-effect-engine/     # Effect-ts-style functional core
│   ├── plugin.yaml           # Hermes plugin manifest
│   └── __init__.py           # TypedError, ServiceContainer, Scope, Fiber, Effect, Schema, ToolDef
│                              # Thread-safe, .env-configured, 0 external deps
│
├── hermes-lsp/               # LSP code intelligence (14 languages)
│   ├── plugin.yaml           # Hermes plugin manifest
│   └── __init__.py           # LSPManager, LSPClient, JSON-RPC, cross-repo fallback
│                              # Thread-safe, .env-configured, 0 external deps
│
├── hermes-semble/            # Semantic code search
│   ├── plugin.yaml           # Hermes plugin manifest
│   └── __init__.py           # _SembleEngine, BM25+semantic hybrid search
│                              # Thread-safe, .env-configured
│
└── hermes-graphify/          # Knowledge graph
    ├── plugin.yaml           # Hermes plugin manifest
    └── __init__.py           # _GraphEngine, dependency graph queries
                              # Thread-safe, .env-configured
```

### Thread Safety Architecture

```
Main Thread (Hermes agent loop)          Reader Thread (per LSP client)
─────────────────────────────            ─────────────────────────────
send_request() ──── stdin ──────►        read_loop() ──── stdout ◄────
  ↑under _lock                             │
  │                                        ├── _read_line_timeout()
  │                                        └── _handle_message()
  │                                              │
  │                                       _diagnostics ←── under _diag_lock
  │                                              │
  ◄──── pending_requests[id].event.set() ─────────┘
       under _lock

Manager (singleton)
  _clients ─── under _lock
  _known_roots ─── under _known_roots_lock
  _cross_repo_cache ─── under _cross_repo_cache_lock
```

All shared state is protected by dedicated locks. No lock ordering deadlocks — the manager never holds a client lock while acquiring another, and vice versa.

### .env Configuration

Every timeout, limit, and interval is configurable via environment variables with sensible defaults:

```bash
# LSP timeouts
HERMES_LSP_REQUEST_TIMEOUT=15           # Per-request timeout (seconds)
HERMES_LSP_HEADER_TIMEOUT=5             # Header read timeout
HERMES_LSP_CONTENT_TIMEOUT=30           # Content read timeout
HERMES_LSP_DIAGNOSTICS_TIMEOUT=5        # Max wait for diagnostics after edit
HERMES_LSP_STOP_TIMEOUT=5               # Max wait for server process to stop

# LSP limits
HERMES_LSP_MAX_DIAGNOSTICS=20           # Max errors returned
HERMES_LSP_MAX_WARNINGS=20              # Max warnings returned
HERMES_LSP_MAX_COMPLETIONS=30           # Max completions returned
HERMES_LSP_MAX_CONTENT_LENGTH=10485760  # Max message body (10MB)

# LSP lifecycle
HERMES_LSP_CLIENT_TTL=300               # Idle client eviction (seconds)
HERMES_LSP_EVICTION_INTERVAL=60         # Eviction sweep interval

# Cache TTLs
HERMES_LSP_SERVER_CACHE_TTL=60          # Server availability cache
HERMES_LSP_CROSS_REPO_CACHE_TTL=30     # Cross-repo lookup cache
HERMES_LSP_KNOWN_ROOTS_MAX=50           # Max tracked project roots
HERMES_LSP_CROSS_REPO_CACHE_MAX=100     # Max cross-repo cache entries

# Effect engine
HERMES_EFFECT_RETRY_MAX_ATTEMPTS=3      # Effect retry attempts
HERMES_EFFECT_RETRY_DELAY_MS=1000       # Delay between retries
HERMES_EFFECT_RETRY_MAX_DELAY_MS=30000  # Max exponential backoff
HERMES_EFFECT_DEFAULT_TIMEOUT_MS=30000  # Effect run timeout
HERMES_EFFECT_SHELL_TIMEOUT=30          # Shell command timeout
HERMES_EFFECT_FIBER_JOIN_TIMEOUT=30     # Fiber join timeout
HERMES_EFFECT_POOL_SIZE=4               # Thread pool size for Effect.with_timeout

# Semble
HERMES_SEMBLE_CACHE_SIZE=10             # Max cached indexes (LRU eviction)
HERMES_SEMBLE_TOP_K=5                   # Default results per search
HERMES_SEMBLE_SNIPPET_LINES=10          # Default snippet line count
HERMES_SEMBLE_INDEX_TIMEOUT=120.0       # Max seconds to wait for indexing

# Graphify
HERMES_GRAPHIFY_GRAPH=""                # Default graph path
HERMES_GRAPHIFY_CACHE_SIZE=10          # Max cached graphs (LRU eviction)
HERMES_GRAPHIFY_QUERY_DEPTH=3           # Default traversal depth
HERMES_GRAPHIFY_TOKEN_BUDGET=2000       # Default output token budget
HERMES_GRAPHIFY_MAX_FILE_SIZE=104857600 # Max graph file size (100MB)
```

## 🔄 Comparison

| Feature | agentic-lsp | OpenCode | Claude Code |
|---------|-------------|----------|-------------|
| **Effect-ts typed errors** | ✓ (Python) | ✓ (TypeScript) | ✗ |
| **Effect-ts DI container** | ✓ | ✓ (Layer) | ✗ |
| **Effect-ts Scope + Fiber** | ✓ | ✓ | ✗ |
| **LSP diagnostics** | ✓ (7 tools) | ✓ | ✓ |
| **LSP completions** | ✓ | ✓ | ✓ |
| **LSP go-to-definition** | ✓ + cross-repo | ✓ (single workspace) | ✓ |
| **LSP auto-fix** | ✓ | ✗ | ✗ |
| **Cross-repo resolution** | ✓ (self-adapting) | ✗ | ✗ |
| **Idle client eviction** | ✓ | ✗ | ✗ |
| **Thread safety** | ✓ (dedicated locks) | ✗ (single-threaded) | N/A |
| **Timeouts on all I/O** | ✓ (configurable) | Partial | ✓ |
| **.env configuration** | ✓ (25+ vars) | ✗ (hardcoded) | ✗ |
| **Zero external deps** | ✓ (stdlib only) | ✗ (Effect-ts, AI SDK) | ✗ (bundled) |
| **Agent-agnostic** | ✓ (Hermes, OpenCode, Cline) | ✗ (OpenCode only) | ✗ (Claude Code only) |
| **Survives updates** | ✓ (user plugin dir) | ✗ (monorepo) | ✗ (bundled) |
| **Languages** | 14 | ~10 | ~10 |
| **Semantic code search** | ✓ (Semble) | ✗ | ✗ |
| **Knowledge graph** | ✓ (Graphify) | ✗ | ✗ |

## 📄 License

MIT

---

<p align="center">
  <b>agentic-lsp</b> — Ultimate vibe coding plugins for Hermes AI agent.
</p>
