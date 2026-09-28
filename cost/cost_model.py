from dataclasses import dataclass

# GPT-4o mini pricing used in this capstone:
# Input:  $0.15 / 1M tokens
# Output: $0.60 / 1M tokens


@dataclass
class CostScenario:
    name: str

    monthly_requests: int

    avg_input_tokens: int

    avg_output_tokens: int

    input_price_per_million: float

    output_price_per_million: float

    monthly_infrastructure_cost: float

    monthly_ops_cost: float


def token_cost(
    token_count: int,
    price_per_million: float,
) -> float:

    return (token_count / 1_000_000) * price_per_million


def calculate_scenario(
    scenario: CostScenario,
):

    input_cost_per_request = token_cost(
        scenario.avg_input_tokens,
        scenario.input_price_per_million,
    )

    output_cost_per_request = token_cost(
        scenario.avg_output_tokens,
        scenario.output_price_per_million,
    )

    llm_cost_per_request = input_cost_per_request + output_cost_per_request

    infrastructure_cost_per_request = (
        scenario.monthly_infrastructure_cost / scenario.monthly_requests
    )

    ops_cost_per_request = scenario.monthly_ops_cost / scenario.monthly_requests

    total_cost_per_request = (
        llm_cost_per_request + infrastructure_cost_per_request + ops_cost_per_request
    )

    total_cost_per_1000 = total_cost_per_request * 1000

    monthly_total = total_cost_per_request * scenario.monthly_requests

    return {
        "llm_cost_per_request": llm_cost_per_request,
        "infra_cost_per_request": infrastructure_cost_per_request,
        "ops_cost_per_request": ops_cost_per_request,
        "total_cost_per_request": total_cost_per_request,
        "cost_per_1000": total_cost_per_1000,
        "monthly_total": monthly_total,
    }


def print_report(
    scenario: CostScenario,
):

    results = calculate_scenario(scenario)

    print()
    print("=" * 60)

    print(scenario.name)

    print("=" * 60)

    print(f"Monthly requests: " f"{scenario.monthly_requests:,}")

    print(f"Average input tokens/request: " f"{scenario.avg_input_tokens}")

    print(f"Average output tokens/request: " f"{scenario.avg_output_tokens}")

    print()

    print("LLM cost/request: " f"${results['llm_cost_per_request']:.6f}")

    print("Infrastructure cost/request: " f"${results['infra_cost_per_request']:.6f}")

    print("Operations cost/request: " f"${results['ops_cost_per_request']:.6f}")

    print("-" * 60)

    print("TOTAL cost/request: " f"${results['total_cost_per_request']:.6f}")

    print("TOTAL cost/1,000 requests: " f"${results['cost_per_1000']:.4f}")

    print("Estimated monthly total: " f"${results['monthly_total']:.2f}")


def main():

    # -----------------------------------
    # BASELINE
    # -----------------------------------

    baseline = CostScenario(
        name="BASELINE",
        monthly_requests=10_000,
        avg_input_tokens=500,
        avg_output_tokens=150,
        input_price_per_million=0.15,
        output_price_per_million=0.60,
        monthly_infrastructure_cost=15.00,
        monthly_ops_cost=20.00,
    )

    # -----------------------------------
    # 10X TRAFFIC SPIKE
    # -----------------------------------

    spike = CostScenario(
        name="10X TRAFFIC SPIKE",
        monthly_requests=100_000,
        avg_input_tokens=500,
        avg_output_tokens=150,
        input_price_per_million=0.15,
        output_price_per_million=0.60,
        # Assume infrastructure must scale
        # during the spike.
        monthly_infrastructure_cost=45.00,
        monthly_ops_cost=30.00,
    )

    print_report(baseline)

    print_report(spike)


if __name__ == "__main__":
    main()
