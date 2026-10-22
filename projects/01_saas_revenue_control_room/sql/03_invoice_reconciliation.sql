CREATE TABLE invoice_ledger AS
WITH unique_invoices AS (
    SELECT DISTINCT * FROM invoices_raw
), p AS (
    SELECT invoice_id, SUM(amount_minor) AS payments_minor FROM payments GROUP BY invoice_id
), c AS (
    SELECT invoice_id, SUM(amount_minor) AS credits_minor FROM credit_notes GROUP BY invoice_id
), r AS (
    SELECT invoice_id, SUM(amount_minor) AS refunds_minor FROM refunds GROUP BY invoice_id
)
SELECT i.*, SUBSTR(i.invoice_date, 1, 7) AS month, u.company, u.region, u.channel, f.cad_rate,
       COALESCE(c.credits_minor, 0) AS credits_minor, COALESCE(p.payments_minor, 0) AS payments_minor,
       COALESCE(r.refunds_minor, 0) AS refunds_minor,
       (i.gross_minor - COALESCE(c.credits_minor, 0)) / 100.0 * f.cad_rate AS net_billed_cad,
       (COALESCE(p.payments_minor, 0) - COALESCE(r.refunds_minor, 0)) / 100.0 * f.cad_rate AS net_cash_cad,
       (i.gross_minor - COALESCE(c.credits_minor, 0) - COALESCE(p.payments_minor, 0)
        + COALESCE(r.refunds_minor, 0)) / 100.0 * f.cad_rate AS outstanding_cad
FROM unique_invoices AS i
JOIN customers AS u ON u.customer_id = i.customer_id
JOIN fx_rates AS f ON f.month = SUBSTR(i.invoice_date, 1, 7) AND f.currency = i.currency
LEFT JOIN p ON p.invoice_id = i.invoice_id
LEFT JOIN c ON c.invoice_id = i.invoice_id
LEFT JOIN r ON r.invoice_id = i.invoice_id;
