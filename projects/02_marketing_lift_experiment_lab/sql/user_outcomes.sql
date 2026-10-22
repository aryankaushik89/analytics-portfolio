-- SQLite. One row per assigned user. LEFT JOIN keeps users with no purchases.
-- DISTINCT removes identical re-deliveries. Conflicting IDs are checked in Python.
WITH assignments AS (
    SELECT DISTINCT * FROM assignments_raw
), events AS (
    SELECT DISTINCT * FROM conversion_events_raw
)
SELECT
    a.experiment_id,
    a.user_id,
    a.assigned_at,
    a.arm,
    a.customer_type,
    a.device,
    a.split,
    a.exposed,
    COUNT(e.event_id) AS purchases_in_window,
    CASE WHEN COUNT(e.event_id) > 0 THEN 1 ELSE 0 END AS converted
FROM assignments AS a
LEFT JOIN events AS e
    ON a.user_id = e.user_id
    AND a.experiment_id = e.experiment_id
    AND e.event_type = 'purchase'
    AND julianday(e.event_at) >= julianday(a.assigned_at)
    AND julianday(e.event_at) < julianday(a.assigned_at) + 7
    AND julianday(e.event_at) <= julianday(:extract_at)
GROUP BY a.user_id;
