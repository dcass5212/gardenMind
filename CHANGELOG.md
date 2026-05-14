# Changelog

All notable changes to GardenMind are documented here.
Format: `## [date] — summary of change`

---

## [2026-05-11] — Add semantic vector search for plant lookup

- Added `chromadb` + `sentence-transformers` to `requirements.txt`
- `scripts/build_plant_index.py` — indexes all 200 plants into a persistent ChromaDB collection using `all-MiniLM-L6-v2` embeddings
- `tools/plants.py` — now tries fast JSON exact/plural/substring lookup first, then falls back to semantic vector search for descriptive queries (e.g. "drought tolerant succulent" → Sedum); original `data/plants.json` retained as canonical source and hard fallback
- `ROADMAP.md` — added Phase 7 (ML Upgrade) with 7a/7b/7c items; marked 7a complete

---

## [2026-05-11] — Fix five bugs across agent, tools, and UI

- `agent.py`: `_chat()` now raises `RuntimeError` after exhausting all retries instead of implicitly returning `None` and causing a downstream `AttributeError`
- `tools/frost.py`: partial city match now sorts by name length (longest first) so "Portland, OR" matches "portland or" (Oregon) instead of "portland" (Maine)
- `tools/plants.py`: changed `if/if` to `if/elif` for pluralization candidates — words ending in "es" no longer also trigger the bare "s" strip, avoiding a spurious intermediate candidate
- `tools/profile.py`: added `_safe_profile_path()` to validate that a resolved profile path stays within `_PROFILES_DIR`, preventing path traversal via crafted `user_id` values
- `ui/app.py`: replicated `run_agent`'s XML tool-leak retry/strip logic in the UI's inline agent loop; also imports `_RAW_TOOL_RE` and `_strip_leaked_tool_syntax` from `agent`

---

## [2026-05-11] — Fix leaked tool-call syntax in agent responses

