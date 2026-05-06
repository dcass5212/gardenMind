"""
Manual smoke test for all 6 GardenMind tools.
Run from the project root: python tests/test_tools.py

Requires GROQ_API_KEY and OPENWEATHERMAP_API_KEY in .env.
Weather tools make live API calls; frost/plants/profile tools are offline.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from tools.weather import get_current_weather, get_forecast
from tools.frost import get_frost_dates
from tools.plants import lookup_plant_care
from tools.profile import get_garden_profile, update_garden_profile

PASS  = "\033[92m PASS\033[0m"
FAIL  = "\033[91m FAIL\033[0m"
HEAD  = "\033[1m\033[94m"
RESET = "\033[0m"

results = []


def run(label, fn, *args, **kwargs):
    """Call fn, print result, record pass/fail."""
    print(f"\n{HEAD}-- {label}{RESET}")
    print(f"   args: {args or ''}{kwargs or ''}")
    try:
        result = fn(*args, **kwargs)
        if "error" in result:
            print(f"{FAIL}  error returned: {result['error']}")
            results.append((label, False))
        else:
            print(f"{PASS}")
            for k, v in result.items():
                print(f"   {k}: {v}")
            results.append((label, True))
    except Exception as exc:
        print(f"{FAIL}  exception: {exc}")
        results.append((label, False))


def run_expect_error(label, fn, *args, **kwargs):
    """Call fn and assert it returns a dict with an 'error' key."""
    print(f"\n{HEAD}-- {label} -- expect graceful error{RESET}")
    try:
        result = fn(*args, **kwargs)
        if "error" in result:
            print(f"{PASS}  error key returned: {result['error']}")
            results.append((label, True))
        else:
            print(f"{FAIL}  expected error key, got: {result}")
            results.append((label, False))
    except Exception as exc:
        print(f"{FAIL}  unexpected exception: {exc}")
        results.append((label, False))


# 1. get_current_weather
run("get_current_weather('Denver, CO')", get_current_weather, "Denver, CO")

# 2. get_forecast
run("get_forecast('Denver, CO', days=3)", get_forecast, "Denver, CO", days=3)

# 3. get_frost_dates - exact match
run("get_frost_dates('Denver')", get_frost_dates, "Denver")

# 4. get_frost_dates - partial match
run("get_frost_dates('New York City')", get_frost_dates, "New York City")

# 5. get_frost_dates - unknown city
run_expect_error("get_frost_dates('Atlantis')", get_frost_dates, "Atlantis")

# 6. lookup_plant_care - exact key
run("lookup_plant_care('tomato')", lookup_plant_care, "tomato")

# 7. lookup_plant_care - common name search
run("lookup_plant_care('Black-Eyed Susan')", lookup_plant_care, "Black-Eyed Susan")

# 8. lookup_plant_care - unknown plant
run_expect_error("lookup_plant_care('dragon fruit')", lookup_plant_care, "dragon fruit")

# 9. update_garden_profile
run(
    "update_garden_profile('test_user', {...})",
    update_garden_profile,
    "test_user",
    {"location": "Denver, CO", "plants": ["tomato", "basil", "marigold"]},
)

# 10. get_garden_profile - should exist now
run("get_garden_profile('test_user')", get_garden_profile, "test_user")

# 11. get_garden_profile - missing user
run_expect_error("get_garden_profile('nobody')", get_garden_profile, "nobody")

# Summary
total  = len(results)
passed = sum(1 for _, ok in results if ok)
print(f"\n{'-'*50}")
print(f"Results: {passed}/{total} passed")
for label, ok in results:
    mark = "\033[92mPASS\033[0m" if ok else "\033[91mFAIL\033[0m"
    print(f"  {mark}  {label}")
print()
