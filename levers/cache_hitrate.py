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


def percentile(values, percentile_value):
    if not values:
        return 0

    values = sorted(values)

    index = int(round((percentile_value / 100) * (len(values) - 1)))

    return values[index]


def clear_cache(headers):
    response = requests.post(
        f"{BASE_URL}/cache/clear",
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()


def get_cache_stats(headers):
    response = requests.get(
        f"{BASE_URL}/cache/stats",
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def run_cache_test():

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    fixtures = load_fixtures()

    # Start from a clean cache
    clear_cache(headers)

    latencies_ms = []

    total_cost = 0.0

    hits = 0
    misses = 0

    successful_requests = 0

    print()
    print("=" * 75)
    print("CACHE HIT-RATE TEST")
    print("=" * 75)

    # ------------------------------------------------
    # Run the same fixture set twice
    # ------------------------------------------------
    #
    # Round 1:
    # expected mostly/all MISS
    #
    # Round 2:
    # expected mostly/all HIT
    #
    # ------------------------------------------------

    for round_number in range(1, 3):

        print()
        print(f"ROUND {round_number}")

        print("-" * 75)

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

                continue

            result = response.json()

            cache_status = result["cache_status"]

            usage = result["usage"]

            if cache_status == "HIT":
                hits += 1

            elif cache_status == "MISS":
                misses += 1

            total_cost += usage["estimated_cost_usd"]

            latencies_ms.append(latency_ms)

            successful_requests += 1

            print(
                f"{fixture['patient_id']} | "
                f"{cache_status:4} | "
                f"{latency_ms:8.2f} ms | "
                f"${usage['estimated_cost_usd']:.8f}"
            )

    # ------------------------------------------------
    # SUMMARY
    # ------------------------------------------------

    total_requests = hits + misses

    if total_requests == 0:
        hit_rate = 0
    else:
        hit_rate = (hits / total_requests) * 100

    average_latency = statistics.mean(latencies_ms)

    p95_latency = percentile(
        latencies_ms,
        95,
    )

    average_cost = total_cost / successful_requests

    estimated_cost_per_1000 = average_cost * 1000

    api_cache_stats = get_cache_stats(headers)

    print()
    print("=" * 75)
    print("CACHE TEST SUMMARY")
    print("=" * 75)

    print(f"Successful requests: " f"{successful_requests}")

    print(f"Cache hits: " f"{hits}")

    print(f"Cache misses: " f"{misses}")

    print(f"Hit rate: " f"{hit_rate:.2f}%")

    print()

    print(f"Average latency: " f"{average_latency:.2f} ms")

    print(f"p95 latency: " f"{p95_latency:.2f} ms")

    print()

    print(f"Estimated total LLM cost: " f"${total_cost:.8f}")

    print(f"Average estimated LLM cost/request: " f"${average_cost:.8f}")

    print(f"Estimated LLM cost/1,000 requests: " f"${estimated_cost_per_1000:.6f}")

    print()

    print("API cache stats:")

    print(
        json.dumps(
            api_cache_stats,
            indent=2,
        )
    )

    print()
    print("NOTE: LLM costs are estimated because " "USE_STUB_LLM=true.")


if __name__ == "__main__":
    run_cache_test()
