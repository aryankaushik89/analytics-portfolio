# Walkthrough

## The question

I wanted to compare three understandable pricing structures and see what happens to merchant fees and provider contribution margin when transaction mix or cost assumptions change.

## The data

The generator creates 360 fictional merchant-month records across four size segments and three channels. The model uses no real merchant, provider or network schedule.

## The calculation

Python separates the price a merchant pays from the five modelled cost components. This makes fee revenue, total cost and contribution margin reconcile for every merchant. Portfolio rates are weighted from totals.

## The dashboard controls

1. Choose Current, Growth or Simple pricing.
2. Filter merchant segment and channel.
3. Change credit cost in basis points without repricing the merchant.
4. Change processed volume while holding merchant mix constant.
5. Read the total sales, weighted effective rate, contribution margin and negative-margin count.
6. Select a merchant row to inspect the fee and cost bridge.
7. Export the filtered merchant calculations as CSV.

The reset button returns the checked base case. If filters leave no merchants, the result area explains that there is nothing to calculate and export is disabled.

## The result

Current has the largest base contribution margin. Growth has the lowest portfolio effective rate, but its smaller commercial buffer is more exposed to an unpriced cost increase. The model supports a segmented review instead of a universal plan change.

## Tradeoffs

The scenario is deliberately narrow. It omits hardware, sales, support, compliance, fraud losses, tax and overhead. The cost rates are authored assumptions. A real pricing decision would need contractual rate tables, merchant-specific terms and validation against settlement statements.

