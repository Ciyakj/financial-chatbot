# utils/question_refiner.py

def is_response_poor(response: str) -> bool:
    if not response:
        return True
    response = response.strip().lower()
    if response in ["i don't know", "not found", "no data", "n/a"]:
        return True
    if len(response) < 20:
        return True
    return False

def get_refinement_suggestions():
    return [
        "Try asking about a specific year or quarter.",
        "Ask for a financial metric (e.g., revenue, profit, expenses).",
        "Mention a section from the report like 'balance sheet' or 'cash flow'.",
        "Use clearer terms or rephrase the question."
    ]
