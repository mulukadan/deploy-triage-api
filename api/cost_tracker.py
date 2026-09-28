from dataclasses import dataclass


@dataclass
class UsageRecord:
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


# ---------------------------------------------------------
# GPT-4o mini documented token rates used for this capstone:
# Input:  $0.15 per 1 million tokens
# Output: $0.60 per 1 million tokens
#
# Source: OpenAI pricing information supplied for the capstone.
# ---------------------------------------------------------

INPUT_PRICE_PER_MILLION = 0.15
OUTPUT_PRICE_PER_MILLION = 0.60


def estimate_tokens(text: str) -> int:
    """
    Very simple token approximation.

    A common rough estimate for English text is:
    approximately 4 characters per token.

    This is ONLY a development estimate.

    When using a real OpenAI response later,
    we can use the actual usage numbers returned
    by the API.
    """

    if not text:
        return 0

    estimated = len(text) // 4

    return max(1, estimated)


def calculate_token_cost(
    tokens: int,
    price_per_million: float,
) -> float:
    """
    Convert token usage into USD cost.
    """

    return (tokens / 1_000_000) * price_per_million


def calculate_usage(
    prompt_text: str,
    completion_text: str,
) -> UsageRecord:
    """
    Estimate token usage and cost for one request.
    """

    input_tokens = estimate_tokens(prompt_text)

    output_tokens = estimate_tokens(completion_text)

    input_cost = calculate_token_cost(
        input_tokens,
        INPUT_PRICE_PER_MILLION,
    )

    output_cost = calculate_token_cost(
        output_tokens,
        OUTPUT_PRICE_PER_MILLION,
    )

    total_cost = input_cost + output_cost

    return UsageRecord(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=total_cost,
    )
