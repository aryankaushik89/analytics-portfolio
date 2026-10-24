# Project working notes

This project demonstrates governed metric questions, not unrestricted text-to-SQL. Keep the metric dictionary and approved SQL templates as the source of truth. The parser may select a template and extract safe parameters; it must not compose arbitrary SQL from user text.

Open the database read-only, keep allowed tables explicit and reject statements outside SELECT or WITH. Keep resource limits and unsupported-question handling visible.

The browser interface is an offline replay of checked SQL answers. It is not a live language-model integration or a live database connection. Do not describe it as generative AI.

Use short notebook cells, numbered explanations, imports on separate lines and visible check tables. Put automated assertions in `tests/`, not the notebook.
