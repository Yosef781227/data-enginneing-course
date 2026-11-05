# Section 2: Data Ingestion and Loading — 21%

Get data in without losing track of it.

Start by asking where the data lives, whether it arrives as files or events, whether changes must be captured, and what progress/schema state must survive a restart.

You should be able to choose COPY INTO, Auto Loader, a suitable connector, Kafka/streaming or JDBC/REST—and explain the choice.


## Load files and database rows

**Questions:** 17, 19, 21, 58, 78, 103, 108, 109, 133, 144, 151, 158, 179, 182, 238, 250, 265, 270

**Think of it like this:** Loading is receiving deliveries. Reading every box again differs from recording which boxes have already arrived.

**What the question tests:** Identify the source and the desired loading behaviour. File formats, connector configuration, schema inference and file-level tracking are separate decisions.

**Example:** COPY INTO loads files into a table and tracks files it has already loaded. Re-running it does not mean every old file is copied again. A JDBC reader instead connects to a database; its driver and connection options must match that database.

**Common trap:** File-level tracking is not business-key deduplication. A new file containing an old customer record can still introduce duplicates. Parquet schema information is different from CSV text parsing.

**Try the lab:** lab1_ingestion / 1c (some platform features are simulated)

**Explain without looking:** If a new file repeats yesterday’s customer, does file tracking guarantee a unique customer table?

**Self-check:** No. You still need a business-key rule, deduplication or an appropriate merge.


## Auto Loader, schemas and checkpoints

**Questions:** 7, 71, 76, 122, 123, 168, 221, 232, 255

**Think of it like this:** Auto Loader is a receiving clerk with a notebook: one record tracks the shape of deliveries; another tracks progress.

**What the question tests:** Separate discovery, schema handling, progress tracking and execution triggers. The source format is `cloudFiles`; the underlying processing uses Structured Streaming.

**Example:** Read with `spark.readStream.format('cloudFiles')`, specify the actual file format, and retain checkpoint state. `availableNow` can process the available backlog and stop. Under default add-new-column behaviour, detecting a new column can update schema metadata and stop the stream; it then needs a restart.

**Common trap:** Schema location and checkpoint location have different jobs. Do not assume a new column means uninterrupted processing in every schema-evolution mode. Default JSON inference differs from ordinary Spark JSON reading.

**Try the lab:** lab1_ingestion / 1d (some platform features are simulated)

**Explain without looking:** What does the checkpoint remember that the schema does not?

**Self-check:** Progress and processing state, rather than just field names and types.


## Choose an ingestion connector

**Questions:** 227, 234, 247, 263

**Think of it like this:** A delivery service for Salesforce records is different from a clerk watching a folder of JSON files.

**What the question tests:** Choose by source system, incremental-change support, volume and governance. Distinguish managed connectors, file ingestion and custom JDBC/REST code.

**Example:** For an enterprise system, evaluate a supported managed Lakeflow Connect connector. For files arriving in object storage, evaluate Auto Loader. For Kafka events, use supported streaming ingestion. Land results in the appropriate governed table.

**Common trap:** A connector name is not proof that every source, region, CDC mode and authentication method is supported. Check current capabilities rather than memorizing one universal connector answer.

**Try the lab:** lab1_ingestion / 1d (some platform features are simulated)

**Explain without looking:** Why might a managed connector be preferable to custom polling code?

**Self-check:** It may manage source-specific ingestion and change tracking with less custom operational work, if it supports the requirements.


## Local development, remote Spark

**Questions:** 149, 200, 205, 215

**Think of it like this:** Your laptop is the remote control; the Databricks compute is the television doing the heavy work.

**What the question tests:** Distinguish local authoring/debugging from remote Spark execution. Verify compatible Databricks Connect, Python and Runtime versions and access requirements.

**Example:** You write a DataFrame transformation in a local IDE. Databricks Connect sends supported Spark work to remote compute; it does not turn the laptop into a copy of a complete Databricks cluster.

**Common trap:** Do not assume every library, UDF or Runtime combination works. A question claiming all processing happens locally is missing the point of Connect.

**Try the lab:** lab1_ingestion / 1d (some platform features are simulated)

**Explain without looking:** Where does a large supported Spark aggregation run when using Connect?

**Self-check:** On the configured remote Databricks compute, while you author code locally.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
