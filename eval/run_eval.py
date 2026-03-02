import json
import requests
from collections import defaultdict

API_URL = "http://127.0.0.1:8000/chat"

# Deterministic refusal detector: stable substring
REFUSAL_MARKER = "Out of scope:"

def call_bot(question: str) -> str:
    r = requests.post(API_URL, json={"question": question}, timeout=60)
    r.raise_for_status()
    return r.json()["answer"]

def contains_all_substrings(answer: str, substrings: list[str]) -> bool:
    a = answer.lower()
    return all(s.lower() in a for s in substrings)

def contains_expected_any(answer: str, expected_any: list[list[str]]) -> bool:
    """
    expected_any is a list of groups; each group is a list of acceptable variants.
    Pass if for every group, at least one variant appears in the answer.
    Deterministic AND-of-ORs.
    """
    a = answer.lower()
    for group in expected_any:
        if not any(var.lower() in a for var in group):
            return False
    return True

def is_refusal(answer: str) -> bool:
    return REFUSAL_MARKER.lower() in answer.lower()

def run():
    with open("eval/dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    per_cat = defaultdict(lambda: {"total": 0, "passed": 0})
    failures = []

    # Named deterministic metrics
    metrics = {
        "in_domain_keyword_coverage": {"passed": 0, "total": 0},
        "refusal_detection_accuracy": {"passed": 0, "total": 0},
    }

    for item in dataset:
        test_id = item.get("id", "")
        cat = item["category"]
        q = item["question"]

        ans = call_bot(q)

        # Deterministic pass/fail logic driven by dataset schema
        if item.get("expected_refusal", False):
            ok = is_refusal(ans)
            metrics["refusal_detection_accuracy"]["total"] += 1
            metrics["refusal_detection_accuracy"]["passed"] += int(ok)
        else:
            if "expected_any" in item:
                ok = contains_expected_any(ans, item["expected_any"])
            else:
                expected = item.get("expected_contains", [])
                ok = contains_all_substrings(ans, expected)
            metrics["in_domain_keyword_coverage"]["total"] += 1
            metrics["in_domain_keyword_coverage"]["passed"] += int(ok)

        per_cat[cat]["total"] += 1
        per_cat[cat]["passed"] += int(ok)

        print(f"[{test_id} | {cat}] PASS={ok}")
        if not ok:
            failures.append({"id": test_id, "category": cat, "question": q, "answer": ans})
            print("  Q:", q)
            print("  A:", ans[:500] + ("..." if len(ans) > 500 else ""))
        print("-" * 60)

    # Summary
    total = sum(v["total"] for v in per_cat.values())
    passed = sum(v["passed"] for v in per_cat.values())

    print("\n=== Pass rates by category ===")
    for cat, s in per_cat.items():
        rate = s["passed"] / s["total"] if s["total"] else 0.0
        print(f"{cat}: {s['passed']}/{s['total']} = {rate:.1%}")

    print("\n=== Deterministic metrics (named) ===")
    for name, s in metrics.items():
        rate = s["passed"] / s["total"] if s["total"] else 0.0
        print(f"{name}: {s['passed']}/{s['total']} = {rate:.1%}")

    print(f"\nOverall: {passed}/{total} = {passed/total:.1%}")

    # Optional: write failures to a file for debugging
    if failures:
        with open("eval/failures.json", "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)
        print("\nWrote failures to eval/failures.json")

if __name__ == "__main__":
    run()