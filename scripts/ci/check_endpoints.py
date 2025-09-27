#!/usr/bin/env python3
"""CI guard script to prevent reintroduction of hardcoded localhost service URLs
and stale/incorrect port mappings.

Checks:
1. No 'http://localhost:' or 'https://localhost:' in runtime source (py/ts/tsx/sh) outside allowlist paths.
2. Service URL port usages match authoritative mapping in docs/SERVICE_ENDPOINTS.md

Exit codes:
 0 = OK
 1 = Violations found

Allowlist (may contain localhost examples):
 - README.md, docs/**, */docs/**
 - frontend/_frontend_cleanup/** (legacy)
 - config/environment/*.env*
 - *.example, *.sample

Usage:
  python scripts/ci/check_endpoints.py

Integrate this in CI before tests to enforce discipline.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_DOC = REPO_ROOT / "docs" / "SERVICE_ENDPOINTS.md"

ALLOW_DIR_PATTERNS = [
    re.compile(r"(^|/)docs(/|$)"),
    re.compile(r"(^|/)frontend/_frontend_cleanup(/|$)"),
    re.compile(r"(^|/)node_modules(/|$)"),  # Third-party dependencies
]
ALLOW_FILE_PATTERNS = [
    re.compile(r"README\.md$"),
    re.compile(r"\.env(\.|$)"),
    re.compile(r"\.example$"),
    re.compile(r"\.sample$"),
]
RUNTIME_EXTENSIONS = {".py", ".ts", ".tsx", ".sh"}

LOCALHOST_RE = re.compile(r"https?://localhost:\d+")
URL_RE = re.compile(r"http://([a-z0-9\-]+):(\d+)")


def load_authoritative_ports() -> dict[str, int]:
    if not SERVICE_DOC.exists():
        print(f"ERROR: {SERVICE_DOC} not found", file=sys.stderr)
        return {}
    mapping: dict[str, int] = {}
    in_table = False
    for line in SERVICE_DOC.read_text().splitlines():
        if line.startswith("| api_gateway"):
            in_table = True
        if in_table and line.startswith("|") and not line.startswith("| Service Key"):
            cols = [c.strip() for c in line.strip().split("|") if c.strip()]
            if len(cols) >= 5:
                # Expect: Service Key, Internal DNS Host, Port, Env Var, Default URL
                key = cols[0]
                host = cols[1]
                port = cols[2]
                default_url = cols[4]
                try:
                    mapping[host] = int(port)
                    # Also capture key->port for additional validation
                    mapping[key] = int(port)
                    # Parse default URL to cross-validate
                except ValueError:
                    pass
        elif in_table and line.strip() == "":
            break
    return mapping


def is_allowed(path: Path) -> bool:
    rel = str(path.as_posix())
    if any(p.search(rel) for p in ALLOW_DIR_PATTERNS):
        return True
    if any(p.search(rel) for p in ALLOW_FILE_PATTERNS):
        return True
    return False


def scan_files() -> tuple[list[str], list[str]]:
    localhost_hits: list[str] = []
    port_mismatch: list[str] = []
    port_map = load_authoritative_ports()

    for path in REPO_ROOT.rglob('*'):
        if not path.is_file():
            continue
        if path.suffix not in RUNTIME_EXTENSIONS:
            continue
        if is_allowed(path):
            continue
        try:
            text = path.read_text(errors='ignore')
        except Exception:
            continue
        # 1. localhost detection
        for match in LOCALHOST_RE.finditer(text):
            localhost_hits.append(f"{path}:{match.group(0)}")
        # 2. port mapping validation (urls to service DNS hosts)
        for match in URL_RE.finditer(text):
            host, port = match.group(1), int(match.group(2))
            if host in port_map and port_map[host] != port:
                port_mismatch.append(f"{path}:{host}:{port} != {port_map[host]}")
    return localhost_hits, port_mismatch


def main() -> int:
    localhost_hits, port_mismatch = scan_files()
    if not localhost_hits and not port_mismatch:
        print("✅ Endpoint guard passed: no localhost leaks or port mismatches in runtime code.")
        return 0
    if localhost_hits:
        print("❌ Disallowed localhost usages found:")
        for h in localhost_hits:
            print("  " + h)
    if port_mismatch:
        print("❌ Port mismatches found (file:host:found != expected):")
        for m in port_mismatch:
            print("  " + m)
    print("\nRefer to docs/SERVICE_ENDPOINTS.md for authoritative mapping.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
