# Metric definitions

## Recurring revenue

Local MRR is unit price times quantity, divided by 100 to convert minor units to currency units. Annual subscriptions are also divided by 12. Only active and past_due statuses contribute. Trials, free plans, cancelled and unpaid statuses contribute zero. The generated scenario contains active, past_due, cancelled and free accounts; trials and unpaid can be represented by the SQL but are not generated examples.

Reported closing MRR is local MRR times the current monthly CAD FX rate. Opening MRR is the previous local balance times the previous FX rate. ARR is closing MRR times 12. These are run rates and do not represent recognized revenue.

## Signed movements

| Movement | Rule | FX basis |
| --- | --- | --- |
| New | Current local MRR is positive, prior value is zero and the account has never paid before | Current month |
| Reactivation | Current local MRR is positive, prior value is zero and the account paid in an earlier month | Current month |
| Expansion | Both values are positive and current local MRR is higher | Current month on the local difference |
| Contraction | Both are positive and current local MRR is lower | Current month on the signed local difference |
| Churn | Prior local MRR is positive and current local MRR is zero | Current month on the negative opening local balance |
| FX | Opening local MRR times the change in FX rate | Current rate less previous rate |

Opening MRR plus all six signed movements equals closing MRR. FX also applies to a churned customer's opening balance, so the combined churn and FX terms remove exactly the previously reported value.

## Retention

The opening paid cohort contains accounts with prior local MRR above zero.

NRR is the sum of their closing local MRR converted at opening FX, divided by their opening reported CAD MRR. New and reactivated accounts are excluded because they have no positive opening MRR in the current month.

GRR uses the same denominator. For each account, retain the smaller of its opening and closing local MRR, converted at opening FX. This removes expansion. GRR is bounded by zero and one. With no positive opening denominator, both rates are unavailable, not zero.

The separate cohort export shows logo retention by first positive month in the generated history. It includes returned accounts as active again, so it is an active-cohort share rather than a survival curve.

## Billing and collection

Net billed = gross invoice amount minus credit notes.

Net cash = payments minus refunds.

Outstanding = net billed minus net cash.

Convert all three at the invoice month's FX rate. This makes an invoice-cohort identity, not an accounting revaluation of older receivables. The dashboard selects invoices issued within the reporting month. It does not present outstanding balances from all preceding months or an ageing report.

The synthetic billing policy assumes same-month settlement events. Monthly contracts bill the current value at the month boundary. Annual contracts bill the annual amount at commencement or renewal. The specific midmonth upgrade bills the old full monthly amount plus the price difference times 16/30. There are no taxes or usage charges.

Floating point amounts remain unrounded during metric calculation and are rounded for presentation. Reconciliation checks allow a one-millionth CAD tolerance for Python floating point calculations. Currency source amounts use integer minor units.
