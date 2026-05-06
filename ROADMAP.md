# GardenMind Roadmap

## Phase 1 — Foundation 🟡

- [x] Project structure created
- [x] CLAUDE.md created
- [x] ROADMAP.md created
- [x] requirements.txt complete
- [x] .env configured with API keys
- [x] data/plants.json built with 25 plants

## Phase 2 — Tools 🟡

- [x] tools/weather.py — get_current_weather, get_forecast
- [x] tools/frost.py — get_frost_dates
- [x] tools/plants.py — lookup_plant_care
- [x] tools/profile.py — get_garden_profile, update_garden_profile
- [x] All tools manually tested

## Phase 3 — Agent Core ✅

- [x] agent.py — Groq tool use loop wired up
- [x] Agent can call all 6 tools
- [x] Multi-step reasoning works end to end
- [x] Tested in terminal/CLI

## Phase 4 — UI ✅

- [x] ui/app.py — Streamlit chat interface
- [x] Shows tool calls in real time
- [x] Garden profile sidebar
- [x] Conversation memory across turns

## Phase 5 — Evals ✅

- [x] 25 test cases written in evals/test_cases.json
- [x] evals/run_evals.py script complete
- [x] Pass rate measured and documented — 20/25 (80%) on llama-3.1-8b-instant

## Phase 6 — Polish ✅README.md complete with demo screenshots
- [x] Code cleaned up and commented
- [x] Deployed to Streamlit Cloud