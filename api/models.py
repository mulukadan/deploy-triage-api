from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    patient_id: str = Field(
        ...,
        examples=["P001"],
    )

    symptoms: str = Field(
        ...,
        min_length=3,
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
    )


class UsageInfo(BaseModel):
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


class TriageResponse(BaseModel):
    patient_id: str

    urgency: str

    advice: str

    model_used: str

    cache_status: str

    usage: UsageInfo


from typing import List


class BatchTriageRequest(BaseModel):
    requests: List[TriageRequest]


class BatchTriageResponse(BaseModel):
    results: List[TriageResponse]
    batch_size: int
