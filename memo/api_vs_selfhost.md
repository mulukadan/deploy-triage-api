# AfyaPlus Architecture Trade-off Memo
## API-Hosted LLM vs Self-Hosted Open-Source Model

## Executive Summary

AfyaPlus currently favors an API-hosted language model for the triage workload.

The main reasons are low current traffic, simpler operations, lower infrastructure complexity, and the ability to pay mainly for model usage rather than maintain dedicated GPU infrastructure.

Self-hosting may become economically interesting at much higher sustained request volumes, but cost alone is not sufficient to justify migration.

This memo uses explicit assumptions and estimates. The self-host values have not been measured on a live production GPU deployment.

---

# Workload Assumptions

The current cost model assumes:

- 10,000 requests per month at baseline
- 100,000 requests per month during a 10x traffic scenario
- 500 average input tokens per request
- 150 average output tokens per request

The API-hosted cost model uses GPT-4o mini pricing:

- Input tokens: $0.15 per 1 million tokens
- Output tokens: $0.60 per 1 million tokens

These rates are used consistently across the AfyaPlus cost model, sensitivity analysis, and break-even calculation.
These rates are modelling assumptions and should be replaced with the documented rates for the final model/provider before production use.

---

# Option 1: API-Hosted Model

Examples include commercial hosted LLM APIs.

## Advantages

- No GPU infrastructure to manage
- Easy horizontal application scaling
- Pay-per-use pricing
- Low operational burden
- Faster development and deployment
- Provider manages model serving infrastructure
- Suitable for low or variable traffic

## Disadvantages

- Usage cost increases with token volume
- Dependency on an external provider
- Internet connectivity is required
- Provider rate limits may apply
- Less control over model infrastructure
- Pricing may change

---

# Option 2: Self-Hosted Open-Source Model

A self-hosted architecture would run an open-source model on owned or rented GPU infrastructure.

## Advantages

- Greater control over model hosting
- Potentially predictable infrastructure cost
- Can reduce dependency on an external inference provider
- More control over deployment location and model lifecycle
- May become cost-effective at high sustained utilisation

## Disadvantages

- GPU infrastructure is expensive
- Requires deployment and monitoring expertise
- Requires capacity planning
- Requires security patching and maintenance
- Requires model serving infrastructure
- Idle GPU capacity still costs money
- Scaling traffic spikes becomes the team's responsibility
- Model quality may differ from the API-hosted model

---

# Cost Comparison

For the sensitivity model, estimated self-host monthly cost is:

| Component | Monthly Estimate |
|---|---:|
| GPU compute | $300 |
| Supporting infrastructure | $50 |
| Operations | $100 |
| Total | $450 |

These numbers are illustrative estimates, not measured production costs.

The API token cost model uses:

- 500 input tokens/request
- 150 output tokens/request
- $0.15 per million input tokens
- $0.60 per million output tokens

The resulting estimated API token cost is approximately:

$0.000165 per request

---

# Volume Sensitivity

| Requests/month | Estimated API token cost | Estimated self-host cost |
|---:|---:|---:|
| 10,000 | $1.65 | $450 |
| 100,000 | $16.50 | $450 |
| 500,000 | $82.50 | $450 |
| 1,000,000 | $165.00 | $450 |
| 5,000,000 | $825.00 | $450 |

The token-cost break-even point under these assumptions is approximately:

2.73 million requests per month

This is only a cost-model crossover point. It does not automatically mean self-hosting becomes the better architecture at that volume.

---

# Other Costs Not Captured by Token Pricing

API token cost is not the full cost of an API-hosted system.

The production architecture may also require:

- application hosting
- cache infrastructure
- monitoring
- networking
- logs
- engineering operations

Similarly, the self-host estimate may require additional costs such as:

- GPU redundancy
- backups
- observability
- autoscaling
- failover
- model storage
- maintenance time
- engineering support

Therefore the break-even estimate should be treated as directional rather than exact.

---

# Reliability and Scaling

## API-Hosted

The model provider manages inference infrastructure.

AfyaPlus mainly needs to scale:

- FastAPI instances
- cache capacity
- application infrastructure

This reduces operational complexity.

## Self-Hosted

AfyaPlus would also need to manage:

- GPU capacity
- inference server replicas
- model loading
- failover
- GPU monitoring
- traffic spikes

This increases infrastructure and operational responsibility.

---

# Quality Considerations

The API-hosted and self-hosted models may not provide equal answer quality.

Before migration, AfyaPlus would need to evaluate both models using the same clinical fixture set.

Metrics should include:

- safety
- triage correctness
- consistency
- latency
- failure rate

A cheaper model should not be selected if it materially reduces triage quality or safety.

---

# Decision

For the current AfyaPlus capstone workload, the preferred deployment architecture is API-hosted inference.

This is based on the current low-volume workload and the operational simplicity of hosted inference.

Self-hosting should be reconsidered if:

- monthly traffic grows substantially
- API token costs approach infrastructure cost
- sustained GPU utilisation becomes high enough
- data residency requirements change
- provider reliability becomes unacceptable
- model quality from an open-source alternative becomes sufficient

The break-even estimate should be recalculated using real measured infrastructure and provider pricing before any production migration.