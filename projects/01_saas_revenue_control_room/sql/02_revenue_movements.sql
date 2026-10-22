CREATE TABLE customer_month_metrics AS
WITH amounts AS (
    SELECT *,
           LAG(local_mrr, 1, 0) OVER (PARTITION BY customer_id ORDER BY month) AS prior_local_mrr,
           LAG(cad_rate, 1, cad_rate) OVER (PARTITION BY customer_id ORDER BY month) AS prior_fx,
           MAX(CASE WHEN local_mrr > 0 THEN 1 ELSE 0 END) OVER (
               PARTITION BY customer_id ORDER BY month
               ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
           ) AS paid_before
    FROM monthly_subscriptions
), movements AS (
    SELECT *, local_mrr * cad_rate AS closing_mrr, prior_local_mrr * prior_fx AS opening_mrr,
           CASE WHEN prior_local_mrr = 0 AND local_mrr > 0 AND COALESCE(paid_before, 0) = 0
                THEN local_mrr * cad_rate ELSE 0 END AS new_mrr,
           CASE WHEN prior_local_mrr = 0 AND local_mrr > 0 AND paid_before = 1
                THEN local_mrr * cad_rate ELSE 0 END AS reactivation_mrr,
           CASE WHEN prior_local_mrr > 0 AND local_mrr > prior_local_mrr
                THEN (local_mrr - prior_local_mrr) * cad_rate ELSE 0 END AS expansion_mrr,
           CASE WHEN local_mrr > 0 AND local_mrr < prior_local_mrr
                THEN (local_mrr - prior_local_mrr) * cad_rate ELSE 0 END AS contraction_mrr,
           CASE WHEN prior_local_mrr > 0 AND local_mrr = 0
                THEN -prior_local_mrr * cad_rate ELSE 0 END AS churn_mrr,
           prior_local_mrr * (cad_rate - prior_fx) AS fx_mrr,
           CASE WHEN prior_local_mrr > 0 THEN local_mrr * prior_fx ELSE 0 END AS retained_cohort_mrr,
           CASE WHEN prior_local_mrr > 0 THEN MIN(local_mrr, prior_local_mrr) * prior_fx ELSE 0 END AS gross_retained_mrr
    FROM amounts
)
SELECT *, closing_mrr - opening_mrr - new_mrr - reactivation_mrr - expansion_mrr
          - contraction_mrr - churn_mrr - fx_mrr AS bridge_difference
FROM movements;
