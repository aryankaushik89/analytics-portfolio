-- Merchant-month profitability using the same component definitions as Python.
-- Rate values are parameters in basis points or cents, not real provider terms.
SELECT
    merchant_id,
    segment,
    channel,
    monthly_sales_cad,
    transactions,
    fee_revenue_cad,
    total_cost_cad,
    fee_revenue_cad - total_cost_cad AS contribution_margin_cad,
    CASE
        WHEN monthly_sales_cad > 0 THEN 100.0 * fee_revenue_cad / monthly_sales_cad
        ELSE NULL
    END AS effective_rate_pct
FROM merchant_plan_economics
WHERE plan = :plan_name
ORDER BY contribution_margin_cad ASC;

