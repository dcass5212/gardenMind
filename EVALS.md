# GardenMind Evals

## Overview

GardenMind evals verify that the agent correctly routes user queries to the right tools and produces responses with the expected content. Each test case specifies:

- **expected_tools** — every tool listed must appear in the conversation history (empty list = skip check)
- **expected_keywords** — every string listed must appear case-insensitively in the final reply (empty list = skip check)

A test passes only when both checks are satisfied and no exception is raised.

The eval runner pre-seeds an `evals_user` profile so garden-profile and integration tests don't depend on `profile_create` running first.

## Test Case Categories

| Category | Count | What it tests |
|---|---|---|
| weather | 5 | `get_current_weather` and `get_forecast` for various cities and phrasings |
| frost_dates | 5 | `get_frost_dates` including state-suffix normalisation and unknown-city graceful error |
| plant_care | 5 | `lookup_plant_care` including plural names, hyphenated names, and unknown plants |
| garden_profile | 5 | `get_garden_profile` and `update_garden_profile` for create, load, update, and error cases |
| integration | 5 | Multi-tool chains: weather+frost, weather+plant care, forecast+plant care, profile+weather |

## How to Run

```
py evals/run_evals.py
```

Options:
- `--no-update-evals-md` — print results only, don't overwrite this file

## Model Note

The model is `llama-3.1-8b-instant` (Groq). The 8b model is less reliable at echoing location names and plant names in replies, accounting for most failures. Tool routing is correct in all cases.

## Results

_Last run: 2026-05-04 — 20/25 passed_

| Category | Total Cases | Passing | Pass Rate |
|---|---|---|---|
| weather | 5 | 3 | 60% |
| frost_dates | 5 | 5 | 100% |
| plant_care | 5 | 5 | 100% |
| garden_profile | 5 | 3 | 60% |
| integration | 5 | 4 | 80% |
| **TOTAL** | **25** | **20** | **80%** |

### Known failures (8b model limitations)

- **weather_current_chicago / weather_forecast_5day** — model gives correct data but doesn't echo the city name or the word "temperature" in the reply
- **profile_create / profile_load** — model calls the right tool but pivots to weather without summarising the profile contents
- **integration_planting_safety** — occasional model refusal ("I can't provide gardening advice for a specific user")

All failures are keyword-echo or model-reasoning issues with `llama-3.1-8b-instant`; tool routing is correct in all cases except the profile/integration replies that skip summarising data.
