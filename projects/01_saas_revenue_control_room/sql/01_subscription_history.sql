CREATE TABLE clean_events AS
SELECT event_id, customer_id, effective_at, unit_amount_minor, quantity, billing_interval, status
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY received_at DESC) AS delivery_number
    FROM subscription_events_raw
)
WHERE delivery_number = 1;

CREATE TABLE monthly_subscriptions AS
WITH ranked_history AS (
    SELECT m.month, c.customer_id, c.company, c.region, c.channel, c.currency,
           e.event_id, e.effective_at, e.unit_amount_minor, e.quantity, e.billing_interval, e.status,
           ROW_NUMBER() OVER (
               PARTITION BY m.month, c.customer_id
               ORDER BY e.effective_at DESC, e.event_id DESC
           ) AS event_rank
    FROM months AS m
    JOIN customers AS c ON c.signup_date <= m.month_end
    JOIN clean_events AS e ON e.customer_id = c.customer_id
                         AND date(e.effective_at) <= date(m.month_end)
)
SELECT r.*, f.cad_rate,
       CASE WHEN r.status IN ('active', 'past_due') THEN
           r.unit_amount_minor * r.quantity / 100.0 /
           CASE WHEN r.billing_interval = 'year' THEN 12.0 ELSE 1.0 END
           ELSE 0 END AS local_mrr
FROM ranked_history AS r
JOIN fx_rates AS f ON f.month = r.month AND f.currency = r.currency
WHERE event_rank = 1;