- Expanded `_RAW_TOOL_RE` to also catch `<tool_call>...</tool_call>` blocks (llama-3.1-8b-instant's second leak format)
- Added `_strip_leaked_tool_syntax()` as a deterministic fallback when retries are exhausted, so raw function syntax never reaches the user

## [2026-05-06] — README screenshots and INTERVIEW.md metrics fix

- Renamed 3 docs/ screenshots to URL-safe filenames
- Wired screenshots into README Demo section as a three-column table
- Fixed stale plant count in INTERVIEW.md (100 → 200, with correct category breakdown)
- Updated "What I'd Build Next" plant library bullet to reflect current 200-plant baseline

## [2026-05-06] — Streamlit Cloud compatibility

- Inject `st.secrets` into `os.environ` at startup in `ui/app.py` so API keys work on Streamlit Cloud without code changes

## [2026-05-06] — Pre-commit file organization

- Created `docs/` folder for README screenshots
- Moved `test_agent.py` and `test_tools.py` to `tests/` with root path fix
- Updated `CLAUDE.md` to reflect new directory layout

## [2026-05-06] — Welcome box custom green color

- Replaced `st.info()` welcome card with a styled HTML `div` using background color `#3a8c26`

## [2026-05-06] — Unified main background color

- Changed chat message bubble background from `_SECONDARY_BG` to `_BG` so the main area has no color variation

## [2026-05-06] — Info box exact color and full prompt bar styling

- Set info box background to exact `#3a8c26`
- Extended chat input selectors to cover `stBottom` wrapper so the entire prompt bar matches sidebar color

## [2026-05-06] — Tuned info box green and chat input color

- Bumped info box background from `#172B0D` to `#1A4A14` for a more saturated true green
- Updated chat input container to match sidebar color (`_SECONDARY_BG`) instead of main background

## [2026-05-06] — Changed info box from blue to leafy green

- Overrode `st.info()` alert background to dark green (`#172B0D`) and forced SVG icon to `_PRIMARY` green

## [2026-05-06] — Lightened sidebar background color

- Changed `_SECONDARY_BG` from `#1C1510` to `#2E1F14` for more contrast between sidebar and main area

## [2026-05-06] — Cleaned up README demo section

- Removed GIF placeholder; added commented screenshot slot pointing to docs/screenshot.png

## [2026-05-06] — Added doc update convention to CLAUDE.md; updated ROADMAP.md

- Added "Doc Update Convention" section to CLAUDE.md listing which docs to update and when
- Marked completed portfolio readiness items in ROADMAP.md

## [2026-05-06] — Added CLAUDE.md to .gitignore

- CLAUDE.md contains AI tooling meta-instructions not appropriate for a public repo

## [2026-05-06] — Cleaned up .gitignore

- Added sections/comments for organization
- Added `*.pyo`, `*.egg-info/`, `venv/`, `.venv/`, `env/`

## [2026-05-06] — Updated README plant count to 200

- Fixed plant count in features list (100 → 200) and architecture table (25 → 200)
- Removed "larger plant library" from "What I'd Build Next" since it's already done

## [2026-05-06] — Synced docs to match model in code (llama-3.1-8b-instant)

- Updated CLAUDE.md, EVALS.md, and ROADMAP.md to reflect `llama-3.1-8b-instant` as the active model

## [2026-05-06] — Added portfolio readiness checklist to ROADMAP.md

- Appended "Portfolio Readiness" section to ROADMAP.md with critical, high-impact, and polish tasks

## [2026-05-06] — Expanded plant library to 200 plants

- Added 50 new plants to `data/plants.json`: 10 vegetables (jicama, sunchoke, napa cabbage, malabar spinach, amaranth greens, mizuna, purslane, escarole, garden cress, yam), 10 herbs (rue, angelica, summer savory, sweet woodruff, pennyroyal, lemon thyme, holy basil, nigella, curry leaf, vietnamese coriander), 15 flowers (ranunculus, anemone, clematis, wisteria, dianthus, scabiosa, gaillardia, agapanthus, crocosmia, liatris, astilbe, geum, catmint, balloon flower, sweet william), 15 fruits (persimmon, jujube, serviceberry, tayberry, boysenberry, pineapple guava, passion fruit, dragon fruit, loquat, olive, avocado, lime, orange, grapefruit, medlar)
- Plant library now totals 200 plants: 60 vegetables, 45 herbs, 55 flowers, 40 fruits

## [2026-05-05] — Inject garden profile into system prompt for personalized responses

- Added `_build_system_prompt()` in `ui/app.py` that appends the loaded profile (location + plants) to the system prompt on every turn
- The model now always has the profile in context without needing to call `get_garden_profile` first — fixes responses not using profile data

## [2026-05-05] — Expanded plant library to 150 plants

- Added 50 new plants to `data/plants.json`: 15 vegetables (artichoke, parsnip, rutabaga, celeriac, endive, mustard greens, collard greens, tomatillo, shallot, edamame, fava bean, lima bean, acorn squash, radicchio, watercress), 10 herbs (lemon verbena, fenugreek, winter savory, spearmint, bee balm, anise hyssop, epazote, shiso, caraway, sweet cicely), 15 flowers (peony, chrysanthemum, lily, iris, tulip, daffodil, ornamental allium, aster, delphinium, lupine, bleeding heart, hellebore, phlox, verbena, stock), 10 fruits (pear, plum, apricot, elderberry, mulberry, kiwi, pomegranate, quince, nectarine, pawpaw)
- Plant library now totals 150 plants: 50 vegetables, 35 herbs, 40 flowers, 25 fruits

## [2026-05-05] — Handle 413 request-too-large by trimming history

- Imported `APIStatusError` from groq in `agent.py`
- `_chat()` now catches 413 errors, drops the two oldest non-system messages, and retries — preventing crashes when long conversations exceed the 8b model's 6k TPM limit

## [2026-05-05] — Soft dark UI theme

- Neutral slate/charcoal palette: `#16191C` base, `#1D2126` sidebar, `#22272E` cards
- Muted sage green accent (`#6FA882`) — subtle, not neon
- Clean off-white text (`#E2E8E0`) with muted caption color (`#7E8F82`)
- Chat bubbles distinguished by background shade only — no harsh colored borders
- Inputs highlight with sage border on focus
- Sidebar has a clean right border divider
- Chat container capped at 860px width; slim custom scrollbar

## [2026-05-05] — Refined Dark Forest color scheme

- Background lightened to `#251A0D` (warmer medium brown)
- Sidebar and chat box updated to deep forest green (`#1A2E14`)
- Input fields use darker green `#162410`; border updated to `#2E4A22`

## [2026-05-05] — Overhauled to single Dark Forest theme with warmer palette

- Removed light mode and theme toggle
- New palette: dark soil background (`#130F08`), dark bark sidebar (`#1C1510`), warm cream text (`#EDD9A0`), vivid leaf green accent (`#6EC44A`)
- CSS injection simplified to a single `_inject_theme()` call with module-level color constants

## [2026-05-05] — Added light/dark theme toggle

- Defined two palettes in `ui/app.py`: Dark Forest (deep greens) and Light Garden (warm parchment)
- Theme injected via CSS on every render; toggle button in sidebar switches and reruns
- `config.toml` updated to Dark Forest as the startup default

## [2026-05-05] — Switched to dark earthy theme

- Updated `.streamlit/config.toml`: dark soil brown background (`#2B1A0A`), mulch-toned sidebar (`#3D2812`), warm leaf green primary (`#8BC97A`), cream/parchment text (`#EDD9A8`)

## [2026-05-05] — Updated Streamlit theme for compatibility with v1.44+ redesign

- Added `base = "light"` to `.streamlit/config.toml` to anchor theme explicitly in newer Streamlit versions
- Refined color palette: deeper forest green primary (`#3A7D44`), warm off-white background (`#FDFCF5`), light sage secondary background (`#E8F0E1`), near-black text with green tint (`#1E2A1F`)

## [2026-05-05] — Fallback warning when plant data is missing

- Updated system prompt in `agent.py` to instruct the LLM to display a ⚠️ disclaimer when `lookup_plant_care` returns an error, making clear the advice is from general knowledge rather than the curated database

## [2026-05-05] — Expanded plant library from 25 to 100 plants

- Added 75 plants to `data/plants.json`: 25 new vegetables, 17 new herbs, 18 new flowers, and a new "fruit" type with 15 plants
- New vegetables: eggplant, sweet potato, potato, onion, garlic, radish, beet, snap pea, swiss chard, cauliflower, cabbage, brussels sprouts, butternut squash, pumpkin, hot pepper, leek, corn, asparagus, celery, arugula, bok choy, turnip, kohlrabi, okra, fennel
- New herbs: sage, dill, tarragon, lemon balm, chamomile, stevia, lemongrass, bay laurel, borage, catnip, marjoram, sorrel, chervil, lovage, hyssop, valerian, thai basil
- New flowers: dahlia, rose, coneflower, hydrangea, impatiens, geranium, begonia, pansy, snapdragon, columbine, coreopsis, daylily, foxglove, hollyhock, salvia, sedum, yarrow, nasturtium
- New fruits: strawberry, blueberry, raspberry, blackberry, grape, watermelon, cantaloupe, fig, lemon, apple, peach, cherry, gooseberry, currant, rhubarb
- Updated CLAUDE.md current status to reflect final plant count
- Final breakdown: 35 vegetables, 25 herbs, 25 flowers, 15 fruits = 100 total

## [2026-05-05] — Phase 6 complete: interview talking points

- Created `INTERVIEW.md` with elevator pitch, stack rationale, 7 key technical decisions, metrics table, 3 challenge narratives, and 10 anticipated Q&A pairs
- ROADMAP.md: Phase 6 task 4 marked complete, phase status → ✅

## [2026-05-05] — Phase 6 tasks 1-3: README, code cleanup, Streamlit Cloud prep

- Completed README.md: filled in all TODOs (overview, features, architecture, setup, deployment, what's next)
- Cleaned up `agent.py`: replaced `import groq as _groq_module` alias with direct `from groq import RateLimitError, BadRequestError`
- Cleaned up `ui/app.py`: moved Groq client init into session state so it's created once per session, not per message
- Created `.streamlit/config.toml` with green theme
- Created `.streamlit/secrets.toml.example` as a deployment reference
- Created `.gitignore` (was missing) covering `.env`, `secrets.toml`, `data/profiles/`, and `__pycache__`
- ROADMAP.md: tasks 1-3 of Phase 6 marked complete

## [2026-05-05] — Updated run commands to use py launcher

- Fixed `streamlit run` → `py -m streamlit run ui/app.py` in CLAUDE.md and README.md
- Fixed `python evals/run_evals.py` → `py evals/run_evals.py` in same files

## [2026-05-04] — Phase 5 complete: evals 20/25 (80%) on llama-3.1-8b-instant

- Wrote 25 eval test cases in `evals/test_cases.json` across 5 categories (weather, frost_dates, plant_care, garden_profile, integration)
- Wrote `evals/run_evals.py` runner with pre-seeded profile setup, per-test tool and keyword checks, category summary, and auto-update of EVALS.md
- Switched inference model from `llama-3.3-70b-versatile` to `llama-3.1-8b-instant` after exhausting the Groq free-tier daily TPD limit during eval runs
- Added raw XML tool-call detection in `run_agent()`: if the 8b model emits `<function>XML</function>` as text instead of structured calls, retries up to 2 times
- Broadened `_chat()` BadRequestError retry to also catch "tool call validation failed" (model hallucinating non-existent tools like `brave_search`)
- Added `import re` to agent.py
- Final result: 20/25 passed — frost_dates 5/5, plant_care 5/5, integration 4/5, weather 3/5, garden_profile 3/5
- Failures are keyword-echo issues with the 8b model (tool routing is correct); expect higher pass rates on 70b
- Phase 5 marked ✅ in ROADMAP.md; EVALS.md updated with overview, category descriptions, model note, and failure analysis

## [2026-05-04] — Phase 3 complete: multi-step reasoning and CLI verified

- Added `_chat()` helper to `agent.py` with retry logic (up to 3 attempts) for Groq 400 "tool_use_failed" errors caused by occasional malformed tool-call generation in llama-3.3-70b-versatile
- Wired `_chat()` into both `run_agent()` and `ui/app.py` agent loop
- Fixed `lookup_plant_care` to handle plural plant names (e.g. "marigolds" → "marigold") via trailing-s/es stripping
- Created `test_agent.py` with 3 end-to-end scenarios: single-tool weather, multi-step planting safety check (weather + frost + plant care), and multi-turn profile save + contextual follow-up — all passed
- Phase 3 marked ✅ in ROADMAP.md

## [2026-05-04] — Ran Phase 2 smoke tests: 9/11 passed

- Tests 1-2 (weather tools) failed with 401 Unauthorized — OPENWEATHERMAP_API_KEY not yet set in .env; expected
- Tests 3-11 (frost, plants, profile) all passed including partial-match and graceful-error cases
- Fixed `tools/plants.py` and `tools/profile.py` to open files with `encoding="utf-8"` explicitly (Windows cp1252 default caused mojibake in terminal output)
- Added Tools table to `README.md` under new Tools section

## [2026-05-04] — Added test_tools.py smoke test script

- 11 test cases covering all 6 tools: exact matches, partial/fuzzy matches, round-trip profile write+read, and graceful error handling for unknown inputs
- Color-coded pass/fail output with summary table; no test framework needed — runs with `python test_tools.py`

## [2026-05-04] — Built Streamlit UI (ui/app.py)

- Wide-layout chat interface with persistent conversation memory via `st.session_state`
- Sidebar: user ID input, location + plants editor, Load/Save profile buttons, active profile summary, clear conversation button
- Agent loop runs directly in the UI using Groq + `_call_tool` from `agent.py`, giving Streamlit control between tool calls
- `st.status` widget shows each tool call in real time (name, args, JSON result) while the agent works; collapses to "✅ Done" when finished
- Empty-state welcome card with example prompts
- Conversation replay filters out intermediate tool/assistant-tool-call turns; only user messages and final replies are re-rendered on reload

## [2026-05-04] — Built data/plants.json, all 6 tools, and agent.py

- Created `data/plants.json` with 25 plants (10 vegetables, 8 herbs, 7 flowers); each entry has watering_frequency, sun_requirements, min/max_temp_f, common_problems, planting_notes
- Rewrote `tools/weather.py`: `get_current_weather` (temp, humidity, rainfall, wind, UV index via OWM) + `get_forecast` (5-day with rain probability, aggregated from 3-hour intervals)
- Rewrote `tools/frost.py`: `get_frost_dates` using hardcoded USDA city-level data (~60 US cities) with fuzzy partial matching
- Rewrote `tools/plants.py`: `lookup_plant_care` with exact key + common_name fallback matching
- Rewrote `tools/profile.py`: `get_garden_profile` + `update_garden_profile` with merge-on-update behavior
- Updated `tools/__init__.py` to export all 6 canonical function names
- Rewrote `agent.py`: full Groq tool-use loop (llama-3.3-70b-versatile), 6 tool schemas, `_call_tool` dispatcher, multi-turn `run_agent`, CLI entry point

## [2026-05-04] — Added README.md, DEVLOG.md, EVALS.md

- Created `README.md` skeleton with 9 sections (overview through what's next)
- Created `DEVLOG.md` with intro and example dated entry format
- Created `EVALS.md` skeleton with overview, categories, run instructions, and results table

## [2026-05-04] — Added ROADMAP.md

- Created `ROADMAP.md` with 6 phases and all checklist items (Phases 1–6)

## [2026-05-04] — Project initialization

- Created `CLAUDE.md` with project overview, architecture, conventions, and commands
- Created `CHANGELOG.md` with update convention
