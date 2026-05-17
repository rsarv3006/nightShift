"""Fake planner for the NightShift end-to-end quickstart."""

from __future__ import annotations

import sys


prompt = sys.stdin.read()
if "repo_lookup_results" in prompt:
    print("# Plan")
    print("")
    print("- Use the context pack and inspected files.")
    print("- Add parser functions to `lisp.py`.")
    print("- Replace the smoke test with parser unit tests.")
else:
    print("lookup_requests:")
    print("- tool: read_file")
    print("  path: lisp.py")
    print("- tool: read_file")
    print("  path: tests/test_lisp.py")
