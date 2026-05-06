# GardenMind Dev Log

A running log of engineering decisions, tradeoffs, and lessons learned throughout the build.

---

## [2026-05-04] — Used city-level frost lookup instead of USDA hardiness zones

**Decision:** `get_frost_dates` accepts a city name (e.g. "Denver") and looks it up in a hardcoded dict of ~60 US cities, with partial-match fallback.

**Why:** The spec said "hardcoded USDA data for common US cities." A zone-based approach (zone_5, zone_6) would require users to already know their zone, which breaks the conversational UX. The agent already has the user's location from their profile — it should be able to pass that directly.

**Learned:** Partial matching (checking if the query is a substring of the city key) handles "New York City" → "new york" and "Portland OR" → "portland or" cleanly without any fuzzy library dependency.

---

## [2026-05-04] — Agent loop lives in the UI, not called via run_agent

**Decision:** `ui/app.py` runs the Groq tool-use loop itself (importing `SYSTEM_PROMPT`, `TOOLS`, `MODEL`, `_call_tool` from `agent.py`) rather than calling `run_agent()`.

**Why:** `run_agent` is blocking — it runs all tool calls internally and returns a string. Streamlit needs to update the UI between each tool call to show them in real time via `st.status`. The only way to do that is to control the loop directly and call `status.update()` after each tool execution.

**Learned:** `st.status` (added Streamlit 1.28) is the right primitive here — it shows a live-updating label during the loop, then collapses to a "Done" state. Intermediate assistant messages (the ones containing `tool_calls` with `content=None`) must be filtered out of the replay loop or the chat history renders blank assistant bubbles.

---

## [2026-05-04] — Groq tool loop over Anthropic SDK

**Decision:** Rewrote `agent.py` from Anthropic SDK to Groq SDK with `llama-3.3-70b-versatile`.

**Why:** The spec calls for Groq explicitly. The existing stub used `Anthropic()` with no actual tool dispatch — it was a placeholder. Groq uses the OpenAI-compatible chat completions format, so tool schemas and the message loop follow the same pattern.

**Learned:** Groq requires the full `tool_calls` array to be echoed back in the assistant message when recording history, otherwise the next API call fails with a validation error. The assistant turn must include both `content` and `tool_calls` fields.

---

## [2026-05-04] — Example entry format

**Decision:** _What did you decide to do?_

**Why:** _What motivated this choice? What alternatives did you consider?_

**Learned:** _What did you discover in the process? What would you do differently?_

---
