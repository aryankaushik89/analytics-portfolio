# Implementation journal

## October 22, 2026

Built the source generator, three SQL models, analytical exports, learning notebook and browser interface. Source records cover 360 fictional accounts, 1,184 delivered event rows and 3,672 invoice rows. Three repeated event deliveries and two repeated invoice rows are deliberate.

The analytical pipeline passed eight visible checks. Fourteen Python tests passed, including annual normalization, past due status, cancellation, reactivation, FX, free accounts, proration, cohort weighting, source deduplication and segment reconciliation.

The JavaScript calculation checks passed 525 month, region and channel combinations. Empty selections were included. The final total was checked against the Python reference result.

The notebook contains nine executed code cells and actual table and chart outputs. The matching Python script ran successfully in a new process. The notebook builder captures Python execution directly and does not run an external Jupyter kernel. An HTML view and chart images were also generated.

Desktop browser checks confirmed the four navigation views, month and region changes, channel filtering, the declining-revenue note, customer search, pagination, no-match feedback, the Midmonth Upgrade dialog, billing records, metric definitions, the guided tour and reset behavior.

The invoice download contained 30 August 2026 Canada/Paid search rows and reconciled to zero difference. The searched customer download contained one September 2026 row for C0004 with CAD 200 closing MRR. Downloads were inspected as actual CSV files.

Visual review confirmed the desktop dashboard layout. Responsive CSS is included, but a separate mobile device visual review was not completed in this run. The optional Google Fonts request is not required for calculations or controls.

Two issues found during verification were corrected. The notebook generator needed raw strings to preserve newline escapes inside code cells. Currency presentation now normalizes floating point negative zero to zero, and the analyst heading identifies a declining filtered view directly.

The app has no authentication, database connection, API key entry or external AI call. It displays synthetic exported data and performs filtering and aggregation in the browser. Hosted preview access is controlled by the hosting service.

The personal portfolio website has not been edited. Daily GitHub publication is handled by the separate release workflow after the checked source is saved.
