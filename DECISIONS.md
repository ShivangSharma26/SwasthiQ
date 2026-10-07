# Decisions & Trade-offs

## 1. LLM Tool Calling Engine
I chose to use **Groq** for fast inference and functional tool calling. However, smaller models occasionally struggle with strict adherence to system prompts (like returning `out_of_scope` for standard requests if prompted too strictly about constraints). 
- **Decision:** I used `qwen/qwen3.8-27b` due to availability on the provided API key. A stronger model like `gpt-4o` or `claude-3-5-sonnet` would yield more robust zero-shot compliance.

## 2. State Management & Isolation
The instructions require state isolation per request. 
- **Decision:** I instantiated the `ClinicDB` object dynamically on every API request. The `ClinicDB` reads `clinic.json` from disk. This ensures complete isolation without needing complex database transaction rollbacks.

## 3. Conversation Handling Loop
The `runner.py` sends all caller turns at once.
- **Decision:** The backend simulates a sequential conversation by appending each user turn, querying the LLM, and feeding back the tool calls until the LLM yields a text reply or reaches an escalated terminal state.

## 4. Ambiguity in `abandoned` vs `refused`
- **Decision:** The assignment implies that `refused` means the agent actively declined, whereas `abandoned` means no action was taken. I added a simple heuristic: if the terminal state was otherwise abandoned and the LLM explicitly mentioned "refuse" in its final reasoning, we mark it `refused`. Otherwise `abandoned`.
   