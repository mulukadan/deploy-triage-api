# AfyaPlus Cost Model

## 1. Purpose

This cost model estimates the operating cost of the AfyaPlus triage API at baseline traffic and under a 10× traffic spike.

The model separates costs into three categories:

- LLM token cost
- Infrastructure cost
- Operations / people cost

The main unit metric is:

**Cost per 1,000 requests**

This makes the cost easier for both engineering and finance teams to understand and reproduce.

---

## 2. Workload Assumptions

The baseline workload assumes:

| Assumption | Value |
|---|---:|
| Monthly requests | 10,000 |
| Average input tokens/request | 500 |
| Average output tokens/request | 150 |
| Model | GPT-4o mini |

The 10× spike scenario assumes:

| Assumption | Value |
|---|---:|
| Monthly requests | 100,000 |
| Average input tokens/request | 500 |
| Average output tokens/request | 150 |
| Model | GPT-4o mini |

The same average token usage is used in both scenarios so the traffic-volume effect can be compared consistently.

---

## 3. GPT-4o Mini Token Pricing

The following GPT-4o mini rates are used throughout this cost model:

| Token Type | Price per 1M tokens |
|---|---:|
| Input tokens | $0.15 |
| Output tokens | $0.60 |

These rates are used consistently in:

- `api/cost_tracker.py`
- `cost/cost_model.py`
- `cost/sensitivity.py`

### Pricing source

GPT-4o mini documented pricing used for this capstone:

- Input: **$0.15 per 1 million tokens**
- Output: **$0.60 per 1 million tokens**

The pricing should be rechecked against the provider's current documentation before a production deployment because model pricing can change.

---

## 4. LLM Cost per Request

The estimated LLM cost is calculated separately for input and output tokens.

### Input token cost

500 input tokens per request:

`500 / 1,000,000 × $0.15 = $0.000075`

### Output token cost

150 output tokens per request:

`150 / 1,000,000 × $0.60 = $0.000090`

### Total LLM cost per request

`$0.000075 + $0.000090 = $0.000165`

Therefore:

**Estimated GPT-4o mini token cost per request = $0.000165**

For 1,000 requests:

`$0.000165 × 1,000 = $0.165`

Therefore:

**Estimated LLM-only cost per 1,000 requests = $0.165**

---

## 5. Baseline Scenario

The baseline assumes:

- 10,000 requests/month
- $15/month infrastructure cost
- $20/month operations cost

### Infrastructure cost per request

`$15 / 10,000 = $0.001500`

### Operations cost per request

`$20 / 10,000 = $0.002000`

### Total cost per request

`LLM + Infrastructure + Operations`

`$0.000165 + $0.001500 + $0.002000`

`= $0.003665`

### Cost per 1,000 requests

`$0.003665 × 1,000`

`= $3.665`

### Estimated monthly cost

`$0.003665 × 10,000`

`= $36.65`

### Baseline Summary

| Metric | Baseline |
|---|---:|
| Monthly requests | 10,000 |
| LLM cost/request | $0.000165 |
| Infrastructure cost/request | $0.001500 |
| Operations cost/request | $0.002000 |
| Total cost/request | $0.003665 |
| Total cost/1,000 requests | $3.665 |
| Estimated monthly total | $36.65 |

---

## 6. 10× Traffic Spike Scenario

The spike scenario assumes:

- 100,000 requests/month
- $45/month infrastructure cost
- $30/month operations cost

The infrastructure and operations costs increase, but they do not increase at the same rate as traffic.

This models the effect of spreading fixed and semi-fixed costs across more requests.

### Infrastructure cost per request

`$45 / 100,000 = $0.000450`

### Operations cost per request

`$30 / 100,000 = $0.000300`

### LLM cost per request

The average token usage per request remains unchanged, so:

`LLM cost/request = $0.000165`

### Total cost per request

`$0.000165 + $0.000450 + $0.000300`

`= $0.000915`

### Cost per 1,000 requests

`$0.000915 × 1,000`

`= $0.915`

### Estimated monthly total

`$0.000915 × 100,000`

`= $91.50`

### 10× Spike Summary

| Metric | 10× Spike |
|---|---:|
| Monthly requests | 100,000 |
| LLM cost/request | $0.000165 |
| Infrastructure cost/request | $0.000450 |
| Operations cost/request | $0.000300 |
| Total cost/request | $0.000915 |
| Total cost/1,000 requests | $0.915 |
| Estimated monthly total | $91.50 |

---

## 7. Baseline vs 10× Spike

| Metric | Baseline | 10× Spike |
|---|---:|---:|
| Monthly requests | 10,000 | 100,000 |
| Total monthly cost | $36.65 | $91.50 |
| Cost/request | $0.003665 | $0.000915 |
| Cost/1,000 requests | $3.665 | $0.915 |

The monthly cost increases from:

**$36.65 → $91.50**

However, the estimated unit cost decreases from:

**$3.665/1,000 requests → $0.915/1,000 requests**

