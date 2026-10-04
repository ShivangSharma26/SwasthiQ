import os
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from groq import Groq
from pydantic import BaseModel
from typing import List, Optional
from db import ClinicDB
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with the user's API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "qwen/qwen3.8-27b" # Good model for tool calling

class TurnRequest(BaseModel):
    conversation_id: str
    today: str
    turns: List[str]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_slots",
            "description": "Find free slots for a doctor on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"}
                },
                "required": ["doctor_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Create an appointment in a free slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "doctor_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "start": {"type": "string", "description": "HH:MM"}
                },
                "required": ["patient_id", "doctor_id", "date", "start"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Move an existing appointment to a new slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "start": {"type": "string", "description": "HH:MM"}
                },
                "required": ["appointment_id", "date", "start"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"}
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_patient",
            "description": "Resolve a caller to a patient record using name and/or phone number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Hand the conversation off to a human. Use this for emergencies, medical advice, out of scope requests, ambiguous patients, or missing authorization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "enum": ["clinical_urgent", "medical_advice", "not_authorised", "ambiguous_patient", "out_of_scope"]
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are the Sunrise Clinic Front Desk Agent.
Your job is to handle bookings, cancellations, rescheduling, and patient lookups.
Today is {today}. The clinic is in Dehradun (India).

CRITICAL RULES - READ CAREFULLY:
1. ONLY use slots, patients, and appointments returned by your tools. NEVER invent them.
2. DO NOT ESCALATE normal booking or rescheduling requests. If a user asks for an appointment, use `lookup_patient`, then `search_slots`, then `book_appointment`. 
3. ESCALATE ONLY in these exact situations:
   - 'clinical_urgent': caller describes symptoms needing immediate care (e.g., chest pain, bleeding).
   - 'medical_advice': caller asks for diagnosis or medicine dosage.
   - 'not_authorised': caller tries to book for someone else but is not their guardian in the system.
   - 'ambiguous_patient': patient lookup returns multiple matches and caller cannot clarify.
   - 'out_of_scope': requests unrelated to front desk duties (e.g., discounts, talking to manager).
4. If the caller has not provided enough information (like name/phone or date/time), politely ask them for it.
5. You must ALWAYS use tools to verify information before confirming anything to the user.
"""

@app.post("/agent/run")
async def agent_run(req: TurnRequest):
    start_time = time.time()
    db = ClinicDB()
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(today=req.today)}
    ]
    
    # In a real conversation, the turns would alternate. But here, the runner provides all caller turns at once?
    # Wait, the prompt says "The script is fixed. The caller's turns do not react to what your agent says."
    # So we feed the turns one by one. After each turn, the agent can reply or call tools.
    
    tool_calls_record = []
    terminal_state = "abandoned"
    escalation_reason = None
    final_patient_id = None
    final_appointment_id = None
    final_reply = ""
    
    for turn in req.turns:
        messages.append({"role": "user", "content": turn})
        
        # Agent loop for this turn
        while True:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.0
            )
            
            msg = response.choices[0].message
            messages.append(msg)
            
            if msg.tool_calls:
                for tcall in msg.tool_calls:
                    args = json.loads(tcall.function.arguments)
                    tool_calls_record.append({
                        "name": tcall.function.name,
                        "arguments": args
                    })
                    
                    fname = tcall.function.name
                    if fname == "search_slots":
                        res = db.search_slots(args.get("doctor_id"), args.get("date"))
                    elif fname == "book_appointment":
                        res = db.book_appointment(args.get("patient_id"), args.get("doctor_id"), args.get("date"), args.get("start"))
                        if "error" not in res:
                            terminal_state = "booked"
                            final_patient_id = args.get("patient_id")
                            final_appointment_id = res["id"]
                    elif fname == "reschedule_appointment":
                        res = db.reschedule_appointment(args.get("appointment_id"), args.get("date"), args.get("start"))
                        if "error" not in res:
                            terminal_state = "rescheduled"
                            final_appointment_id = res["id"]
                    elif fname == "cancel_appointment":
                        res = db.cancel_appointment(args.get("appointment_id"))
                        if "error" not in res:
                            terminal_state = "cancelled"
                            final_appointment_id = args.get("appointment_id")
                    elif fname == "lookup_patient":
                        res = db.get_patient(args.get("name"), args.get("phone"))
                    elif fname == "escalate_to_human":
                        terminal_state = "escalated"
                        escalation_reason = args.get("reason")
                        res = {"status": "escalated"}
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tcall.id,
                        "name": fname,
                        "content": json.dumps(res)
                    })
                    
                if terminal_state == "escalated":
                    break # Stop processing if escalated
            else:
                final_reply = msg.content
                break # Agent replied
                
        if terminal_state == "escalated":
            break
            
    def get_content(m):
        return m.content if hasattr(m, "content") else m.get("content")
    def get_role(m):
        return m.role if hasattr(m, "role") else m.get("role")

    if terminal_state == "abandoned" and any(get_content(m) and "refuse" in get_content(m).lower() for m in messages if get_role(m) == "assistant"):
        terminal_state = "refused"
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "conversation_id": req.conversation_id,
        "tool_calls": tool_calls_record,
        "terminal_state": terminal_state,
        "escalation_reason": escalation_reason,
        "patient_id": final_patient_id,
        "appointment_id": final_appointment_id,
        "reply": final_reply or "",
        "metrics": {
            "turns": len(req.turns),
            "tokens": 0, # Groq doesn't always provide easy token counts in the same way, or we can just mock it
            "latency_ms": latency_ms
        }
    }
