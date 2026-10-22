# Project working notes

Keep the Python, SQL and explanations straightforward. Use short notebook cells, numbered sections, one import per line and visible check tables. Keep automated assertions in tests. Do not introduce custom classes in the analysis.

This project uses authored synthetic randomized experiments. No Criteo records, employer data or assessment material is included. Always label the scenario and financial assumptions. Estimate intention-to-treat effects from assigned users, not exposed users. Keep development and evaluation users separate. The development-selected customer group is fixed before inspecting evaluation outcomes.

Use seven complete days after assignment for conversions. Deduplicate event IDs before the user join. Keep all assigned users, including people with no events. A failed sample-ratio check blocks recommendations. Filters do not override a failure in the full experiment.

Run `python generate_data.py`, `python analysis.py`, `python -m unittest discover -s tests -v`, `python tools/make_notebook.py`, `python experiment_analysis.py` and `node tests/check_dashboard.mjs` for the initial analytical release. Re-run affected checks after changes. Keep outputs, documentation and interface data consistent. Preserve Site identity and private access.
