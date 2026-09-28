import json
import statistics
import time
from pathlib import Path

import requests

BASE_URL = "http://127.0.0.1:8000"

USERNAME = "mercy"
PASSWORD = "afyaplus123"

FIXTURE_FILE = Path("fixtures/triage_requests.json")

BATCH_SIZE = 5


def get_token():

    response = requests.post(
        f"{BASE_URL}/token",
        data={
            "username": USERNAME,
            "password": PASSWORD,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def load_fixtures():

    with open(
        FIXTURE_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def clear_cache(headers):

    response = requests.post(
        f"{BASE_URL}/cache/clear",
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()


def create_batches(
    fixtures,
    batch_size,
):

    return [
        fixtures[i : i + batch_size]
        for i in range(
            0,
            len(fixtures),
            batch_size,
        )
    ]


def run_individual_test(
    fixtures,
    headers,
):

    clear_cache(headers)

    latencies = []

    total_cost = 0.0

    start_all = time.perf_counter()

    for fixture in fixtures:

        start = time.perf_counter()

        response = requests.post(
            f"{BASE_URL}/triage",
            headers=headers,
            json=fixture,
            timeout=30,
        )

        end = time.perf_counter()

        response.raise_for_status()

        result = response.json()

        latency_ms = (end - start) * 1000

        latencies.append(latency_ms)

        total_cost += result["usage"]["estimated_cost_usd"]

    end_all = time.perf_counter()

    total_wall_time_ms = (end_all - start_all) * 1000

    return {
        "http_requests": len(fixtures),
        "patient_requests": len(fixtures),
        "total_wall_time_ms": total_wall_time_ms,
        "average_patient_time_ms": total_wall_time_ms / len(fixtures),
        "average_http_latency_ms": statistics.mean(latencies),
        "llm_cost": total_cost,
    }


def run_batch_test(
    fixtures,
    headers,
):

    clear_cache(headers)

    batches = create_batches(
        fixtures,
        BATCH_SIZE,
    )

    batch_latencies = []

    total_cost = 0.0

    processed = 0

    start_all = time.perf_counter()

    for batch in batches:

        payload = {"requests": batch}

        start = time.perf_counter()

        response = requests.post(
            f"{BASE_URL}/triage/batch",
            headers=headers,
            json=payload,
            timeout=30,
        )

        end = time.perf_counter()

        response.raise_for_status()

        result = response.json()

        latency_ms = (end - start) * 1000

        batch_latencies.append(latency_ms)

        for triage_result in result["results"]:

            total_cost += triage_result["usage"]["estimated_cost_usd"]

            processed += 1

    end_all = time.perf_counter()

    total_wall_time_ms = (end_all - start_all) * 1000

    return {
        "http_requests": len(batches),
        "patient_requests": processed,
        "total_wall_time_ms": total_wall_time_ms,
        "average_patient_time_ms": total_wall_time_ms / processed,
        "average_batch_latency_ms": statistics.mean(batch_latencies),
        "llm_cost": total_cost,
    }


def percentage_change(
    before,
    after,
):

    return ((after - before) / before) * 100


def main():

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    fixtures = load_fixtures()

    print()
    print("=" * 72)
    print("INDIVIDUAL VS BATCH API TEST")
    print("=" * 72)

    individual = run_individual_test(
        fixtures,
        headers,
    )

    batch = run_batch_test(
        fixtures,
        headers,
    )

    time_change = percentage_change(
        individual["total_wall_time_ms"],
        batch["total_wall_time_ms"],
    )

    print()
    print("INDIVIDUAL REQUESTS")
    print("-" * 72)

    print(f"Patient requests: " f"{individual['patient_requests']}")

    print(f"HTTP requests: " f"{individual['http_requests']}")

    print(f"Total wall time: " f"{individual['total_wall_time_ms']:.2f} ms")

    print(f"Average time/patient: " f"{individual['average_patient_time_ms']:.2f} ms")

    print(f"Estimated LLM cost: " f"${individual['llm_cost']:.8f}")

    print()

    print("BATCH REQUESTS")
    print("-" * 72)

    print(f"Patient requests: " f"{batch['patient_requests']}")

    print(f"HTTP requests: " f"{batch['http_requests']}")

    print(f"Batch size: " f"{BATCH_SIZE}")

    print(f"Total wall time: " f"{batch['total_wall_time_ms']:.2f} ms")

    print(f"Average time/patient: " f"{batch['average_patient_time_ms']:.2f} ms")

    print(f"Estimated LLM cost: " f"${batch['llm_cost']:.8f}")

    print()

    print("=" * 72)
    print("COMPARISON")
    print("=" * 72)

    print(
        f"HTTP requests reduced: "
        f"{individual['http_requests']} "
        f"-> {batch['http_requests']}"
    )

    print(f"Wall-time change: " f"{time_change:.2f}%")

    print(f"Individual estimated LLM cost: " f"${individual['llm_cost']:.8f}")

    print(f"Batch estimated LLM cost: " f"${batch['llm_cost']:.8f}")

    print()
    print("Interpretation:")

    print(
        "Batching reduces HTTP request overhead "
        "and can improve throughput. "
        "It does not reduce token cost in this "
        "implementation because each patient is "
        "still processed individually by the model."
    )


if __name__ == "__main__":
    main()
