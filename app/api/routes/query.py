from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_router import query_router
from app.api.routes.analyze import analyze_intervention, analyze_trends
from app.models.schemas import InterventionAnalysisRequest, TrendsAnalysisRequest

router = APIRouter()


@router.post(
    "",
    response_model=QueryResponse,
    summary="Classify a natural-language query and route it to the appropriate logic.",
)
async def handle_query(
    request: QueryRequest,
    store=Depends(get_store),
):
    # classify the text from the user
    routing = query_router.classify(request.query)

    # we can fill this when we run another endpoint
    analysis_result = None

    # run intervention analysis automatically
    if routing.intent.name == "INTERVENTION_ANALYSIS":
        intervention_request = InterventionAnalysisRequest()
        intervention_result = await analyze_intervention(intervention_request, store=store)
        analysis_result = intervention_result.model_dump()
    # run trends analysis automatically for attendance/performance questions
    elif routing.intent.name == "ATTENDANCE_SUMMARY" or routing.intent.name == "PERFORMANCE_TRENDS":
        trends_request = TrendsAnalysisRequest()
        trends_result = await analyze_trends(trends_request, store=store)
        analysis_result = trends_result.model_dump()

    return QueryResponse(routing=routing, analysis_result=analysis_result)

