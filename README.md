# Week 7 – Cost-Optimised AI Deployment

## Overview

This project extends the AfyaPlus triage API with cost optimisation, deployment controls, measurable optimisation levers, and an executive cost brief.

The service uses FastAPI and Docker and supports authenticated triage requests.

The cost model uses GPT-4o mini pricing:

- Input: $0.15 per 1 million tokens
- Output: $0.60 per 1 million tokens

The baseline traffic assumption is:

- 10,000 requests/month

The 10× spike assumption is:

- 100,000 requests/month

The main business metric is:

**Cost per 1,000 requests**

---

## Deliverable 1 – Cost Model

Files:

- `cost/cost_model.py`
- `cost/cost_model.md`
- `cost/sensitivity.py`

### Baseline

- Monthly requests: 10,000
- Cost/request: $0.003665
- Cost/1,000 requests: $3.665
- Estimated monthly cost: $36.65

### 10× Traffic Spike

- Monthly requests: 100,000
- Cost/request: $0.000915
- Cost/1,000 requests: $0.915
- Estimated monthly cost: $91.50

The lower unit cost at higher traffic is caused by infrastructure and operations costs being spread across a larger request volume.

Run:

```bash
python cost/cost_model.py
```

Sensitivity and API-vs-self-host break-even:

```bash
python cost/sensitivity.py
```

---

## Deliverable 2 – Deployment and Budget Controls

Files:

- `deploy/docker-compose.cost.yml`
- `deploy/azure_budget_triage.json`
- `deploy/budget_alert_notes.md`
- `Dockerfile`
- `.dockerignore`

The AfyaPlus API is deployed locally using Docker Compose.

Run:

```bash
docker compose -f deploy/docker-compose.cost.yml build
```

Start:

```bash
docker compose -f deploy/docker-compose.cost.yml up -d
```

Check status:

```bash
docker compose -f deploy/docker-compose.cost.yml ps
```

Expected service:

```text
afyaplus-triage
```

Expected status:

```text
healthy
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

### FinOps Labels

The Docker deployment includes:

- `finops.service = afyaplus-triage`
- `finops.environment = development`
- `finops.cost-center = ai-platform`
- `finops.owner = afyaplus-team`

### Budget Control

Monthly budget:

**$50**

Thresholds:

- 80% warning: $40
- 100% alert: $50

The Azure budget JSON is included as configuration evidence.

---

## Deliverable 3 – Optimisation Levers

Files:

- `levers/cache_triage.py`
- `levers/cache_hitrate.py`
- `levers/batch_worker.py`
- `levers/batch_measure.py`
- `levers/measurements.md`

A fixed fixture set is stored in:

- `fixtures/triage_requests.json`

The same fixture set is used for before/after measurements.

---

### Lever 1 – Response Cache

The implementation uses an in-memory dictionary cache with a 300-second TTL.

Controlled test results:

- Successful requests: 20
- Cache hits: 10
- Cache misses: 10
- Hit rate: 50%
- Baseline estimated LLM cost/1,000: $0.018540
- Cached estimated LLM cost/1,000: $0.009270

Estimated LLM cost reduction:

**50%**

The measured 50% hit rate is specific to the controlled experiment because every request was deliberately repeated once.

The cache is a local fallback implementation and is not intended as a production distributed cache.

Run:

```bash
python levers/cache_hitrate.py
```

---

### Lever 2 – Batch API

The batch endpoint groups patient triage requests into fewer HTTP requests.

Controlled test results:

| Metric | Individual | Batch |
|---|---:|---:|
| Patient requests | 10 | 10 |
| HTTP requests | 10 | 2 |
| Total wall time | 188.91 ms | 50.91 ms |
| Average time/patient | 18.89 ms | 5.09 ms |
| Estimated LLM cost | $0.00018540 | $0.00018540 |

Observed results:

- HTTP request reduction: 80%
- Wall-time reduction: 73.05%
- Token cost reduction: 0%

Batching improved throughput and reduced HTTP overhead, but it did not reduce token usage because each patient still required model processing.

Run:

```bash
python -m levers.batch_measure
```

---

## Deliverable 4 – API vs Self-Host Memo

File:

- `memo/api_vs_selfhost.md`

The sensitivity model compares API-hosted GPT-4o mini inference against an estimated self-hosted open-source model deployment.

Estimated self-host monthly cost:

**$450/month**

This includes:

- GPU: $300
- Supporting infrastructure: $50
- Operations: $100

Estimated token-cost crossover:

**approximately 2.73 million requests/month**

This is only a cost crossover point.

It does not automatically mean self-hosting becomes the preferred architecture at that volume.

The decision must also consider:

- model quality
- safety
- GPU utilisation
- reliability
- staffing
- security
- monitoring
- operational complexity

---

## Deliverable 5 – Executive One-Pager

File:

- `exec/one_pager.pdf`

The executive summary includes:

- baseline cost
- 10× spike cost
- two optimisation levers
- budget controls
- risk and mitigation
- API-vs-self-host trade-off
- go/no-go conditions

---

## API Endpoints

The API currently exposes:

```text
GET  /health

POST /token

POST /triage

POST /triage/batch

GET  /cache/stats

POST /cache/clear
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Authentication

The capstone uses JWT authentication.

Demo dispatcher:

```text
username: mercy
```

The password is used only for local capstone testing and should not be used in production.

Production deployments should use:

- secure credential storage
- real user persistence
- rotated JWT secrets
- secret management

---

## Environment Variables

Example configuration:

```text
JWT_SECRET=replace-with-a-long-random-secret

OPENAI_API_KEY=

OPENAI_MODEL=gpt-4o-mini

USE_STUB_LLM=true
```

The `.env` file is excluded from Git.

No secrets should be committed to the repository.

---

## Fallbacks Declared

### Redis

Used:

**In-memory dictionary cache**

Reason:

Redis was not required