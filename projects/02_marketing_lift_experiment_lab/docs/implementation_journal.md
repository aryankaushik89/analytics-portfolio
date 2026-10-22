# Implementation journal

October 22, 2026.

## 1. Scope and data choice

I wrote the decision, audience, split, metric, quality gate and completion checks in build_brief.md before coding. I checked the Criteo primary source and its corrected download. The dataset download was unavailable from the build environment, so the actual implementation uses authored synthetic data. I did not use employer data, assessment files or a third-party sample relabelled as original data.

## 2. Analytical implementation

The generator created 118,202 assignment deliveries and 9,570 event deliveries. After identical re-deliveries, 118,127 assigned users remain. The broken experiment deliberately loses control assignments. The main and small experiments retain their full populations.

I implemented the seven-day user outcome separately in pandas and SQLite. All 10 structural checks pass. The full-experiment quality check deliberately blocks missing_controls. That expected failure is not described as a passing experiment.

I used a Wilson/Newcombe difference interval, a chi-square allocation diagnostic, a development-only customer group selection and a hypothetical cost calculation. There is no fitted prediction model, live ad-platform integration or causal estimate from observational advertising exposure.

## 3. Execution and tests

The notebook builder executed 11 code cells from a fresh direct Python namespace, capturing actual printed tables and two matplotlib figures. It did not start an external Jupyter kernel. The matching script ran in a separate process, and its stdout matches the notebook's captured stdout exactly.

All 22 Python tests pass. The numerical interface tests compare all 54 experiment × split × customer × device filter selections with independent Python outputs. Counts and effect intervals match at the stated tolerances. Seven further boundary checks cover empty data, a missing arm, zero conversions, invalid planning combinations and CSV quoting.

## 4. Browser checks

I used the supported browser preview to check all five views, campaign/split/customer/device filters, reset, development-only messaging, customer-group explanations and data-quality blocks. A blocked experiment stays blocked after changing customer and device filters. The small test at CAD 0.30 shows an inconclusive decision. Invalid negative cost shows a useful message.

I opened retargeting_000017. It has two in-window purchases and one later event, with converted = 1. The empty record search disables export. I downloaded and parsed a one-record examples CSV and a filtered summary CSV. The downloaded data matches the active search, filters, counts and calculations. The planning view gives 10,890 users per arm at the defaults and rejects inputs summing above 100%.

The initial browser pass found an asynchronous tab-display delay. I made tab display synchronous when a navigation button is clicked, then repeated the affected navigation checks. The notebook builder also caught a string-literal escaping error, which was corrected before successful execution.

## 5. Presentation and hosting

The interface uses plain headings, modest green accents and simple cards. It runs in the browser with saved aggregates and can later be hosted on GitHub Pages. Private Sites access is preserved. The personal portfolio website is outside this change.

Desktop visual review passed. A supported browser check at a 390-pixel iframe width also passed, with no horizontal overflow of the page body and a working experiment filter. The navigation strip can scroll within its own region. This was a responsive layout check, not a mobile-device hardware test.

The final verification manifest records the responsive-layout checks, byte-identical data regeneration, actual dependency versions and source file hashes. Publication records are held separately from public source. There are no secrets in this folder.

## 6. Limits

This release demonstrates the method on synthetic data. The real Criteo benchmark is deferred. The intervals assume independent users and pointwise comparisons. The financial inputs are hypothetical. No mobile-device hardware test, live ad feed, deployed Python backend or cloud data warehouse integration is claimed.
