# GPT-4o mini documented pricing used for the API-hosted scenario:
# Input:  $0.15 per 1M tokens
# Output: $0.60 per 1M tokens


def api_monthly_cost(
    monthly_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> float:

    input_cost = (
        monthly_requests * avg_input_tokens / 1_000_000 * input_price_per_million
    )

    output_cost = (
        monthly_requests * avg_output_tokens / 1_000_000 * output_price_per_million
    )

    return input_cost + output_cost


def self_host_monthly_cost(
    gpu_cost: float,
    infrastructure_cost: float,
    ops_cost: float,
) -> float:

    return gpu_cost + infrastructure_cost + ops_cost


def find_break_even(
    avg_input_tokens: int,
    avg_output_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
    self_host_cost: float,
):

    cost_per_request = (avg_input_tokens / 1_000_000 * input_price_per_million) + (
        avg_output_tokens / 1_000_000 * output_price_per_million
    )

    if cost_per_request == 0:
        return None

    return self_host_cost / cost_per_request


def main():

    # ----------------------------------
    # API ASSUMPTIONS
    # ----------------------------------

    avg_input_tokens = 500
    avg_output_tokens = 150

    # Example classroom assumptions.
    # Replace with documented provider rates
    # before final submission.

    input_price_per_million = 0.15
    output_price_per_million = 0.60

    # ----------------------------------
    # SELF-HOST ASSUMPTIONS
    # ----------------------------------

    # Example estimates only.
    # These are not measured cloud prices.

    gpu_monthly_cost = 300.00

    supporting_infrastructure = 50.00

    operations_cost = 100.00

    self_host_total = self_host_monthly_cost(
        gpu_monthly_cost,
        supporting_infrastructure,
        operations_cost,
    )

    print()
    print("=" * 70)
    print("API VS SELF-HOST COST SENSITIVITY")
    print("=" * 70)

    print(f"Estimated self-host monthly cost: " f"${self_host_total:.2f}")

    print()

    request_levels = [
        10_000,
        100_000,
        500_000,
        1_000_000,
        5_000_000,
    ]

    print(
        f"{'Requests/month':>15} | " f"{'API token cost':>15} | " f"{'Self-host':>12}"
    )

    print("-" * 50)

    for monthly_requests in request_levels:

        api_cost = api_monthly_cost(
            monthly_requests,
            avg_input_tokens,
            avg_output_tokens,
            input_price_per_million,
            output_price_per_million,
        )

        print(
            f"{monthly_requests:>15,} | "
            f"${api_cost:>14.2f} | "
            f"${self_host_total:>11.2f}"
        )

    break_even_requests = find_break_even(
        avg_input_tokens,
        avg_output_tokens,
        input_price_per_million,
        output_price_per_million,
        self_host_total,
    )

    print()
    print("-" * 70)

    print(
        f"Estimated token-cost break-even volume: "
        f"{break_even_requests:,.0f} requests/month"
    )

    print()

    print(
        "IMPORTANT: This compares API token cost "
        "against estimated self-host monthly cost."
    )

    print(
        "It does not prove that self-hosting becomes "
        "the better architecture at the break-even point."
    )

    print(
        "Quality, reliability, staffing, GPU utilisation, "
        "security, and operational complexity also matter."
    )


if __name__ == "__main__":
    main()
