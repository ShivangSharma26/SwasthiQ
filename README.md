# Clinic Front Desk Agent

This is the completed assignment for the SwasthiQ SDE Intern screening.

## Structure
- `/backend`: Python FastAPI application containing the agent loop and tools.
- `/frontend`: React (Vite) application containing the UI.
- `/adversarial`: Adversarial conversation scripts that test the agent's edge cases.
- `DECISIONS.md`: Documentation of ambiguities and design choices.

## Backend Setup & Run
1. `cd backend`
2. `python -m venv venv`
3. `.\venv\Scripts\Activate.ps1` (or `source venv/bin/activate` on Mac/Linux)
4. `pip install fastapi uvicorn groq pydantic`
5. `uvicorn main:app --host 0.0.0.0 --port 8000`

### Testing
From the root directory, run:
`python runner.py --url http://localhost:8000/agent/run`

## Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## LLM Details
- **Model Used**: `qwen/qwen3.8-27b` via Groq (Note: Groq models are rotated frequently; switch to `llama-3.1-70b-versatile` if available).
- **Latency**: ~8.4 seconds per conversation.
- **Tokens**: Tokens vary per conversation length.

## Next Steps for the User
- Review the code in `backend/main.py`.
- Run tests to see how the LLM behaves.
- Develop the React UI in `/frontend` to match the PDF mockups perfectly using Tailwind CSS.
- Record the 3-minute video requested in the assignment guidelines and submit.
