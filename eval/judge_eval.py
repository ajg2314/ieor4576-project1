import json
import os
from collections import defaultdict
from dotenv import load_dotenv
from google import genai

load_dotenv()

def safe_json_loads(text: str, debug_label: str = "") -> dict:
    if not text:
        raise ValueError(f"Judge returned empty text for {debug_label}")

    # First try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first JSON object substring
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # If still failing, print raw output for debugging
        print(f"\n--- RAW JUDGE OUTPUT ({debug_label}) ---")
        print(text[:2000])
        print("--- END RAW OUTPUT ---\n")
        raise

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")

BOT_URL = "http://127.0.0.1:8000/chat"

import requests

def call_bot(question: str) -> str:
    r = requests.post(BOT_URL, json={"question": question}, timeout=60)
    r.raise_for_status()
    return r.json()["answer"]

def get_judge_client() -> genai.Client:
    return genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

JUDGE_SYSTEM = """You are a strict evaluator for a domain Q&A chatbot.
Return ONLY a JSON object (no markdown, no code fences, no extra text) with keys:
pass (boolean), score (integer 0-5), reason (string).
"""

def judge_golden(question: str, answer: str, expected: str) -> dict:
    prompt = f"""{JUDGE_SYSTEM}

GOLDEN CHECK:
Compare the assistant answer to the expected answer for correctness and completeness.
Be strict: if the answer is missing key facts, mark fail.

Question: {question}

Assistant answer:
{answer}

Expected answer:
{expected}

Return JSON now."""
    client = get_judge_client()
    resp = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config={"response_mime_type": "application/json"},
    )
    text = (resp.text or "").strip()
    return safe_json_loads(text, debug_label="golden")

def judge_rubric(question: str, answer: str, rubric: str) -> dict:
    prompt = f"""{JUDGE_SYSTEM}

RUBRIC CHECK:
Grade the assistant answer using the rubric below.
- pass=true if it meets the rubric at a solid level
- score 0-5 indicates rubric quality

Question: {question}

Assistant answer:
{answer}

Rubric:
{rubric}

Return JSON now."""
    client = get_judge_client()
    resp = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config={"response_mime_type": "application/json"},
    )
    text = (resp.text or "").strip()
    return safe_json_loads(text, debug_label="rubric")

def run():
    with open("eval/maaj_golden.json", "r", encoding="utf-8") as f:
        golden = json.load(f)
    with open("eval/maaj_rubric.json", "r", encoding="utf-8") as f:
        rubric_cases = json.load(f)

    # Run golden
    print("=== MaaJ Golden (10) ===")
    g_pass = 0
    for item in golden:
        ans = call_bot(item["question"])
        result = judge_golden(item["question"], ans, item["expected"])
        ok = bool(result["pass"])
        g_pass += int(ok)
        print(item["id"], "PASS=" + str(ok), "score=" + str(result.get("score")), "reason=" + result.get("reason",""))

    # Run rubric
    print("\n=== MaaJ Rubric (10) ===")
    r_pass = 0
    for item in rubric_cases:
        ans = call_bot(item["question"])
        result = judge_rubric(item["question"], ans, item["rubric"])
        ok = bool(result["pass"])
        r_pass += int(ok)
        print(item["id"], "PASS=" + str(ok), "score=" + str(result.get("score")), "reason=" + result.get("reason",""))

    print("\nSUMMARY")
    print(f"Golden pass: {g_pass}/{len(golden)}")
    print(f"Rubric pass: {r_pass}/{len(rubric_cases)}")

if __name__ == "__main__":
    run()