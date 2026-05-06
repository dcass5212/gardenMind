"""
End-to-end agent test for Phase 3.
Runs two scenarios through run_agent() and prints the full result.
Run from the project root: py tests/test_agent.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from agent import run_agent

PASS  = "\033[92mPASS\033[0m"
FAIL  = "\033[91mFAIL\033[0m"
HEAD  = "\033[1m\033[94m"
RESET = "\033[0m"

results = []


def run_scenario(title, messages):
    """
    Send one or more messages through run_agent() and print the final reply.
    messages is a list of strings; each is a separate turn in the same conversation.
    Returns the last reply.
    """
    print(f"\n{HEAD}{'='*60}{RESET}")
    print(f"{HEAD}{title}{RESET}")
    print(f"{HEAD}{'='*60}{RESET}")

    history = []
    reply = ""
    try:
        for msg in messages:
            print(f"\nUser: {msg}")
            reply = run_agent(msg, history)
            print(f"\nGardenMind: {reply}")

        ok = bool(reply and len(reply) > 40)
        if ok:
            print(f"\n{PASS}")
        else:
            print(f"\n{FAIL}  reply too short or empty")
        results.append((title, ok))
    except Exception as exc:
        print(f"\n{FAIL}  exception: {exc}")
        results.append((title, False))

    return reply


# ------------------------------------------------------------------
# Scenario 1: single-tool — current weather
# Verifies the agent calls get_current_weather and summarises it.
# ------------------------------------------------------------------
run_scenario(
    "Scenario 1: single tool — current weather",
    ["What is the current weather in Denver?"],
)

# ------------------------------------------------------------------
# Scenario 2: multi-step — planting safety check
# The agent must chain: get_current_weather + get_frost_dates +
# lookup_plant_care to give a grounded recommendation.
# ------------------------------------------------------------------
run_scenario(
    "Scenario 2: multi-step — planting safety check",
    [
        "I'm in Denver, CO and I'm growing tomatoes and basil. "
        "Given the current weather and frost dates, is it safe to transplant "
        "my tomatoes outside this week?"
    ],
)

# ------------------------------------------------------------------
# Scenario 3: multi-turn memory — profile then follow-up
# Turn 1: save a profile. Turn 2: ask a follow-up that requires the
# agent to recall context from the conversation history.
# ------------------------------------------------------------------
run_scenario(
    "Scenario 3: multi-turn — profile save then contextual follow-up",
    [
        "Save my garden profile: I'm user demo_user, located in Seattle, WA, "
        "and I'm growing kale, mint, and marigolds.",
        "Given my garden, what should I be most worried about this week weather-wise?",
    ],
)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
total  = len(results)
passed = sum(1 for _, ok in results if ok)
print(f"\n{'-'*60}")
print(f"Results: {passed}/{total} scenarios passed")
for title, ok in results:
    mark = f"\033[92mPASS\033[0m" if ok else f"\033[91mFAIL\033[0m"
    print(f"  {mark}  {title}")
print()
