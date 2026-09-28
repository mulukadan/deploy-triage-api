# AfyaPlus Budget Controls

## Service

AfyaPlus Triage API

## Environment

Development / Capstone deployment

## Cost ownership

Service: afyaplus-triage

Environment: development

Cost centre: ai-platform

Owner: afyaplus-team

---

## Monthly Budget

The proposed monthly cloud budget is:

$50 USD

The baseline cost model estimates approximately:

$36.65 USD/month

at:

10,000 requests/month

This provides some headroom above the expected baseline.

---

## Alert Thresholds

Two budget thresholds are configured.

### 80% warning

Threshold:

$40

Purpose:

Warn the engineering/operations team before the service reaches the full monthly budget.

Recommended actions:

- Check request volume.
- Review cache hit rate.
- Check model token usage.
- Investigate abnormal traffic.
- Review infrastructure utilisation.

### 100% alert

Threshold:

$50

Purpose:

Escalate when actual monthly spend reaches the approved budget.

Recommended actions:

- Investigate the cost increase.
- Review traffic spike behaviour.
- Confirm caching is operating correctly.
- Check for unnecessary LLM calls.
- Consider reducing non-critical model usage.

---

## FinOps Labels

The local Docker deployment includes the following labels:

- service = afyaplus-triage
- environment = development
- cost-center = ai-platform
- owner = afyaplus-team

Equivalent tags should be applied to cloud resources so service costs can be filtered and attributed.

---

## Capstone Fallback

No paid Azure deployment is required for this capstone environment.

The submitted Azure budget JSON is configuration evidence only.

The application is deployed locally using Docker Compose.

This follows the capstone fallback path for students without access to a paid cloud account.