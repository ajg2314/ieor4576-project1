# ieor4576-project1
# Probability Domain QA Chatbot

## Overview

This project implements a **domain-restricted Q&A chatbot** focused on **foundational undergraduate probability**.

The system:
- Answers questions about core probability concepts (definitions, rules, common discrete distributions, LLN/CLT statements).
- Refuses out-of-scope or adversarial queries.
- Uses Google Cloud Vertex AI (Gemini 2.5 Flash Lite).
- Includes deterministic evaluation and MaaJ LLM-based evaluation.
- Is deployed to Google Cloud Run.

---

## Scope

The chatbot supports:

- Conditional probability
- Bayes' rule
- Linearity of expectation
- Common discrete distributions (Bernoulli, Binomial, Geometric, Poisson)
- Law of Large Numbers (LLN)
- Central Limit Theorem (CLT)
- Conditional expectation (basic definition)

It refuses:
- Continuous-time processes
- Advanced measure-theoretic probability
- Finance/medical/legal advice
- Adversarial prompt injections

---

## Project Structure
├── app.py
├── prompt.py
├── guardrails.py
├── vertex_client.py
├── eval/
│ ├── dataset.json
│ ├── run_eval.py
│ └── judge_eval.py
├── Dockerfile
├── cloudbuild.yaml
├── pyproject.toml
└── uv.lock

---

# Running Locally

## 1. Install Dependencies

This project uses `uv`.

Install uv (if needed):

pip install uv

Then install project dependencies:

uv sync


---

## 2. Set Environment Variables

Create a `.env` file:

GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-flash-lite


Make sure Vertex AI is enabled in your Google Cloud project.

---

## 3. Start the Server

uv run uvicorn app:app --reload


The app runs at:
http://127.0.0.1:8000


---

# Running Evaluation

To run all deterministic and MaaJ evaluations:
uv run python eval/run_eval.py && uv run python eval/judge_eval.py


This will print:

- Deterministic metrics
- MaaJ Golden results
- MaaJ Rubric results

---

# Deterministic Metrics

The system uses:

- Keyword coverage checks (`expected_contains`, `expected_any`)
- Refusal detection via fixed refusal marker

---

# MaaJ Evaluation

Two evaluation sets:

- Golden answers (exact match grading)
- Rubric-based evaluation (LLM-as-judge)

---

# Model

- Vertex AI
- Gemini 2.5 Flash Lite

---

# Author

IEOR 4576 — Project 1  
Andy Gu
