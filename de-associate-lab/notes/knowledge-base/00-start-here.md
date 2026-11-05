# Before you start: what you are building

Imagine a shop. Each day it receives orders, payments and customer records. They arrive as files, database rows or a live stream of events. A data engineer turns those messy deliveries into reliable information: ‘How much did we sell this week?’

## The whole journey
`Sources → ingest → bronze → clean and join → silver → aggregate → gold → dashboard`

- **Data** means recorded facts. A **row** is one record, such as one order. A **column** is one field, such as price. A **table** is a named collection of rows with defined columns.
- A **schema** describes column names and data types. A type says what a value represents: text, number, date, array or a nested record. A value of `NULL` means missing or unknown; it is not zero or an empty string.
- **SQL** is a language for working with tables. **Python** is a programming language. **PySpark** lets Python describe data operations for Spark, an engine that spreads work across computers. A **DataFrame** is a table-like object you transform in code.
- **Cloud storage** holds files. **Compute** runs instructions on those files. Choosing compute does not choose where the data is permanently stored. A **notebook** is an interactive document containing code and explanations.
- **Delta Lake** is a table storage layer: Parquet data files plus a transaction log. The log tracks consistent versions. It supports reliable updates and reading older versions when the needed history and files remain available.
- **Unity Catalog** organizes data objects and controls access. Think of a library catalogue plus access cards. A common object name is `catalog.schema.table`.

## Three ways data arrives
**Batch:** handle a bounded collection, such as yesterday’s files. **Streaming:** keep handling arriving events. **Incremental:** handle only what has not been handled already. Incremental does not necessarily mean a process must run forever. A scheduled run can process available new data and stop.

## Three levels of readiness
**Bronze** preserves source records with minimal changes, so you can trace or replay them. **Silver** cleans types, missing values and duplicates, and combines useful records. **Gold** presents business-ready facts and summaries. These are design layers, not special file formats.

## How the pieces work together
A **pipeline** turns input data into output data. A **job** decides when tasks run and which task must finish first. A declarative pipeline lets you describe the desired datasets while the platform manages dependencies and updates. **CI/CD** means checking and delivering versioned project changes repeatably. Monitoring tells you whether the work is correct, fast and reliable. Governance limits what people can see or change.

## How to read an exam question
1. Restate the goal in plain words: load new files, retain all left-hand rows, retry failed work, or hide sensitive values?
2. Circle the constraint: ‘without copying’, ‘only new’, ‘must retain’, ‘do not rerun’, or ‘minimum permissions’.
3. Identify the layer: storage, computation, transformation, orchestration, deployment or governance.
4. Predict the behaviour before looking at the choices. For code, try a tiny example with two or three rows.
5. Reject choices by explaining what each would actually do. Do not memorize the letter: the options can move.

## How to use this course
Read one topic, explain it in your own words, then do its linked lab. Some labs simulate Databricks-only features; they say so. Those features need Databricks Free Edition or an appropriate workspace for real-platform practice. Answer the linked PDF questions only after the explanation makes sense. A source-key match is evidence of recall, not proof that the key is right or that you understand the concept.

The current official outline covers seven sections and 45 scored questions. Your 280-question PDF is a study bank; it cannot establish which questions you will receive. The mixed 45-question practice uses approximate blueprint weights, not a prediction of your live paper. Unscored items can also appear on the real exam. During closed-book practice, keep lessons hidden until you finish your attempt.
