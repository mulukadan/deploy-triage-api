import json
import statistics
import time
from pathlib import Path

import requests

BASE_URL = "http://127.0.0.1:8000"

USERNAME = "mercy"
PASSWORD = "afyaplus123"

FIXTURE_FILE = Path("fixtures/triage_requests.json")


def get_token():
    """
    Log in to the API and return a JWT token.
    """

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
    """
    Load our fixed triage test requests.
    """

    with open(
        FIXTURE_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def percentile(values, percentile_value):
    """
    Simple percentile calculator.

    Example:
    percentile(values, 95)
    gives us approximately p95 latency.
    """

    if not values:
        return 0

    values = sorted(values)

    index = int(round((percentile_value / 100) * (len(values) - 1)))

    return values[index]


def run_baseline():
    token = get_token()

    fixtures = load_fixtures()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    latencies_ms = []

    total_input_tokens = 0
    total_output_tokens = 0
    total_estimated_llm_cost = 0.0

    successful_requests = 0

    print()
    print("=" * 70)
    print("BASELINE TRIAGE MEASUREMENT")
    print("=" * 70)

    for number, fixture in enumerate(
        fixtures,
        start=1,
    ):

        start_time = time.perf_counter()

        response = requests.post(
            f"{BASE_URL}/triage",
            headers=headers,
            json=fixture,
            timeout=30,
        )

        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        if response.status_code != 200:
            print(f"Request {number}: FAILED " f"HTTP {response.status_code}")
            print(response.text)
            continue

        result = response.json()

        usage = result["usage"]

        latencies_ms.append(latency_ms)

        total_input_tokens += usage["input_tokens"]

        total_output_tokens += usage["output_tokens"]

        total_estimated_llm_cost += usage["estimated_cost_usd"]

        successful_requests += 1

        print(
            f"Request {number:02d} | "
            f"{fixture['patient_id']} | "
            f"{result['urgency']:9} | "
            f"{latency_ms:8.2f} ms | "
            f"${usage['estimated_cost_usd']:.8f}"
        )

    if successful_requests == 0:
        print()
        print("No successful requests.")
        return

    average_latency = statistics.mean(latencies_ms)

    p95_latency = percentile(
        latencies_ms,
        95,
    )

    average_llm_cost = total_estimated_llm_cost / successful_requests

    estimated_llm_cost_per_1000 = average_llm_cost * 1000

    print()
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)

    print(f"Successful requests: " f"{successful_requests}")

    print(f"Total input tokens: " f"{total_input_tokens}")

    print(f"Total output tokens: " f"{total_output_tokens}")

    print(f"Average latency: " f"{average_latency:.2f} ms")

    print(f"p95 latency: " f"{p95_latency:.2f} ms")

    print(f"Estimated LLM cost for fixture set: " f"${total_estimated_llm_cost:.8f}")

    print(f"Average estimated LLM cost/request: " f"${average_llm_cost:.8f}")

    print(f"Estimated LLM cost/1,000 requests: " f"${estimated_llm_cost_per_1000:.6f}")

    print()
    print(
        "NOTE: These LLM token/cost numbers are " "estimated because USE_STUB_LLM=true."
    )


if __name__ == "__main__":
    run_baseline()
