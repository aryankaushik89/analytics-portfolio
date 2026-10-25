# Metric definitions

All dollar measures use Canadian dollars and describe one representative synthetic month.

## Processed sales

Gross card sales submitted for processing before refunds. Volume scenarios multiply both sales and transaction counts by the selected change.

## Refund amount

Processed sales multiplied by the merchant's refund rate. It reduces net sales. The model adds a small handling cost for the estimated number of refunded transactions. It does not reverse every original payment cost.

## Fee revenue

The modelled underlying payment cost before a scenario shock, plus the selected plan's volume markup, transaction fee and monthly fee. This cost-plus construction makes the commercial layer visible without presenting a real provider schedule.

## Total payment cost

Synthetic credit interchange, debit transaction cost, network cost, processing cost and refund-handling cost. Credit interchange varies with premium-card and international shares. A cost shock changes this amount while leaving merchant pricing fixed.

## Contribution margin

Fee revenue minus total payment cost. This is before sales, support, hardware, compliance, fraud losses, taxes and overhead, so it is not operating profit.

## Weighted effective rate

Total fee revenue divided by total processed sales. The portfolio and segment figures are recomputed from totals instead of averaging merchant percentages.

## Contribution margin rate

Contribution margin divided by fee revenue. It is undefined when fee revenue is zero.

## Break-even markup

The volume markup required for total fee revenue to equal modelled cost after the plan's transaction and monthly fees. It is undefined at zero volume and can be negative when fixed components already cover costs.

