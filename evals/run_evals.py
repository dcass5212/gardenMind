"""
GardenMind eval runner.

Runs every test case in evals/test_cases.json through run_agent(), checks:
  - expected_tools: every listed tool must appear in conversation history
  - expected_keywords: every listed string must appear in the reply (case-insensitive)

A test PASSES only when both checks are satisfied.
An empty list means "skip this check."

Profile dependency: the garden_profile and integration categories include tests
that read evals_user's profile.  A setup step pre-seeds that profile so those
tests are not order-dependent on profile_create passing first.

Usage:
    py evals/run_evals.py [--no-update-evals-md]
"""

import sys
import json
import time
import argparse
from datetime import date
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from tools.profile import update_garden_profile
from agent import run_agent

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_LABEL = f"{GREEN}PASS{RESET}"
FAIL_LABEL = f"{RED}FAIL{RESET}"

# ── Paths ─────────────────────────────────────────────────────────────────────
CASES_FILE = Path(__file__).parent / "test_cases.json"
EVALS_MD   = Path(__file__).parent.parent / "EVALS.md"


def load_cases() -> list[dict]:
    with open(CASES_FILE, encoding="utf-8") as f:
        return json.load(f)


def setup():
    """Pre-seed evals_user so profile_load and integration tests are independent."""
    update_garden_profile(
        "evals_user",
        {"location": "Boston, MA", "plants": ["tomato", "basil", "marigold"]},
    )


def tools_called_from_history(history: list) -> set[str]:
    """Extract every tool name that was actually called during the agent turn."""
    called = set()
    for msg in history:
        for tc in msg.get("tool_calls") or []:
            called.add(tc["function"]["name"])
    return called


def run_case(case: dict) -> dict:
    """Run a single test case. Returns a result dict."""
    history = []
    reply = ""
    error = None

    try:
        reply = run_agent(case["input"], history)
    except Exception as exc:
        error = str(exc)

    called   = tools_called_from_history(history)
    reply_lc = reply.lower()

    missing_tools    = [t for t in case["expected_tools"]    if t not in called]
    missing_keywords = [k for k in case["expected_keywords"] if k.lower() not in reply_lc]

    passed = error is None and not missing_tools and not missing_keywords

    return {
        "id":               case["id"],
        "category":         case["category"],
        "description":      case["description"],
        "passed":           passed,
        "error":            error,
        "tools_called":     sorted(called),
        "missing_tools":    missing_tools,
        "missing_keywords": missing_keywords,
        "reply_preview":    reply[:120].replace("\n", " "),
    }


def print_result(result: dict, idx: int, total: int):
    label = PASS_LABEL if result["passed"] else FAIL_LABEL
    print(f"  [{idx:>2}/{total}] {label}  {result['id']}")
    if not result["passed"]:
        if result["error"]:
            print(f"         {RED}error:{RESET} {result['error'][:120]}")
        if result["missing_tools"]:
            print(f"         {YELLOW}missing tools:{RESET} {result['missing_tools']}")
        if result["missing_keywords"]:
            print(f"         {YELLOW}missing keywords:{RESET} {result['missing_keywords']}")
        print(f"         reply: {result['reply_preview']!r}")


def print_summary(results: list[dict]):
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    total_pass = sum(1 for r in results if r["passed"])
    total      = len(results)

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Summary — {total_pass}/{total} passed ({total_pass/total:.0%}){RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    print(f"\n{'Category':<20} {'Pass':>5} {'Total':>6} {'Rate':>6}")
    print("-" * 42)
    for cat, cat_results in by_cat.items():
        p = sum(1 for r in cat_results if r["passed"])
        n = len(cat_results)
        print(f"{cat:<20} {p:>5} {n:>6} {p/n:>6.0%}")
    print("-" * 42)
    print(f"{'TOTAL':<20} {total_pass:>5} {total:>6} {total_pass/total:>6.0%}")
    print()


def update_evals_md(results: list[dict]):
    """Overwrite the Results section of EVALS.md with live numbers."""
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    total_pass = sum(1 for r in results if r["passed"])
    total      = len(results)

    rows = []
    for cat, cat_results in by_cat.items():
        p = sum(1 for r in cat_results if r["passed"])
        n = len(cat_results)
        rows.append(f"| {cat} | {n} | {p} | {p/n:.0%} |")

    rows.append(f"| **TOTAL** | **{total}** | **{total_pass}** | **{total_pass/total:.0%}** |")

    table = (
        "| Category | Total Cases | Passing | Pass Rate |\n"
        "|---|---|---|---|\n"
        + "\n".join(rows)
    )

    current = EVALS_MD.read_text(encoding="utf-8")
    before, _, _ = current.partition("## Results")
    new_content = (
        before
        + "## Results\n\n"
        + f"_Last run: {date.today()} — {total_pass}/{total} passed_\n\n"
        + table
        + "\n"
    )
    EVALS_MD.write_text(new_content, encoding="utf-8")
    print(f"EVALS.md updated with {date.today()} results.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-update-evals-md", action="store_true")
    args = parser.parse_args()

    cases = load_cases()

    print(f"{BOLD}GardenMind Evals — {len(cases)} test cases{RESET}")
    print("Setting up pre-seeded profile for eval tests...")
    setup()
    print("Done.\n")

    results = []
    for i, case in enumerate(cases, 1):
        cat = case["category"]
        if i == 1 or cases[i-2]["category"] != cat:
            print(f"\n{BOLD}[ {cat.upper()} ]{RESET}")
        result = run_case(case)
        results.append(result)
        print_result(result, i, len(cases))
        time.sleep(12)  # llama-3.1-8b-instant has 30k TPM; integration tests use 4-6 calls

    print_summary(results)

    if not args.no_update_evals_md:
        update_evals_md(results)


if __name__ == "__main__":
    main()
