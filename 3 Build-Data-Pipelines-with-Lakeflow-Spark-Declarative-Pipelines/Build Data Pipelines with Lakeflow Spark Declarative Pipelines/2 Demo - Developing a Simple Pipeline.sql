-- Databricks notebook source
-- MAGIC %md
-- MAGIC ![Databricks Academy](./Includes/images/common/db-academy.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 2 - Developing a Simple Pipeline
-- MAGIC
-- MAGIC In this demonstration, we will create a simple Lakeflow Spark Declarative Pipeline project using the new **Lakeflow Pipeline Editor** with declarative SQL.
-- MAGIC
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Describe the SQL syntax used to create a Lakeflow Spark Declarative Pipeline.
-- MAGIC - Navigate the Lakeflow Pipeline Editor to modify pipeline settings and ingest the raw data source file(s).
-- MAGIC - Create, execute, and monitor a Spark Declarative Pipeline.

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC ## REQUIRED - SELECT A COMPUTE ENVIRONMENT
-- MAGIC
-- MAGIC <div style="
-- MAGIC   border-left: 4px solid #f44336;
-- MAGIC   background: #ffebee;
-- MAGIC   padding: 14px 18px;
-- MAGIC   border-radius: 4px;
-- MAGIC   margin: 16px 0;
-- MAGIC ">
-- MAGIC   <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Select Serverless Compute</strong>
-- MAGIC   <div style="color:#333;">
-- MAGIC
-- MAGIC Before starting this notebook, select the required compute environment listed below.
-- MAGIC
-- MAGIC - **Serverless Compute, Version 5**  
-- MAGIC ![Serverless Select](./Includes/images/common/select-serverless.png)
-- MAGIC <br></br>
-- MAGIC   - How to select an environment version:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/compute/serverless/dependencies#-select-an-environment-version) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/dependencies#-select-an-environment-version) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/compute/serverless/dependencies#-select-an-environment-version)
-- MAGIC
-- MAGIC **NOTE:**  This notebook was **developed and tested using Serverless V5**. Other compute options may work but are not guaranteed to behave the same or support all features demonstrated.
-- MAGIC   </div>
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## A. Classroom Setup
-- MAGIC
-- MAGIC Run the following cell to configure your working environment for this course.
-- MAGIC
-- MAGIC This cell will also reset your `/Volumes/labuser/sdp_1_bronze/source` volume with the JSON files to the starting point, with one JSON file in each directory.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-REQUIRED

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Developing and Running a Spark Declarative Pipeline with the Lakeflow Pipeline Editor
-- MAGIC
-- MAGIC
-- MAGIC This course includes a simple, pre-configured Spark Declarative Pipeline to explore and modify.
-- MAGIC
-- MAGIC In this section, we will:
-- MAGIC
-- MAGIC - Explore the Lakeflow Pipeline Editor and the declarative SQL syntax
-- MAGIC - Modify pipeline settings
-- MAGIC - Run the Spark Declarative Pipeline and explore the streaming tables and materialized view.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### B1. Create a Spark Declarative Pipeline From Existing Assets

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Run the cell below and **copy the path** from the output cell to your **labuser_USERNAME.sdp_1_bronze.source** volume.
-- MAGIC
-- MAGIC    You will need this path when modifying your pipeline settings.
-- MAGIC
-- MAGIC    This volume path contains the **orders**, **status** and **customer** directories, which contain the raw JSON files.
-- MAGIC
-- MAGIC    **EXAMPLE PATH**: `/Volumes/labuser/sdp_1_bronze/source`

-- COMMAND ----------

-- DBTITLE 1,Path to data source files
-- MAGIC %python
-- MAGIC print(source_volume_path)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC *In this course, we have starter files for you to use in your pipeline. This demonstration uses the folder **2 - Developing a Simple Pipeline Project**.*
-- MAGIC
-- MAGIC 2. To create the pipeline and add existing assets to associate it with code files already available in your Workspace (including Git folders) complete the following:
-- MAGIC
-- MAGIC    a. For ease of use, open **Jobs & Pipelines** in a separate tab:
-- MAGIC
-- MAGIC     - On the main navigation bar, right-click on **Jobs & Pipelines** and select **Open in a New Tab**.
-- MAGIC
-- MAGIC    b. In **Jobs & Pipelines** select **Create** → **ETL Pipeline**.
-- MAGIC
-- MAGIC    c. Select **Settings (or the gear icon)** and complete the following:
-- MAGIC
-- MAGIC     | Section | Field | Value |
-- MAGIC     |---------|-------|---------------|
-- MAGIC     | **Pipeline settings** |  **Name** | `2 - Developing a Simple Pipeline-add-your-name` |
-- MAGIC     | **Default location for data assets** | **Default catalog** | Your **labuser** catalog |
-- MAGIC     | **Default location for data assets** | **Default schema** | Your **sdp_1_bronze** schema (database) |
-- MAGIC
-- MAGIC    d. In **Settings**, in the **Code assets** section select **Configure paths** to reference our project files.
-- MAGIC
-- MAGIC     - For **Pipeline root folder**: Select the **2 - Developing a Simple Pipeline Project** folder within this course folder then click **Select**:
-- MAGIC       - `.../Build Data Pipelines with Lakeflow Spark Declarative Pipelines/2 - Developing a Simple Pipeline Project`
-- MAGIC
-- MAGIC     - **Source code paths**: Within the same root folder as above, select the **orders** folder and click **Select**::
-- MAGIC       - `.../Build Data Pipelines with Lakeflow Spark Declarative Pipelines/2 - Developing a Simple Pipeline Project/orders`
-- MAGIC
-- MAGIC     **NOTE:** You can select folders containing SQL and Python files to be executed as part of the pipeline, or you can provide individual file paths. The specified files will be processed when the pipeline runs.
-- MAGIC
-- MAGIC **Example**
-- MAGIC
-- MAGIC <img src="./Includes/images/developing-a-simple-pipeline/select_assets.png" alt="Setting Pipeline Assets" width="900">
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### B2. Explore the Pipeline Editor

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. In the new **Lakeflow Pipeline Editor** tab, select the **orders_pipeline.sql** file.
-- MAGIC
-- MAGIC     In the left navigation pane, confirm you are in the **Pipeline** tab.
-- MAGIC
-- MAGIC     Here you should see your pipeline assets.
-- MAGIC
-- MAGIC <br></br>
-- MAGIC ![Orders File Directions](./Includes/images/developing-a-simple-pipeline/demo02-sql-orders-files.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### B2.1. Explore the Folder Structure
-- MAGIC
-- MAGIC Your pipeline project contains three folders:
-- MAGIC
-- MAGIC | Folder | Description |
-- MAGIC |--------|-------------|
-- MAGIC | `exploration` | Sample exploration notebook. **This is excluded from the pipeline** |
-- MAGIC | `orders` | Contains the orders pipeline code (`orders_pipeline.sql`) |
-- MAGIC | `python_excluded` | Python version of the SQL pipeline code. This course focuses on SQL. Feel free to explore the Python version. |
-- MAGIC
-- MAGIC > **NOTE:** You can structure your pipeline project and files however you would like.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### B2.2. Include or Exclude Folders from the Pipeline
-- MAGIC
-- MAGIC 1. Expand the `exploration` folder.
-- MAGIC     - Notice the icon to the right of the `sample_exploration` notebook ![Exclude](./Includes/images/developing-a-simple-pipeline/exclude.png)
-- MAGIC
-- MAGIC     - Hover over it to confirm it is **excluded** from the pipeline.
-- MAGIC
-- MAGIC 2. Right-click on the `exploration` folder.
-- MAGIC     - Notice the option **Include folder as pipeline source code** (don't select it, we don't want explorations included).
-- MAGIC
-- MAGIC     - You can toggle this to include or exclude the folder. **Leave it excluded for now.**
-- MAGIC
-- MAGIC
-- MAGIC 3. Right now only the **orders** folder files are **Included** in the pipeline.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### B2.3. Explore and Modify Pipeline Settings
-- MAGIC
-- MAGIC 1. Select the **Settings** icon (gear icon) in the left navigation pane below the **Pipeline** and **All Files** tabs.
-- MAGIC     - A panel will open on the right.
-- MAGIC
-- MAGIC 2. **Pipeline Settings** - Review the pipeline details:
-- MAGIC     - Pipeline ID, type, name, mode, creator, owner, and run as.
-- MAGIC     - Leave these as is.
-- MAGIC
-- MAGIC 3. **Code Assets** - This section automatically references all included files in your project.
-- MAGIC     - **Root folder** - references the entire pipeline project folder
-- MAGIC     - **Source code** - lists all included files (should show only the `orders` folder)
-- MAGIC     - **NOTE:** Use **Configure paths** to reference files you want to add inside or outside the project root folder if needed
-- MAGIC
-- MAGIC 4. **Default Location for Data Assets**
-- MAGIC
-- MAGIC     - Select **Edit the catalog and schema** and confirm the following:
-- MAGIC
-- MAGIC         | Field | What to Select |
-- MAGIC         |-------|---------------|
-- MAGIC         | **Default catalog** | Your **labuser** catalog |
-- MAGIC         | **Default schema** | **sdp_1_bronze** |
-- MAGIC
-- MAGIC     - Select **Save** if you updated these.
-- MAGIC
-- MAGIC     > **NOTE:** With Lakeflow Spark Declarative Pipelines you can publish streaming tables and materialized views to any catalog and schema. You are not restricted to the default catalog and schema.
-- MAGIC
-- MAGIC 5. **Compute** - Sets the pipeline compute
-- MAGIC
-- MAGIC     a. Select the **Edit** icon and confirm that **Serverless** is selected.
-- MAGIC
-- MAGIC     b. Deselect **Serverless** and review the available compute options, cluster policies, and tags.
-- MAGIC
-- MAGIC     c. **Reselect Serverless** and navigate back to the pipeline settings.

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC <div style="
-- MAGIC   border-left: 4px solid #ff9800;
-- MAGIC   background: #fff3e0;
-- MAGIC   padding: 14px 18px;
-- MAGIC   border-radius: 4px;
-- MAGIC   margin: 16px 0;
-- MAGIC ">
-- MAGIC   <strong style="display:block; color:#e65100; margin-bottom:6px; font-size: 1.1em;">
-- MAGIC     REQUIRED - Add a Configuration Parameter to Point to your Source Volume
-- MAGIC   </strong>
-- MAGIC   <div style="color:#333;">
-- MAGIC
-- MAGIC 6. Complete the following steps to add a `source` variable pointing to your raw data volume.
-- MAGIC
-- MAGIC    a. Run the cell below and copy the path to your source data volume.
-- MAGIC
-- MAGIC    b. Select **Add configuration**.
-- MAGIC
-- MAGIC    c. **Key** = `source`
-- MAGIC
-- MAGIC    d. **Value** = Paste the volume path of your `labuser.sdp_1_bronze.source` volume.
-- MAGIC     - Example: `/Volumes/labuser/sdp_1_bronze/source`
-- MAGIC
-- MAGIC    e. Select **Save**.
-- MAGIC
-- MAGIC **Use parameters with pipelines**:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/ldp/parameters) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/parameters) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/ldp/parameters)
-- MAGIC   </div>
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %python
-- MAGIC print(source_volume_path)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC 7. **Usage** - Review the **Usage** section. This is where you can assign a budget policy for Serverless compute. Tags are applied to compute activity and logged in your billing records.
-- MAGIC
-- MAGIC 8. **Notifications** - Enables you to add notifications on pipeline runs.
-- MAGIC
-- MAGIC 9. **Advanced Settings**
-- MAGIC
-- MAGIC      a. Expand **Advanced Settings** and select **Edit advanced settings**. Review the following options:
-- MAGIC
-- MAGIC     - **Channel** - controls the pipeline runtime version. Leave as **Current**.
-- MAGIC
-- MAGIC     - **Event Logs** - optionally write pipeline audit logs, data quality checks, and lineage to a table. Leave this deselected for now.
-- MAGIC
-- MAGIC 10. Select anywhere in the code editor to close the **settings** panel.

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC
-- MAGIC #### B2.4. Explore the SDP SQL Code
-- MAGIC 1. Review the SQL code in the **orders_pipeline.sql** file.
-- MAGIC
-- MAGIC > **NOTE:** You can also use Python to build pipelines. That can be found in the **python_excluded** folder. This demonstration focuses on SQL.
-- MAGIC
-- MAGIC <br></br>
-- MAGIC ##### EXPAND FOR THE ORDERS CODE DETAILS
-- MAGIC
-- MAGIC <details>
-- MAGIC
-- MAGIC ###### A. Bronze - Raw Ingestion (Streaming Table)
-- MAGIC
-- MAGIC - Ingests raw JSON files from a Volume using Auto Loader (`STREAM read_files`)
-- MAGIC - Adds `processing_time` and `source_file` columns for auditing
-- MAGIC - **Incrementally processes only new files** on each pipeline run
-- MAGIC
-- MAGIC ###### B. Silver - Cleaned & Typed (Streaming Table)
-- MAGIC
-- MAGIC - Reads incrementally from the bronze streaming table (`FROM STREAM sdp_1_bronze.orders_bronze_demo2`)
-- MAGIC - Selects relevant columns and casts `order_timestamp` to `TIMESTAMP`
-- MAGIC - Only new rows from bronze flow through
-- MAGIC
-- MAGIC ###### C. Gold - Aggregation (Materialized View)
-- MAGIC
-- MAGIC - Aggregates silver into **daily order counts** (`GROUP BY date`)
-- MAGIC - Uses a `MATERIALIZED VIEW` instead of a streaming table
-- MAGIC - Aggregations require a full table scan. **However, Databricks optimizes recomputation where possible**
-- MAGIC - **Incremental refresh for materialized views**:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/optimizations/incremental-refresh) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/incremental-refresh) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/optimizations/incremental-refresh)
-- MAGIC
-- MAGIC
-- MAGIC **Key Differences ST/MV**:
-- MAGIC   - Bronze and Silver use `STREAMING TABLE` for incremental processing.
-- MAGIC   - Gold uses `MATERIALIZED VIEW` because `GROUP BY` aggregations can't be incrementally computed.
-- MAGIC
-- MAGIC </details>

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Run the Spark Declarative Pipeline

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC ### C1. Dry Run the Pipeline
-- MAGIC Using a dry run, you can **check for problems in a pipeline's source code** without waiting for tables to be created or updated.
-- MAGIC
-- MAGIC This feature is useful when developing or testing pipelines because it lets you quickly find and fix errors in your pipeline, such as incorrect table or column names.
-- MAGIC
-- MAGIC
-- MAGIC 1. <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Select **Dry Run** from the top navigation bar (if your screen is small, you might have to select the drop-down next to the **Run pipeline** button in the top navigation bar).</span>
-- MAGIC
-- MAGIC     - Notice that the pipeline switches to **DRY RUN** mode in the left window and begins processing each step (this takes about ~1 minute).
-- MAGIC
-- MAGIC     - After the dry run completes, you should see three items in the **Pipeline graph** (Select the graph icon in the right navigation bar if necessary):
-- MAGIC
-- MAGIC       ![Graph](./Includes/images/developing-a-simple-pipeline/dry-run-pipeline-graph.png)
-- MAGIC
-- MAGIC 2. Explore the bottom window and observe the following columns:
-- MAGIC
-- MAGIC     - **Catalog** - the catalog each object will write to
-- MAGIC
-- MAGIC     - **Schema** - the schema each object will write to
-- MAGIC
-- MAGIC     - **Type** - the object type
-- MAGIC
-- MAGIC       ![Window](./Includes/images/developing-a-simple-pipeline/pipeline-dry-run-window.png)

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC <div style="
-- MAGIC   border-left: 4px solid #ff9800;
-- MAGIC   background: #fff3e0;
-- MAGIC   padding: 14px 18px;
-- MAGIC   border-radius: 4px;
-- MAGIC   margin: 16px 0;
-- MAGIC ">
-- MAGIC   <strong style="display:block; color:#e65100; margin-bottom:6px; font-size: 1.1em;">
-- MAGIC     Troubleshooting a Pipeline Error
-- MAGIC   </strong>
-- MAGIC   <div style="color:#333;">
-- MAGIC
-- MAGIC If your pipeline returns an error, verify the following in your <strong>Pipeline Settings</strong>:
-- MAGIC
-- MAGIC   - Default catalog is set to your <strong>labuser</strong> catalog
-- MAGIC
-- MAGIC   - Default schema is set to <strong>sdp_1_bronze</strong>
-- MAGIC
-- MAGIC   - The `source` configuration variable references your volume path: `/Volumes/labuser/sdp_1_bronze/source`
-- MAGIC
-- MAGIC   </div>
-- MAGIC </div>

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### C2. Run the Spark Declarative Pipeline
-- MAGIC
-- MAGIC 1. Select the drop-down next to the **Run pipeline** button in the top navigation bar.
-- MAGIC
-- MAGIC You will see two options:
-- MAGIC
-- MAGIC | Update Type | Materialized View | Streaming Table |
-- MAGIC |-------------|------------------|-----------------|
-- MAGIC | **Run pipeline** - Refresh | Updates results to reflect the current results for the defining query. Will examine the costs, and perform an incremental refresh if it is more cost-efficient. | Processes new records through logic defined in streaming tables and flows. |
-- MAGIC | **Run pipeline with full table refresh** - Full refresh of the pipeline | Updates results to reflect the current results for the defining query. | Clears data from streaming tables, clears state information (checkpoints) from flows, and reprocesses all records from the data source. |
-- MAGIC
-- MAGIC 2. Select **Run pipeline** and monitor each stage in the right window.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC
-- MAGIC <div style="
-- MAGIC   border-left: 4px solid #1976d2;
-- MAGIC   background: #e3f2fd;
-- MAGIC   padding: 14px 18px;
-- MAGIC   border-radius: 4px;
-- MAGIC   margin: 16px 0;
-- MAGIC ">
-- MAGIC   <strong style="display:block; color:#0d47a1; margin-bottom:6px; font-size: 1.1em;">
-- MAGIC     Information
-- MAGIC   </strong>
-- MAGIC   <div style="color:#333;">
-- MAGIC
-- MAGIC - A full refresh deletes all objects and checkpoints. Be careful when using.
-- MAGIC - To prevent a full refresh from being triggered, set the table property: `pipelines.reset.allowed = false`
-- MAGIC - **Pipeline refresh semantics**:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/ldp/updates#pipeline-refresh-semantics) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/updates#pipeline-refresh-semantics) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/ldp/updates#pipeline-refresh-semantics)
-- MAGIC
-- MAGIC   </div>
-- MAGIC </div>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### C3. Monitor the Pipeline Run
-- MAGIC
-- MAGIC 1. While the pipeline is running (~1 minute), observe the **Pipeline graph** on the right.
-- MAGIC
-- MAGIC     As each object is created, a data flow appears and row counts update as processing completes.
-- MAGIC
-- MAGIC     Expected results:
-- MAGIC     - **174 rows** ingested from Raw JSON → Bronze → Silver
-- MAGIC     - **7 rows** in the materialized view aggregation

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC ### C4. Explore the Completed Pipeline
-- MAGIC
-- MAGIC After the pipeline completes, explore the results:
-- MAGIC
-- MAGIC 1. Review the **Pipeline graph**. The graph visualizes the full data flow.
-- MAGIC
-- MAGIC 2. Review the bottom window for details on tables and materialized views created, including locations, durations, and row counts.
-- MAGIC
-- MAGIC    a. <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Select the **Performance** tab to view performance metrics, then return to **Tables**.</span>
-- MAGIC
-- MAGIC    b. <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Select the **orders_bronze_demo2** streaming table to view its **data**, **Table metrics**, and **Performance**.</span>
-- MAGIC
-- MAGIC    c. <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Select the arrow to the left of **All tables** in the bottom window to return to the full pipeline objects list.</span>
-- MAGIC
-- MAGIC    d. <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Select the **gold_orders_by_date_demo2** materialized view and confirm it summarizes data by date as expected.</span>
-- MAGIC       - <span style="background-color: #fff3e0; padding: 2px 6px; border-radius: 4px;">Use the navigation bar in the bottom window to explore the **Data**, **Columns**, **Table metrics**, and **Performance** tabs for the materialized view.</span>
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### C5. Explore the DAG (Pipeline Graph)
-- MAGIC
-- MAGIC 1. You can also select objects directly within the DAG (Pipeline Graph) to update the details in the bottom window.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### C6. Run the Pipeline Again
-- MAGIC
-- MAGIC 1. Select **Run pipeline** again and explore the updated results while it runs.
-- MAGIC
-- MAGIC 2. After the second run completes, note that no new rows were added to the streaming tables.
-- MAGIC
-- MAGIC **This is expected since no new files were added to the data source and the checkpoints know the current data was already ingested**.
-- MAGIC
-- MAGIC ![Run 2](./Includes/images/developing-a-simple-pipeline/run-2-no-changes.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Add a New File to Cloud Storage
-- MAGIC
-- MAGIC 1. Run the cell below to add a new JSON file (**01.json**) to your volume at:  `/Volumes/labuser/sdp_1_bronze/source/orders`.
-- MAGIC
-- MAGIC       This will simulate files being added to cloud storage.

-- COMMAND ----------

-- DBTITLE 1,Add a new JSON file to the data source
-- MAGIC %python
-- MAGIC ## Find data in workspace data folder
-- MAGIC data_path = find_folder('Includes/data')
-- MAGIC
-- MAGIC ## Land another JSON file to your orders volume
-- MAGIC copy_workspace_files_to_volume(
-- MAGIC     src_workspace_folder=f'{data_path}/orders',
-- MAGIC     target_volume_path=f'{source_volume_path}/orders',
-- MAGIC     n=2
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to view the new file in your volume:
-- MAGIC
-- MAGIC    a. Select the **Catalog** icon ![Catalog Icon](./Includes/images/common/catalog_icon.png) from the left navigation pane.
-- MAGIC
-- MAGIC    b. Expand your **labuser.sdp_1_bronze.source** volume.
-- MAGIC
-- MAGIC    c. Expand the **orders** directory.
-- MAGIC
-- MAGIC    d. You should see two files in your volume: **00.json** and **01.json** (refresh if necessary).

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Run the cell below to view the data in the new **/orders/01.json** file. Notice the following:
-- MAGIC
-- MAGIC    - The **01.json** file contains new orders.
-- MAGIC    - The **01.json** file has 25 rows.
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,Preview the 01.json file
-- MAGIC %python
-- MAGIC spark.sql(f'''
-- MAGIC   SELECT *
-- MAGIC   FROM json.`{source_volume_path}/orders/01.json`
-- MAGIC ''').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. Go back to the **orders_pipeline.sql** file and select **Run Pipeline** to execute your ETL pipeline again with the new file.
-- MAGIC
-- MAGIC    - Watch the pipeline run and notice only **25 rows** are added to the bronze and silver tables.
-- MAGIC
-- MAGIC    - This happens because:
-- MAGIC       - The pipeline has already processed the initial **00.json** file (174 rows)
-- MAGIC       - It now reads only the new **01.json** file (25 rows)
-- MAGIC       - New rows are appended to the **streaming tables**
-- MAGIC       - The materialized view is **incrementally recomputed** using the latest data (should have a total of **8 rows**)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Checkpoint
-- MAGIC ![Final](./Includes/images/developing-a-simple-pipeline/demo2-final.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Exploring Your Streaming Tables

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E1. View the Tables

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. View the new streaming tables and materialized view in your catalog. Complete the following:
-- MAGIC
-- MAGIC    a. Select the catalog icon ![Catalog Icon](./Includes/images/common/catalog_icon.png) in the left navigation pane.
-- MAGIC
-- MAGIC    b. Expand your **labuser** catalog.
-- MAGIC
-- MAGIC    c. Expand the schemas **sdp_1_bronze**, **sdp_2_silver**, and **sdp_3_gold**.
-- MAGIC       - Notice that the two streaming tables and materialized view are correctly placed in your schemas.
-- MAGIC
-- MAGIC          - Streaming Bronze Table: **labuser.sdp_1_bronze.orders_bronze_demo2**
-- MAGIC
-- MAGIC          - Streaming Silver Table: **labuser.sdp_2_silver.orders_silver_demo2**
-- MAGIC
-- MAGIC          - Gold Materialized View: **labuser.sdp_3_gold.orders_by_date_gold_demo2**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the cell below to view the data in the **labuser.sdp_1_bronze.orders_bronze_demo2** table.
-- MAGIC
-- MAGIC    Before you run the cell, how many rows should this streaming table have?
-- MAGIC
-- MAGIC    Notice the following:
-- MAGIC       - The table contains 199 rows (**00.json** had 174 rows, and **01.json** had 25 rows).
-- MAGIC       - In the **source_file** column you can see the exact file the rows were ingested from.
-- MAGIC       - In the **processing_time** column you can see the exact time the rows were ingested.

-- COMMAND ----------

-- DBTITLE 1,View the streaming table
SELECT *
FROM sdp_1_bronze.orders_bronze_demo2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E2. View the Table History
-- MAGIC
-- MAGIC 1. Run the code below to view the history of the **orders_bronze_demo2** streaming table.
-- MAGIC
-- MAGIC       Notice the following:
-- MAGIC
-- MAGIC       - In the **operation** column, the last two updates are **STREAMING UPDATE**, not `WRITE` or `MERGE`. This confirms the table is being written to incrementally by a streaming query.
-- MAGIC
-- MAGIC       - Expand the **operationParameters** values for the last two updates. Notice both use `"outputMode": "Append"` and each has an incrementing **epochId** (`0` for the initial load, `1` for the incremental update).
-- MAGIC
-- MAGIC       - Find the **operationMetrics** column. Expand the values for the last two updates. Observe the following:
-- MAGIC
-- MAGIC          - It displays various metrics for the streaming update: **numRemovedFiles, numOutputRows, numOutputBytes, and numAddedFiles**.
-- MAGIC
-- MAGIC          - In the `numOutputRows` values
-- MAGIC             - **174 rows** were added in the first update
-- MAGIC             -  **25 rows** in the second. 
-- MAGIC             - If this were a batch pipeline doing a full re-read, the second run would show 199 rows. The fact that it shows only 25 proves that only new data was processed.
-- MAGIC
-- MAGIC

-- COMMAND ----------

DESCRIBE HISTORY sdp_1_bronze.orders_bronze_demo2

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## F. Viewing Spark Declarative Pipelines with the Pipelines UI
-- MAGIC
-- MAGIC After exploring and creating your pipeline using the **orders_pipeline.sql** file in the steps above, you can view the pipeline(s) you created in your workspace via the **Jobs and Pipelines** UI.
-- MAGIC
-- MAGIC 1. Complete the following steps to view the pipeline you created:
-- MAGIC
-- MAGIC    a. In the main applications navigation pane on the far left (you may need to expand it by selecting the ![Expand Navigation Pane](./Includes/images/developing-a-simple-pipeline/expand_main_navigation.png) icon at the top left of your workspace) right-click on **Jobs & Pipelines** and select **Open Link in a New Tab**.
-- MAGIC
-- MAGIC    b. This should take you to the pipelines you have created. You should see your **2 - Developing a Simple Pipeline Project - your name** pipeline.
-- MAGIC
-- MAGIC    c. Select your **2 - Developing a Simple Pipeline Project - your name**. 
-- MAGIC
-- MAGIC    d. Under your pipeline name, select the drop-down with the timestamp. Here you can view the **Pipeline graph** and other metrics for each run of the pipeline.
-- MAGIC
-- MAGIC    e. Close the pipeline UI tab you opened.
-- MAGIC
-- MAGIC    ![Jobs & Pipelines](./Includes/images/developing-a-simple-pipeline/demo_2_view_in_jobs_pipelines.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - **Lakeflow Spark Declarative Pipelines documentation**:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/)

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC
-- MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.
-- MAGIC Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
-- MAGIC <script>
-- MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
-- MAGIC </script>