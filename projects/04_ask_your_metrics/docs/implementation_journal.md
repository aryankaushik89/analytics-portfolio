# Implementation journal

## Scope

I chose an offline governed baseline because no supported live model key was available and the brief requires actual integrations to be distinguished from fixtures. The project is complete as a deterministic metric-question system, not presented as generative AI.

## Data

The generator created 240 customers, 5,760 monthly subscription rows and 3,392 invoices for 2025–2026. The seed is 89. Source CSVs and SQLite tables are included.

## What ran

- Generated all synthetic source tables and rebuilt SQLite.
- Ran seven approved metric templates through a read-only connection.
- Compared ten supported answers with independent pandas calculations.
- Checked two clarification and four unsupported cases.
- Passed 20 Python tests covering reproducibility, every approved template, rejected SQL, database writes, supported answers, fallback handling and result limits.
- Executed 8 notebook code cells in a fresh Python namespace.
- Checked JavaScript syntax and the static dashboard controls.

## Limits

- No live model, Stripe account or production database.
- The browser interface replays checked outputs rather than running SQLite.
- The 16-question set is authored and small.
- The parser covers tested terms and dates, not general conversation.
- No role-based access or audit log beyond the visible output.
