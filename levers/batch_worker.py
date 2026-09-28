from dataclasses import dataclass
from typing import List

from api.llm_service import assess_symptoms


@dataclass
class BatchItem:
    patient_id: str
    symptoms: str
    age: int


@dataclass
class BatchResult:
    patient_id: str
    urgency: str
    advice: str
    model_used: str


def process_batch(
    items: List[BatchItem],
) -> List[BatchResult]:
    """
    Process multiple triage requests as one batch workload.

    This is a simple local batching demonstration.

    In a production system, this queue could be processed
    by Celery, Redis Queue, Kafka consumers, cloud queues,
    or a provider-specific batch inference service.
    """

    results = []

    for item in items:

        result = assess_symptoms(
            symptoms=item.symptoms,
            age=item.age,
        )

        results.append(
            BatchResult(
                patient_id=item.patient_id,
                urgency=result["urgency"],
                advice=result["advice"],
                model_used=result["model_used"],
            )
        )

    return results
