from app.models.schemas import QueryIntent, QueryRoutingDecision


class QueryRouter:
    # very simple keyword based router
    def classify(self, text: str) -> QueryRoutingDecision:
        normalized = text.lower()
        intent, confidence = self._heuristic_intent(normalized)
        suggested_endpoint = self._suggest_endpoint(intent)
        params = {}

        return QueryRoutingDecision(
            intent=intent,
            confidence=confidence,
            suggested_endpoint=suggested_endpoint,
            parameters=params,
        )

    def _heuristic_intent(self, text: str):
        if any(word in text for word in ["intervention", "at-risk", "risk", "support"]):
            return QueryIntent.INTERVENTION_ANALYSIS, 0.85

        if any(word in text for word in ["trend", "over time", "improve", "decline"]):
            return QueryIntent.PERFORMANCE_TRENDS, 0.8

        if any(word in text for word in ["attendance", "present", "absent", "participation"]):
            return QueryIntent.ATTENDANCE_SUMMARY, 0.8

        return QueryIntent.UNKNOWN, 0.3

    @staticmethod
    def _suggest_endpoint(intent: QueryIntent):
        if intent == QueryIntent.INTERVENTION_ANALYSIS:
            return "/analyze/intervention"
        if intent in {QueryIntent.ATTENDANCE_SUMMARY, QueryIntent.PERFORMANCE_TRENDS}:
            return "/analyze/trends"
        return None


query_router = QueryRouter()

