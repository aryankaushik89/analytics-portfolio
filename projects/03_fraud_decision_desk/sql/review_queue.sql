-- Build a daily review queue without changing the source score table.
WITH eligible AS (
    SELECT
        transaction_id,
        transaction_time,
        day,
        amount,
        fraud_score,
        is_fraud,
        ROW_NUMBER() OVER (
            PARTITION BY day
            ORDER BY fraud_score DESC, transaction_time
        ) AS queue_position
    FROM scored_transactions
    WHERE fraud_score >= :score_threshold
)
SELECT
    transaction_id,
    transaction_time,
    day,
    amount,
    fraud_score,
    is_fraud,
    queue_position
FROM eligible
WHERE queue_position <= :daily_review_capacity
ORDER BY day, queue_position;
