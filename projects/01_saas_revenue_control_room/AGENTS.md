# Working conventions

This is Aryan Kaushik's personal analytics project. Keep Python and SQL readable, with short steps and plain English comments. Use one import statement per line. Use functions when a step repeats, and avoid unnecessary classes. The learning notebook uses numbered headings, short explanations before code and observations after outputs. Show data checks as readable tables there; keep automated assertions in the separate tests.

Keep the presentation understated and personal. Use plain descriptive headings and natural first-person notes where useful. Avoid product marketing slogans or elaborate branding. Aryan prefers about five percent less polish than the initial dashboard, while keeping readable layouts, working controls and correct analysis.

The data is entirely synthetic. Never describe the figures as customer results from a real company. MRR is a subscription run rate, not recognized revenue or cash. Keep the stated billing rules and currency treatment consistent in Python, SQL and the interface.

Run `python analysis.py`, `python -m unittest discover -s tests -v` and `python tools/make_notebook.py` after analytical changes. Run `node tests/check_dashboard.mjs` after calculation changes in the interface. Keep the notebook, findings and dashboard data in agreement. Preserve .openai/hosting.json and use the Sites workflow for deployment.
