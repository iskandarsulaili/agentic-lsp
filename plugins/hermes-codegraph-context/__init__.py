"""
hermes-codegraph-context — Advanced code analysis via CodeGraphContext.

Wraps CodeGraphContext (MIT, PyPI) as a native Hermes plugin for
advanced code analysis: dead code detection, complexity metrics,
call chain tracing, Spring framework introspection, and Cypher
graph queries. Uses embedded KuzuDB backend — no Docker needed.

SYNERGY with our other plugins:
  CodeGraph    → deterministic AST queries (callers, callees, impact)
  CGCtx        → advanced analysis (dead code, complexity, Spring)
  Graphify     → semantic/LLM exploration (concepts, docs)
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────
CGC_TIMEOUT = int(os.environ.get("HERMES_CGC_TIMEOUT", "120"))
CGC_DB = os.environ.get("HERMES_CGC_DB", "kuzudb")

# ── State ─────────────────────────────────────────────────────────────
_lock = threading.Lock()
_installed = False


def _ensure_installed() -> bool:
    """Auto-install codegraphcontext via pip if not found."""
    global _installed
    if _installed:
        return True
    with _lock:
        if _installed:
            return True
        try:
            import codegraphcontext  # noqa: F401
            _installed = True
            return True
        except ImportError:
            pass
        logger.info("cgc: installing codegraphcontext via pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "codegraphcontext"],
                capture_output=True,
                timeout=180,
            )
            import codegraphcontext  # noqa: F401
            _installed = True
            return True
        except Exception as e:
            logger.warning("cgc: auto-install failed: %s", e)
            return False


# ── Core analysis via subprocess ──────────────────────────────────────

def _run_cgc(args: List[str], stdin: str = "") -> Dict[str, Any]:
    """Run CodeGraphContext CLI and return parsed result."""
    if not _ensure_installed():
        return {"error": "codegraphcontext not installed. Install with: pip install codegraphcontext"}
    try:
        result = subprocess.run(
            [sys.executable, "-m", "codegraphcontext.cli.main"] + args,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=CGC_TIMEOUT,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode != 0:
            return {"error": (err or out)[:500]}
        # Try JSON parse
        if out.startswith("{"):
            return json.loads(out)
        if out.startswith("["):
            return {"results": json.loads(out)}
        return {"output": out[:5000]}
    except subprocess.TimeoutExpired:
        return {"error": f"cgc timed out after {CGC_TIMEOUT}s"}
    except Exception as e:
        return {"error": str(e)}


def _cgc_tool(action: str, params: Dict[str, Any] = None) -> str:
    """Dispatch a CGC analysis action via subprocess."""
    if params is None:
        params = {}

    # For DB-backend operations, we use the MCP protocol via subprocess
    # by running a tool dispatch through the CGC server in ping mode
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": action,
            "arguments": params,
        },
    }

    result = _run_cgc(
        ["--tool", action] + [f"--{k}={v}" for k, v in params.items()],
        stdin=json.dumps(payload),
    )
    return json.dumps(result, default=str)


# ── Tools ─────────────────────────────────────────────────────────────

def _handle_cgc_analyze(args: dict, **kwargs: Any) -> str:
    """Run code relationship analysis (15 subtypes)."""
    relationship_type = args.get("type", "call_chain")
    project = args.get("project", "")
    symbol = args.get("symbol", "")
    params = {"relationship_type": relationship_type}
    if project:
        params["project_path"] = project
    if symbol:
        params["symbol_name"] = symbol
    return _cgc_tool("analyze_code_relationships", params)


def _handle_cgc_dead_code(args: dict, **kwargs: Any) -> str:
    """Detect dead/unused code — functions, methods, and variables
    that are never called or referenced."""
    project = args.get("project", "")
    params = {}
    if project:
        params["project_path"] = project
    return _cgc_tool("find_dead_code", params)


def _handle_cgc_complexity(args: dict, **kwargs: Any) -> str:
    """Calculate cyclomatic complexity of functions/methods.
    Higher values = harder to maintain, more bugs likely."""
    project = args.get("project", "")
    params = {}
    if project:
        params["project_path"] = project
    return _cgc_tool("calculate_cyclomatic_complexity", params)


def _handle_cgc_complex_functions(args: dict, **kwargs: Any) -> str:
    """Find the most complex functions in the codebase, ranked by
    cyclomatic complexity. Use to identify high-risk refactoring targets."""
    project = args.get("project", "")
    limit = min(args.get("limit", 20), 100)
    params = {"limit": limit}
    if project:
        params["project_path"] = project
    return _cgc_tool("find_most_complex_functions", params)


def _handle_cgc_call_chain(args: dict, **kwargs: Any) -> str:
    """Trace the complete call chain for a function — every caller
    and callee across the entire codebase. Shows full execution path."""
    symbol = args.get("symbol", "")
    project = args.get("project", "")
    if not symbol:
        return json.dumps({"error": "symbol is required"})
    params = {"relationship_type": "call_chain", "symbol_name": symbol}
    if project:
        params["project_path"] = project
    return _cgc_tool("analyze_code_relationships", params)


def _handle_cgc_module_deps(args: dict, **kwargs: Any) -> str:
    """Show module-level dependency graph — which modules depend on
    which. Useful for understanding architecture layers."""
    project = args.get("project", "")
    params = {"relationship_type": "module_deps"}
    if project:
        params["project_path"] = project
    return _cgc_tool("analyze_code_relationships", params)


def _handle_cgc_spring_endpoints(args: dict, **kwargs: Any) -> str:
    """Find Java Spring Boot REST endpoints, beans, and their
    dependency wiring. Requires Spring framework project."""
    project = args.get("project", "")
    params = {}
    if project:
        params["project_path"] = project
    return _cgc_tool("find_java_spring_endpoints", params)


def _handle_cgc_cypher(args: dict, **kwargs: Any) -> str:
    """Execute a raw Cypher query against the code graph database.
    For advanced users who need custom graph traversals."""
    query = args.get("query", "")
    if not query:
        return json.dumps({"error": "Cypher query is required"})
    params = {"query": query}
    return _cgc_tool("execute_cypher_query", params)


# ── Slash command ─────────────────────────────────────────────────────

def _cmd_cgc(args: str, ctx: Any = None) -> str:
    """Interactive /cgc slash command."""
    parts = args.strip().split()
    if not parts:
        return (
            "Usage: /cgc <subcommand> [args]\n"
            "Subcommands:\n"
            "  analyze <type> [symbol]  Code relationship analysis\n"
            "  dead-code [project]      Find dead code\n"
            "  complexity [project]     Calculate complexity\n"
            "  top-complex [limit]      Find most complex functions\n"
            "  call-chain <symbol>      Trace call chain\n"
            "  module-deps [project]    Module dependencies\n"
            "  spring [project]         Spring endpoints (Java)\n"
            "  cypher <query>           Run Cypher query"
        )

    cmd = parts[0]
    rest = parts[1:]

    if cmd == "analyze":
        rtype = rest[0] if rest else "call_chain"
        symbol = rest[1] if len(rest) > 1 else ""
        return _handle_cgc_analyze({"type": rtype, "symbol": symbol}, ctx=ctx)
    if cmd == "dead-code":
        return _handle_cgc_dead_code({"project": " ".join(rest)}, ctx=ctx)
    if cmd == "complexity":
        return _handle_cgc_complexity({"project": " ".join(rest)}, ctx=ctx)
    if cmd == "top-complex":
        limit = int(rest[0]) if rest and rest[0].isdigit() else 20
        return _handle_cgc_complex_functions({"limit": limit}, ctx=ctx)
    if cmd == "call-chain":
        return _handle_cgc_call_chain({"symbol": " ".join(rest)}, ctx=ctx)
    if cmd == "module-deps":
        return _handle_cgc_module_deps({"project": " ".join(rest)}, ctx=ctx)
    if cmd == "spring":
        return _handle_cgc_spring_endpoints({"project": " ".join(rest)}, ctx=ctx)
    if cmd == "cypher":
        return _handle_cgc_cypher({"query": " ".join(rest)}, ctx=ctx)

    return f"Unknown subcommand: {cmd}. Use /cgc for help."


# ── Register ──────────────────────────────────────────────────────────

def register(ctx) -> Dict[str, Any]:
    """Register the hermes-codegraph-context plugin."""

    ctx.register_tool(
        name="cgc_analyze",
        toolset="codegraph-context",
        schema={
            "name": "cgc_analyze",
            "description": "Analyze code relationships in a project. Supports 15 subtypes: call_chain, module_deps, class_hierarchy, variable_scope, data_flow, dead_code, cyclomatic_complexity, find_complexity, find_functions_by_decorator, and more. Use to understand how code connects at a structural level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Relationship type: call_chain, module_deps, class_hierarchy, variable_scope, data_flow, dead_code, cyclomatic_complexity, find_complexity, find_functions_by_decorator (default: call_chain)"},
                    "project": {"type": "string", "description": "Project directory path"},
                    "symbol": {"type": "string", "description": "Optional symbol name to focus analysis on"},
                },
            },
        },
        handler=_handle_cgc_analyze,
    )

    ctx.register_tool(
        name="cgc_dead_code",
        toolset="codegraph-context",
        schema={
            "name": "cgc_dead_code",
            "description": "Detect dead/unused code — functions, methods, and variables that are never called or referenced across the entire codebase. Use for cleanup and refactoring before making changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project directory path"},
                },
            },
        },
        handler=_handle_cgc_dead_code,
    )

    ctx.register_tool(
        name="cgc_complexity",
        toolset="codegraph-context",
        schema={
            "name": "cgc_complexity",
            "description": "Calculate cyclomatic complexity of functions and methods. Higher values indicate harder-to-maintain, bug-prone code. Use to identify refactoring priorities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project directory path"},
                },
            },
        },
        handler=_handle_cgc_complexity,
    )

    ctx.register_tool(
        name="cgc_top_complex",
        toolset="codegraph-context",
        schema={
            "name": "cgc_top_complex",
            "description": "Find the most complex functions in a codebase, ranked by cyclomatic complexity. The top results are the highest-risk refactoring targets. Use to prioritize technical debt reduction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 20, max: 100)"},
                    "project": {"type": "string", "description": "Project directory path"},
                },
            },
        },
        handler=_handle_cgc_complex_functions,
    )

    ctx.register_tool(
        name="cgc_call_chain",
        toolset="codegraph-context",
        schema={
            "name": "cgc_call_chain",
            "description": "Trace the complete call chain for a symbol (function, method, or class member). Shows every caller and callee — the full execution path through the codebase. Use to understand impact before making changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Function/method/symbol name to trace"},
                    "project": {"type": "string", "description": "Project directory path"},
                },
                "required": ["symbol"],
            },
        },
        handler=_handle_cgc_call_chain,
    )

    ctx.register_tool(
        name="cgc_module_deps",
        toolset="codegraph-context",
        schema={
            "name": "cgc_module_deps",
            "description": "Show module-level dependency graph — which modules import and depend on which. Useful for understanding architecture layers, identifying circular dependencies, and planning refactoring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project directory path"},
                },
            },
        },
        handler=_handle_cgc_module_deps,
    )

    ctx.register_tool(
        name="cgc_spring",
        toolset="codegraph-context",
        schema={
            "name": "cgc_spring",
            "description": "Find Java Spring Boot REST endpoints, beans, and their dependency wiring. Shows controllers, services, repositories, and their injection relationships. Requires a Spring Boot project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Spring Boot project directory path"},
                },
            },
        },
        handler=_handle_cgc_spring_endpoints,
    )

    ctx.register_tool(
        name="cgc_cypher",
        toolset="codegraph-context",
        schema={
            "name": "cgc_cypher",
            "description": "Execute a raw Cypher query against the code graph database. For advanced users who need custom graph traversals beyond the built-in analysis tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Cypher query string"},
                },
                "required": ["query"],
            },
        },
        handler=_handle_cgc_cypher,
    )

    ctx.register_command(
        name="/cgc",
        description="CodeGraphContext: advanced code analysis commands",
        handler=_cmd_cgc,
    )

    logger.info(
        "cgc: 9 tools registered — dead code, complexity, call chains, "
        "Spring introspection, Cypher queries. Auto-syncs via pip on first use."
    )

    return {"name": "hermes-codegraph-context", "version": "1.0.0"}
