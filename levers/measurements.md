# Optimisation Measurements

## Test Environment

The AfyaPlus triage API was tested locally using FastAPI and Uvicorn.

The same fixed fixture set in:

`fixtures/triage_requests.json`

was used for baseline and optimisation measurements.

The LLM path was stubbed during development using:

`USE_STUB_LLM=true`

Therefore token counts and LLM costs shown below are estimates rather than actual billed API usage.

---

# Baseline

The baseline test executed 10 triage requests without using cached responses.

| Metric | Baseline |
|---|---:|
| Successful requests | 10 |
| Total input tokens | 136 |
| Total output tokens | 275 |
| Average latency | 14.49 ms |
| p95 latency | 23.37 ms |
| Estimated LLM cost for fixture set | $0.00018540 |
| Average estimated LLM cost/request | $0.00001854 |
| Estimated LLM cost/1,000 requests | $0.018540 |

---

# Lever 1: Response Cache

An in-memory response cache with a 300-second TTL was added.

The fixed fixture set was executed twice.

Round 1 populated the cache and produced 10 cache misses.

Round 2 repeated the same requests and produced 10 cache hits.

| Metric | Cache Test |
|---|---:|
| Successful requests | 20 |
| Cache hits | 10 |
| Cache misses | 10 |
| Hit rate | 50.00% |
| Average latency | 9.71 ms |
| p95 latency | 18.83 ms |
| Estimated total LLM cost | $0.00018540 |
| Average estimated LLM cost/request | $0.00000927 |
| Estimated LLM cost/1,000 requests | $0.009270 |

---

## Before vs After

| Metric | Baseline | Cache | Change |
|---|---:|---:|---:|
| Estimated LLM cost/1,000 | $0.018540 | $0.009270 | -50.0% |
| Average latency | 14.49 ms | 9.71 ms | -33.0% |
| p95 latency | 23.37 ms | 18.83 ms | -19.4% |
| Cache hit rate | 0% | 50% | +50 percentage points |

---

## Interpretation

The controlled cache workload reduced estimated LLM cost per 1,000 requests by 50% because half of the requests were served from cache and did not require another model execution.

The observed average latency and p95 latency were also lower during the cache test. However, the local test uses a very fast stubbed model, so individual request latency contains significant runtime and HTTP noise. The strongest demonstrated benefit of this lever is reduction in model calls and estimated LLM cost.

The measured 50% hit rate is specific to this controlled test because every fixture request was deliberately repeated once. It should not be treated as a predicted production hit rate.

---

## Cache Limitations

The current implementation uses an in-memory Python dictionary rather than Redis.

Consequences:

- Cache contents are lost when the API process restarts.
- Cache entries are local to one process.
- Multiple API replicas would not share the same cache.
- The implementation is suitable for capstone evidence and local testing but not a production distributed cache.

A production deployment could use Redis or another shared caching service.

# Lever 2: Batch API

A batch endpoint was implemented to allow multiple patient triage requests to be submitted in a single HTTP request.

The same 10 fixture requests were tested in two modes:

1. Individual mode: 10 patient requests sent as 10 separate HTTP requests
2. Batch mode: 10 patient requests sent as 2 HTTP requests, using a batch size of 5

| Metric | Individual | Batch | Change |
|---|---:|---:|---:|
| Patient requests | 10 | 10 | No change |
| HTTP requests | 10 | 2 | -80% |
| Total wall time | 188.91 ms | 50.91 ms | -73.05% |
| Average time/patient | 18.89 ms | 5.09 ms | -73.05% |
| Estimated LLM cost | $0.00018540 | $0.00018540 | No change |

## Interpretation

Batching reduced the number of HTTP requests from 10 to 2 and reduced measured total wall time by 73.05% in the local test.

The estimated LLM cost did not change because the current batch implementation still performs one model inference per patient.

The demonstrated benefit of batching in this implementation is therefore reduced HTTP overhead and improved throughput, not reduced token usage.

The measured wall-time improvement is specific to the local test environment and should not be treated as a guaranteed production improvement.

## Batch Limitations

The current implementation uses a synchronous local batch endpoint.

It does not use a production queue such as Redis Queue, Celery, Kafka, or a cloud messaging service.

A production deployment could use an asynchronous queue and worker pool to smooth traffic spikes, apply backpressure, and improve resource utilisation.