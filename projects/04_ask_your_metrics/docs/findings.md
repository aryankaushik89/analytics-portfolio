# Findings

## The checked interface stays narrow

All 16 evaluation questions passed: ten answered questions matched independent pandas calculations, two broad requests asked for clarification and four unsupported or unsafe requests ran no SQL.

That is useful evidence for the registry, but it is not broad natural-language understanding. The questions were written for this project and cover a small approved vocabulary.

## The synthetic business grew, but not in a straight line

MRR moved from $231,830.52 in January 2026 to $252,017.16 in December. June ending MRR was $249,283.27. Enterprise contributed the most June MRR at $167,009.50 because the authored enterprise plans are much larger than the other segments.

September NRR was 96.19%, so the starting customer base lost more MRR through churn and contraction than it gained through expansion in that month. April customer churn was 2.02%.

## A visible stop is part of the result

“How is revenue doing?” does not name a metric or time period, so the engine asks for both. CAC is not in the metric dictionary, and write-style questions are unsupported. In each case, no query runs.

## What I would add next

- Test paraphrases written by people who did not see the templates.
- Add role-based metric access and logged query approvals.
- Separate semantic parsing evaluation from numeric SQL evaluation.
- Add a live model only with structured output, an available key and a comparison against this deterministic baseline.
