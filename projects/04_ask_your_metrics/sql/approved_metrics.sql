-- These are the approved metric shapes used by the Python registry.

-- Ending MRR
SELECT ROUND(SUM(mrr), 2) AS ending_mrr
FROM subscription_monthly
WHERE month = :month
  AND status IN ('active', 'past_due');

-- Customer churn rate
SELECT
  ROUND(
    100.0 * SUM(CASE WHEN prior_mrr > 0 AND mrr = 0 THEN 1 ELSE 0 END)
    / NULLIF(SUM(CASE WHEN prior_mrr > 0 THEN 1 ELSE 0 END), 0),
    2
  ) AS customer_churn_rate_pct
FROM subscription_monthly
WHERE month = :month;

-- Net revenue retention
SELECT
  ROUND(
    100.0 * SUM(CASE WHEN prior_mrr > 0 THEN mrr ELSE 0 END)
    / NULLIF(SUM(CASE WHEN prior_mrr > 0 THEN prior_mrr ELSE 0 END), 0),
    2
  ) AS net_revenue_retention_pct
FROM subscription_monthly
WHERE month = :month;
