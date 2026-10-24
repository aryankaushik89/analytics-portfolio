# Interview explanation

I built Ask Your Metrics to show a governed analytics assistant rather than a chatbot that quietly writes any SQL it wants.

The data is a synthetic subscription business with 240 customers and two years of monthly history. I wrote a metric dictionary for MRR, active customers, churn, NRR, segment MRR and invoice collection rate. A deterministic parser selects an approved query and extracts only date parameters.

The database opens read-only. The query validator allows SELECT or WITH statements against three approved tables, and SQLite's authorizer denies writes and schema changes. Every answer includes the interpreted question, SQL, parameters, returned rows and definition.

I evaluated 16 questions. Ten supported questions matched separate pandas calculations, two ambiguous questions asked for clarification and four unsupported or unsafe requests ran no SQL.

The honest limitation is that this is not a live LLM integration. The browser page is a static replay of checked answers. I would use this version as a baseline before adding a model with structured output and a larger unseen paraphrase set.
