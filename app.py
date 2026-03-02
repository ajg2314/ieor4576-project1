import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT
from vertex_client import generate_answer
from guardrails import apply_backstop

load_dotenv()

app = FastAPI(title="Probability Domain Chatbot")

class ChatIn(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
def chat(payload: ChatIn):
    question = payload.question.strip()

    full_prompt = (
        SYSTEM_PROMPT
        + "\n\nUser question:\n"
        + question
        + "\n\nAnswer:"
    )

    try:
        answer = generate_answer(full_prompt)
    except Exception as e:
        # If Vertex call fails, return a controlled error (still better than crashing).
        answer = f"Error calling Vertex AI: {type(e).__name__}: {e}"

    answer = apply_backstop(question, answer)
    return {"answer": answer}