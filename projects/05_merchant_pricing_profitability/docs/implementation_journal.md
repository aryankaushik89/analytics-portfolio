# Implementation journal

## Scope

I refined the project around one commercial decision: compare transparent pricing options at merchant level and test whether they cover modelled payment costs. The intended readers are payments analytics and commercial finance teams. The new evidence is weighted pricing, cost allocation, contribution margin, break-even logic and sensitivity analysis.

## Source review

I reviewed current public Canadian sources before setting the model structure. Mastercard explains that interchange is one part of a merchant discount rate and that acquirers set their merchant agreements. Visa describes interchange as a transfer between an acquirer and issuer. The Financial Consumer Agency of Canada emphasizes transparent merchant pricing and cost disclosure. Those sources informed the component labels, not the numeric assumptions.

## Data choice

I used deterministic synthetic data because a real merchant book and provider cost schedule would be proprietary. The generator is included and every commercial rate is visible in code and in the interface.

## Build notes

The matching script regenerates the merchant file and writes merchant, plan and segment outputs. The notebook reruns the same functions in short sections. The static dashboard uses the same merchant inputs and formulas in JavaScript, with no external service or live payment integration.

## Checks

Automated tests cover determinism, row grain, fee and margin reconciliation, debit and credit splits, refunds, zero volume, a negative-margin stress case, volume loss, summary totals, plan coverage and empty input. Browser checks cover filters, sensitivity controls, merchant detail, reset, CSV export and an empty-result state.

## Limits

The model is a learning and decision-support demonstration. It is not a quote, a profitability forecast or evidence about a real provider. A desktop browser was used for functional and visual checks. Responsive rules are included, but any separate device check is recorded only if performed.

