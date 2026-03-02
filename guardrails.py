REFUSAL = (
    "Out of scope: I can only help with foundational undergraduate probability "
    "(definitions, basic rules, common discrete distributions, conditional probability/expectation, "
    "LLN/CLT statements)."
)

# Simple keyword-based backstop (required by the assignment spec)
OUT_OF_SCOPE_KEYWORDS = {
    "finance": ["stock", "stocks", "invest", "investment", "options", "crypto", "bitcoin", "trading"],
    "medical": ["diagnose", "symptom", "treatment", "medication", "dose", "dosage", "disease"],
    "legal": ["lawsuit", "illegal", "contract", "attorney", "lawyer", "legal advice"],
    "self_harm": ["suicide", "kill myself", "self harm", "self-harm"],
    "measure_theory": ["radon", "nikodym", "ito", "stochastic calculus", "filtration", "brownian motion"],
    "statistics": ["p-value", "confidence interval", "regression", "hypothesis test", "bayesian inference"],
}

def should_refuse(question: str) -> bool:
    q = question.lower()
    for _, kws in OUT_OF_SCOPE_KEYWORDS.items():
        if any(kw in q for kw in kws):
            return True
    return False

def apply_backstop(question: str, answer: str) -> str:
    # If question triggers out-of-scope, override whatever the model said.
    if should_refuse(question):
        return REFUSAL
    return answer