This happens because infrastructure and operations costs are spread across a much larger number of requests.

The model therefore demonstrates an economy-of-scale effect.

---

## 8. Measured Fixture Cost vs Business Cost Model

The AfyaPlus fixture test produced an estimated LLM-only cost of:

**$0.018540 per 1,000 requests**

This figure is different from the full modeled baseline cost of:

**$3.665 per 1,000 requests**

because they measure different things.

### Fixture measurement

The fixture test measures:

- estimated input tokens
- estimated output tokens
- estimated LLM token cost

It does not include infrastructure or operations.

### Full business cost model

The full cost model includes:

- LLM cost
- infrastructure
- operations / people cost

Therefore the two figures should not be directly compared as if they represent the same cost scope.

---

## 9. Effect of Response Caching

The controlled cache experiment used the same fixed fixture set twice.

Results:

| Metric | Baseline | Cache Test |
|---|---:|---:|
| Estimated LLM cost/1,000 | $0.018540 | $0.009270 |
| Cache hit rate | 0% | 50% |

The estimated LLM cost per 1,000 requests decreased by:

**50%**

This occurred because 10 of 20 requests were served from cache and did not require another model execution.

This is an LLM cost saving only.

A cache hit still consumes some:

- application CPU
- memory
- networking
- infrastructure

Therefore cache hits should not be described as having zero total system cost.

---

## 10. Effect of Batching

The batch experiment compared:

- 10 individual patient requests sent as 10 HTTP requests
- 10 patient requests sent as 2 batches of 5

Results:

| Metric | Individual | Batch |
|---|---:|---:|
| Patient requests | 10 | 10 |
| HTTP requests | 10 | 2 |
| Total wall time | 188.91 ms | 50.91 ms |
| Estimated LLM cost | $0.00018540 | $0.00018540 |

Batching reduced HTTP requests by:

**80%**

Measured wall time decreased by:

**73.05%**

However, estimated LLM cost remained unchanged because every patient was still processed individually by the model.

Therefore, in the current implementation, batching primarily improves:

- HTTP efficiency
- throughput
- scheduling efficiency

It does not reduce token cost.

---

## 11. Cost Optimisation Summary

The two implemented optimisation levers affect cost differently.

### Response cache

Primary benefit:

**Reduces repeated LLM executions**

Measured controlled-test result:

**50% reduction in estimated LLM cost per 1,000 requests**

### Batch API

Primary benefit:

**Reduces HTTP overhead and improves throughput**

Measured controlled-test result:

- HTTP requests reduced from 10 to 2
- total wall time reduced by 73.05%
- token cost unchanged

This distinction is important because optimisation benefits should not be incorrectly attributed.

---

## 12. Budget Control

The proposed AfyaPlus monthly cloud budget is:

**$50**

The baseline modeled monthly cost is:

**$36.65**

Budget alerts are configured at:

| Threshold | Amount |
|---|---:|
| 80% warning | $40 |
| 100% alert | $50 |

The 80% warning provides time to investigate:

- traffic growth
- token usage
- cache hit rate
- unnecessary model calls
- infrastructure utilisation

before the full monthly budget is reached.

---

## 13. Assumptions and Limitations

The following assumptions should be considered when interpreting this cost model:

1. Average input usage is assumed to be 500 tokens/request.
2. Average output usage is assumed to be 150 tokens/request.
3. Infrastructure costs are modeled assumptions rather than measured production cloud bills.
4. Operations cost is a simplified monthly estimate.
5. The development fixture tests use `USE_STUB_LLM=true`.
6. Fixture token counts and costs are therefore estimates rather than actual API billing records.
7. The 10× spike assumes infrastructure can support higher traffic with less than proportional cost growth.
8. Actual production costs will depend on traffic distribution, token usage, caching, model choice, cloud infrastructure, monitoring, networking, storage, and engineering operations.

---

## 14. Reproducibility

The cost calculations can be reproduced using:

`python cost/cost_model.py`

The API-vs-self-host sensitivity calculation can be reproduced using:

`python cost/sensitivity.py`

The baseline fixture measurement can be reproduced using:

`python levers/baseline_measure.py`

The cache experiment can be reproduced using:

`python levers/cache_hitrate.py`

The batch experiment can be reproduced using:

`python -m levers.batch_measure`

All cost assumptions are visible in the repository so the calculations can be reviewed and repeated.

---

## 15. Conclusion

At the modeled baseline of 10,000 requests per month, AfyaPlus has an estimated full operating cost of:

**$36.65/month**

or:

**$3.665 per 1,000 requests**

At the stated 10× traffic scenario of 100,000 requests per month, the modeled cost becomes:

**$91.50/month**

or:

**$0.915 per 1,000 requests**

The lower unit cost at higher traffic is caused by infrastructure and operations costs being spread across more requests.

Response caching provides a direct opportunity to reduce repeated LLM token usage, while batching primarily improves request-processing efficiency.

The final production cost model should be recalculated using measured cloud infrastructure costs, actual model usage, and real production traffic.