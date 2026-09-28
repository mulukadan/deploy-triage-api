from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.cost_tracker import calculate_usage

from api.models import (
    TriageRequest,
    TriageResponse,
    UsageInfo,
    BatchTriageRequest,
    BatchTriageResponse,
)

from api.auth import (
    authenticate_user,
    create_access_token,
    require_dispatcher,
)

from levers.cache_triage import (
    get_from_cache,
    make_cache_key,
    save_to_cache,
    get_cache_stats,
    clear_cache,
)

from api.llm_service import assess_symptoms

app = FastAPI(
    title="AfyaPlus Triage API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "afyaplus-triage",
        "version": "1.0.0",
    }


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def process_triage_request(
    request: TriageRequest,
) -> TriageResponse:

    cache_key = make_cache_key(
        symptoms=request.symptoms,
        age=request.age,
    )

    cached_result = get_from_cache(cache_key)

    # -----------------------------------
    # CACHE HIT
    # -----------------------------------

    if cached_result is not None:

        return TriageResponse(
            patient_id=request.patient_id,
            urgency=cached_result["urgency"],
            advice=cached_result["advice"],
            model_used=cached_result["model_used"],
            cache_status="HIT",
            usage=UsageInfo(
                input_tokens=0,
                output_tokens=0,
                estimated_cost_usd=0.0,
            ),
        )

    # -----------------------------------
    # CACHE MISS
    # -----------------------------------

    result = assess_symptoms(
        symptoms=request.symptoms,
        age=request.age,
    )

    prompt_text = f"Patient age: {request.age}\n" f"Symptoms: {request.symptoms}"

    completion_text = f"Urgency: {result['urgency']}\n" f"Advice: {result['advice']}"

    usage = calculate_usage(
        prompt_text=prompt_text,
        completion_text=completion_text,
    )

    cache_value = {
        "urgency": result["urgency"],
        "advice": result["advice"],
        "model_used": result["model_used"],
    }

    save_to_cache(
        cache_key,
        cache_value,
    )

    return TriageResponse(
        patient_id=request.patient_id,
        urgency=result["urgency"],
        advice=result["advice"],
        model_used=result["model_used"],
        cache_status="MISS",
        usage=UsageInfo(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            estimated_cost_usd=usage.total_cost,
        ),
    )


@app.post(
    "/triage",
    response_model=TriageResponse,
)
def triage(
    request: TriageRequest,
    current_user=Depends(require_dispatcher),
):

    return process_triage_request(request)


@app.post(
    "/triage/batch",
    response_model=BatchTriageResponse,
)
def triage_batch(
    batch: BatchTriageRequest,
    current_user=Depends(require_dispatcher),
):

    results = []

    for request in batch.requests:

        result = process_triage_request(request)

        results.append(result)

    return BatchTriageResponse(
        results=results,
        batch_size=len(results),
    )


@app.get("/cache/stats")
def cache_stats(
    current_user=Depends(require_dispatcher),
):
    return get_cache_stats()


@app.post("/cache/clear")
def reset_cache(
    current_user=Depends(require_dispatcher),
):

    clear_cache()

    return {"message": "Cache cleared"}
