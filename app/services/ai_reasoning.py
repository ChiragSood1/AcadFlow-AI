from app.core.config import settings
from app.models.schemas import StudentInterventionRecommendation
from openai import OpenAI


class AIReasoningService:
    # simple helper that creates text explanations
    def __init__(self):
        pass

    async def recommend_interventions(self, risk_records):
        # if no students, return empty list
        if not risk_records:
            return []

        recommendations = []

        # go student by student
        for record in risk_records:
            # if no API key, use a very simple text instead of calling the API
            if not settings.ai.api_key:
                if record.risk_band == record.risk_band.HIGH:
                    ai_text = "Meet the student and talk about attendance and marks. Make a simple support plan."
                elif record.risk_band == record.risk_band.MEDIUM:
                    ai_text = "Invite the student to extra help sessions and keep an eye on their progress."
                else:
                    ai_text = "Give the student positive feedback and encourage them to stay consistent."
            else:
                # build prompt for THIS student
                prompt = f"""
You are an academic advisor.

Student ID: {record.student_id}
Subject: {record.subject_code}
Risk level: {record.risk_band}

Do NOT calculate anything.
Do NOT change the risk level.

Generate:
1. A short recommendation (1–2 sentences)
2. A short reason (1 sentence)

Keep it practical and professional.
"""

                try:
                    client = OpenAI(api_key=settings.ai.api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an academic advisor."},
                            {"role": "user", "content": prompt},
                        ],
                    )
                    ai_text = response.choices[0].message.content.strip()
                except Exception:
                    # fallback if AI fails
                    ai_text = "Meet the student and provide basic academic support."

            # create response object
            recommendations.append(
                StudentInterventionRecommendation(
                    student_id=record.student_id,
                    subject_code=record.subject_code,
                    risk_band=record.risk_band,
                    recommendation=ai_text,
                    rationale="Generated using AI based on risk level.",
                )
            )

        return recommendations

    async def summarize_trends(self, trend_points):
        if not trend_points:
            return "No attendance data is available for the requested period."

        total = 0.0
        for tp in trend_points:
            total += tp.average_attendance_percentage

        avg = total / len(trend_points)

        return f"Average attendance across the selected period is around {avg:.1f}%."


# single shared instance
ai_reasoning_service = AIReasoningService()