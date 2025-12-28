from typing import TypedDict

INTENTS = {
    "ANOMALY_CHECK": [
        "anomaly", "issue", "problem", "mismatch", "error", "irregular",
        "not found", "missing", "unexpected"
    ],
    "PAYMENT_QUERY": [
        "payment", "pending", "due", "invoice", "outstanding",
        "unpaid", "receivable", "overdue"
    ],
    "INVENTORY_QUERY": [
        "inventory", "stock", "warehouse", "quantity", "product",
        "items", "available", "shortage"
    ],
    "SUMMARY_REPORT": [
        "summary", "report", "overview", "status", "dashboard",
        "analytics", "insights"
    ],
    "ACTION_REQUEST": [
        "send", "notify", "alert", "email", "remind",
        "schedule", "trigger"
    ]
}


class IntentResult(TypedDict):
    intent: str
    confidence: float
    explanation: str


def classify_intent(user_text: str) -> IntentResult:
    """
    Returns:
    {
        intent: str,
        confidence: float,
        explanation: str
    }
    """

    text = user_text.lower()
    scores = {intent: 0 for intent in INTENTS}
    matched_keywords = {intent: [] for intent in INTENTS}

    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if keyword in text:
                scores[intent] += 1
                matched_keywords[intent].append(keyword)

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    if best_score == 0:
        return {
            "intent": "UNKNOWN",
            "confidence": 0.0,
            "explanation": "No ERP-specific keywords detected"
        }

    # Confidence calculation
    total_words = max(len(text.split()), 1)
    confidence = round(best_score / total_words, 2)

    explanation = (
        f"Detected intent '{best_intent}' "
        f"based on keywords: {matched_keywords[best_intent]}"
    )

    return {
        "intent": best_intent,
        "confidence": confidence,
        "explanation": explanation
    }


# Falls back to Azure AI if confidence is low
def classify_intent_with_fallback(user_text: str, ai_classifier=None) -> IntentResult:
    result = classify_intent(user_text)
    confidence = result["confidence"]

    if confidence >= 0.25 or ai_classifier is None:
        return result

    # Azure AI fallback
    ai_intent = ai_classifier(user_text)

    return {
        "intent": ai_intent,
        "confidence": 0.6,
        "explanation": "Intent determined using Azure AI fallback"
    }
