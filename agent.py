import json
import os
import re
import time

from groq import Groq, RateLimitError, BadRequestError, APIStatusError
from dotenv import load_dotenv

from tools.weather import get_current_weather, get_forecast
from tools.frost import get_frost_dates
from tools.plants import lookup_plant_care
from tools.profile import get_garden_profile, update_garden_profile

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are GardenMind, an expert gardening assistant. "
    "You give personalized, weather-aware gardening advice based on the user's "
    "location, what they're growing, and real-time conditions. "
    "Use your tools to look up weather, frost dates, plant care info, and the "
    "user's garden profile before answering. Always be specific and practical. "
    "If lookup_plant_care returns an error, you MUST begin your response with: "
    "'⚠️ Note: [plant name] isn't in my plant database, so the following advice "
    "is based on general knowledge and may be less accurate.' "
    "Then provide your best general advice."
)

# --- Tool schemas (Groq uses OpenAI-compatible function calling format) ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Current weather for a city: temp, humidity, rain, wind, UV index.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name, e.g. 'Denver'."},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Multi-day forecast (max 5) with high/low temps and rain probability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name."},
                    "days": {"type": "integer", "description": "Days to forecast (1-5)."},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_frost_dates",
            "description": "Average last spring and first fall frost dates for a US city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "US city name."},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_plant_care",
            "description": "Watering, sun, temp tolerances, problems, and planting notes for a plant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plant_name": {"type": "string", "description": "Common name, e.g. 'tomato'."},
                },
                "required": ["plant_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_garden_profile",
            "description": "Load a user's saved garden profile (location and plant list).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_garden_profile",
            "description": "Save or update a user's garden profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID."},
                    "updates": {"type": "object", "description": "Fields to merge, e.g. {location, plants}."},
                },
                "required": ["user_id", "updates"],
            },
        },
    },
]

# Maps tool name → callable
_TOOL_MAP = {
    "get_current_weather": get_current_weather,
    "get_forecast": get_forecast,
    "get_frost_dates": get_frost_dates,
    "lookup_plant_care": lookup_plant_care,
    "get_garden_profile": get_garden_profile,
    "update_garden_profile": update_garden_profile,
}


_MAX_RETRIES = 4
_RATE_LIMIT_BACKOFF = [20, 40, 65]  # seconds to wait on successive 429s (~1 min window reset)

# Patterns for when the model emits tool calls as raw text instead of structured calls.
# llama-3.1-8b-instant leaks two main formats:
#   1. <tool_call>{"name": ..., "arguments": ...}</tool_call>
#   2. <func_name>{"arg": "val"}</func_name>
_RAW_TOOL_RE = re.compile(
    r"<tool_call>.*?</tool_call>"
    r"|<\w[\w_]*>\s*\{.*?\}\s*</\w[\w_]*>",
    re.DOTALL,
)


def _strip_leaked_tool_syntax(text: str) -> str:
    """Remove leaked tool-call markup the model occasionally emits as plain text."""
    return _RAW_TOOL_RE.sub("", text).strip()


def _chat(client_instance, messages: list) -> object:
    """Call Groq chat completions with retry on transient errors.

    - 400 tool_use_failed: retry immediately (model is stochastic).
    - 413 request too large: drop the two oldest non-system messages and retry.
    - 429 rate limit: back off with increasing delays before retrying.
    """
    msgs = list(messages)  # local copy so trimming doesn't mutate the caller's history
    rate_limit_attempt = 0
    for attempt in range(_MAX_RETRIES):
        try:
            return client_instance.chat.completions.create(
                model=MODEL,
                messages=msgs,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=4096,
            )
        except RateLimitError:
            if rate_limit_attempt < len(_RATE_LIMIT_BACKOFF):
                wait = _RATE_LIMIT_BACKOFF[rate_limit_attempt]
                rate_limit_attempt += 1
                time.sleep(wait)
            else:
                raise
        except BadRequestError as exc:
            _retryable = ("tool_use_failed", "tool call validation failed")
            if attempt < _MAX_RETRIES - 1 and any(p in str(exc) for p in _retryable):
                continue
            raise
        except APIStatusError as exc:
            # Drop the two oldest non-system messages to shrink token count, then retry.
            if exc.status_code == 413 and len(msgs) > 3:
                msgs = [msgs[0]] + msgs[3:]
                continue
            raise
    raise RuntimeError(f"_chat: exceeded {_MAX_RETRIES} retries without a successful response")


def _call_tool(name: str, args: dict) -> str:
    """Execute a tool and return its result as a JSON string."""
    fn = _TOOL_MAP.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(**args)
    except Exception as e:
        result = {"error": str(e)}
    return json.dumps(result)


def run_agent(user_message: str, conversation_history: list) -> str:
    """
    Run one turn of the agent loop.

    Appends the user message to history, calls Groq, executes any tool calls,
    feeds results back, and returns the final text response.
    History is mutated in place so the caller can pass it across turns.
    """
    conversation_history.append({"role": "user", "content": user_message})

    xml_retries = 0
    while True:
        response = _chat(
            client,
            [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        )

        message = response.choices[0].message

        # No tool calls — we have the final answer
        if not message.tool_calls:
            reply = message.content or ""
            # Detect model emitting raw tool-call syntax instead of structured calls;
            # retry up to 2 times so it can self-correct, then strip as a fallback.
            if _RAW_TOOL_RE.search(reply):
                if xml_retries < 2:
                    xml_retries += 1
                    continue
                reply = _strip_leaked_tool_syntax(reply)
            conversation_history.append({"role": "assistant", "content": reply})
            return reply

        # Record the assistant turn that contains the tool call requests
        conversation_history.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ],
        })

        # Execute each tool and add results
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            result = _call_tool(tc.function.name, args)
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


if __name__ == "__main__":
    history = []
    print("GardenMind — type 'quit' to exit\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue
        reply = run_agent(user_input, history)
        print(f"\nGardenMind: {reply}\n")
