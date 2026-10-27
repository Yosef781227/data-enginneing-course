-- Databricks notebook source
-- MAGIC %md
-- MAGIC ![Databricks Academy](./Includes/images/common/db-academy.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 5 - Deploying a Pipeline to Production
-- MAGIC
-- MAGIC In this demonstration, we will begin by adding an additional data source to our pipeline and performing a join with our streaming tables. Then, we will focus on productionizing the pipeline by adding comments and table properties to the objects we create, scheduling the pipeline, and creating an event log to monitor the pipeline.
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Apply the appropriate comment syntax and table properties to pipeline objects to enhance readability.
-- MAGIC - Demonstrate how to perform a join between two streaming tables using a materialized view to optimize data processing.
-- MAGIC - Execute the scheduling of a pipeline using trigger or continuous modes to ensure timely processing.
-- MAGIC - Explore the event log to monitor a production Lakeflow Spark Declarative Pipeline.

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
-- MAGIC 1. Run the following cell to configure your working environment for this course.
-- MAGIC
-- MAGIC     This cell will also reset your `/Volumes/labuser/sdp_1_bronze/source` volume with the JSON files to the starting point, with one JSON file in each directory.

-- COMMAND ----------

-- MAGIC %run ./Includes/Classroom-Setup-REQUIRED

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Explore the Orders and Status JSON Files

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Explore the raw data located in the `/Volumes/labuser/sdp_1_bronze/source/orders/` volume.
-- MAGIC
-- MAGIC    This is the data we have been working with throughout the course demonstrations.
-- MAGIC
-- MAGIC    Run the cell below to view the results. Notice that the orders JSON file(s) contains information about when each order was placed.

-- COMMAND ----------

-- DBTITLE 1,Preview the orders data source files
SELECT *
FROM read_files(
  source_volume_path || '/orders/',
  format => 'JSON'
)
LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Explore the **status** raw data located in the `/Volumes/labuser/sdp_1_bronze/source/status/` volume and filter for the specific **order_id** *75123*.
-- MAGIC
-- MAGIC    Run the cell below to view the results. Notice that the status JSON file(s) contain **order_status** information for each order.
-- MAGIC
-- MAGIC    **NOTE:** The **order_status** can include multiple rows per order and may be any of the following:
-- MAGIC
-- MAGIC    - on the way
-- MAGIC    - canceled
-- MAGIC    - return canceled
-- MAGIC    - reported shipping error
-- MAGIC    - delivered
-- MAGIC    - return processed
-- MAGIC    - return picked up
-- MAGIC    - placed
-- MAGIC    - preparing
-- MAGIC    - return requested
-- MAGIC

-- COMMAND ----------

-- DBTITLE 1,Preview the status data source files
SELECT *
FROM read_files(
  source_volume_path || '/status/',
  format => 'JSON'
)
WHERE order_id = 75123;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. One of our objectives is to join the **orders** data with the order **status** data.
-- MAGIC
-- MAGIC     The query below demonstrates what the result of the final join in the Spark Declarative Pipeline will look like after the data has been incrementally ingested and cleaned when we create the pipeline. Run the cell and review the output.
-- MAGIC
-- MAGIC     Notice that after joining the tables, we can see each **order_id** along with its original **order_timestamp** and the **order_status** at specific points in time.
-- MAGIC
-- MAGIC **NOTE:** The data used in this demo is artificially generated, so the **order_status_timestamps** may not reflect realistic timing.

-- COMMAND ----------

-- DBTITLE 1,Perform a join to preview the desired result
WITH orders AS (
  SELECT *
  FROM read_files(
        source_volume_path || '/orders/',
        format => 'JSON'
  )
),
status AS (
  SELECT *
  FROM read_files(
        source_volume_path || '/status/',
        format => 'JSON'
  )
)
-- Join the views to get the order history with status
SELECT
  orders.order_id,
  timestamp(orders.order_timestamp) AS order_timestamp,
  status.order_status,
  timestamp(status.status_timestamp) AS order_status_timestamp
FROM orders
  INNER JOIN status
  ON orders.order_id = status.order_id
ORDER BY order_id, order_status_timestamp;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Putting a Pipeline in Production
-- MAGIC
-- MAGIC This course includes a complete Lakeflow Spark Declarative Pipeline project that has already been created.
-- MAGIC
-- MAGIC In this section, you'll explore the Spark Declarative Pipeline and modify its settings for production use.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. The screenshot below shows what the final Spark Declarative Pipeline will look like when ingesting a single JSON file from the data sources:
-- MAGIC ![Final Demo 6 Pipeline](./Includes/images/deploying-a-pipeline-to-production/demo5_pipeline_image_run1.png)
-- MAGIC
-- MAGIC     **Note:** Depending on the number of files you've ingested, the row count may vary.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Run the cell below to create your starter Spark Declarative Pipeline for this demonstration. The pipeline will set the following for you:
-- MAGIC     - Your default catalog: **labuser**
-- MAGIC     - Your configuration parameter: `source` = `/Volumes/labuser/sdp_1_bronze/source`
-- MAGIC
-- MAGIC     **NOTE:** If the pipeline already exists, an error will be returned. In that case, you'll need to delete the existing pipeline and rerun this cell.
-- MAGIC
-- MAGIC     To delete the pipeline:
-- MAGIC
-- MAGIC     a. Select **Jobs & Pipelines** from the far-left navigation bar.
-- MAGIC
-- MAGIC     b. Find the pipeline you want to delete.
-- MAGIC
-- MAGIC     c. Click the three-dot menu ![ellipsis icon](./Includes/images/common/ellipsis_icon.png).
-- MAGIC
-- MAGIC     d. Select **Delete**.
-- MAGIC
-- MAGIC **NOTE:**  The `create_declarative_pipeline` function is a custom function built for this course to create the sample pipeline using the Databricks REST API. This avoids manually creating the pipeline and referencing the pipeline assets.

-- COMMAND ----------

-- DBTITLE 1,Create pipeline 5
-- MAGIC %python
-- MAGIC create_declarative_pipeline(
-- MAGIC     pipeline_name=f'5 - Deploying a Pipeline to Production Project - {my_catalog}',
-- MAGIC     root_path_folder_name='5 - Deploying a Pipeline to Production Project',
-- MAGIC     catalog_name=my_catalog,
-- MAGIC     schema_name='default',
-- MAGIC     source_folder_names=['orders', 'status'],
-- MAGIC     configuration={'source': source_volume_path}
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. Complete the following steps to open the starter Spark Declarative Pipeline project for this demonstration:
-- MAGIC
-- MAGIC    a. In the main navigation bar, right-click on **Jobs & Pipelines** and select **Open Link in New Tab**.
-- MAGIC
-- MAGIC    b. In **Jobs & Pipelines** select your **5 - Deploying a Pipeline to Production Project - labuser** pipeline.
-- MAGIC       - **REQUIRED:** At the top near your pipeline name, turn on **New pipeline monitoring**.
-- MAGIC
-- MAGIC    c. In the **Pipeline details** pane on the far right select **Open in Editor** (field to the right of **Source code**) to open the pipeline in the **Lakeflow Pipeline Editor**.
-- MAGIC
-- MAGIC    d. In the new tab, you should see the following folders:
-- MAGIC       - **explorations**
-- MAGIC       - **orders**
-- MAGIC       - **status**
-- MAGIC       - plus the extra **python_excluded** folder that contains the Python version.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Explore the code in the `orders/orders_pipeline.sql` file
-- MAGIC
-- MAGIC 1. In your **Spark Declarative Pipeline** select the **orders** folder.
-- MAGIC
-- MAGIC 2. This file contains the same **orders_pipeline.sql** pipeline you've been working with throughout the course.
-- MAGIC
-- MAGIC 3. Quickly review the code again. Notice the following:
-- MAGIC     - Each streaming table or materialized view now includes a `COMMENT` and `TBLPROPERTIES` section to document each object.
-- MAGIC     - Data quality expectations were added from the previous demonstration.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## E. Explore the code in the `status/status_pipeline` notebook

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E1. Open the `status/status_pipeline.sql` file
-- MAGIC 1. In your Spark Declarative Pipeline editor open the **status/status_pipeline.sql** file.
-- MAGIC
-- MAGIC 2. This file processes new data and adds it to the pipeline for order **status**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E2. Bronze Status Table Creation (`1_bronze_db.status_bronze_demo5`)
-- MAGIC
-- MAGIC Use the code in section `A. Bronze Table Creation`, to understand how the Bronze streaming table is created and how data quality is enforced.
-- MAGIC
-- MAGIC 1. This statement creates the streaming table **1_bronze_db.status_bronze_demo5** by ingesting raw JSON files from your lab volume path: `/Volumes/labuser_/sdp_1_bronze/source/status/`
-- MAGIC
-- MAGIC 2. The `COMMENT` clause adds descriptive metadata to the table, making it easier to understand the table's purpose when browsing in Unity Catalog.
-- MAGIC
-- MAGIC 3. The `TBLPROPERTIES` section adds table level configuration:
-- MAGIC    - `"quality" = "bronze"` labels this table as part of the Bronze layer in the medallion architecture.
-- MAGIC    - `"pipelines.reset.allowed" = false` prevents full table refreshes, which helps avoid accidental truncation of the table and loss of checkpoints during pipeline resets.
-- MAGIC
-- MAGIC 4. The `${source}` variable in the `FROM STREAM` clause is used to dynamically reference your specific volume location using the SDP configuration parameter.
-- MAGIC
-- MAGIC **NOTES**:
-- MAGIC    - **Pipeline table properties**: [AWS](https://docs.databricks.com/aws/en/ldp/properties#pipeline-table-properties) |
-- MAGIC    [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/properties#pipeline-table-properties) |
-- MAGIC    [GCP](https://docs.databricks.com/gcp/en/ldp/properties#pipeline-table-properties)
-- MAGIC    
-- MAGIC    - **For proper tagging visit Apply tags to Unity Catalog securable objects**: [AWS](https://docs.databricks.com/aws/en/database-objects/tags) |
-- MAGIC    [Azure](https://learn.microsoft.com/en-us/azure/databricks/database-objects/tags) |
-- MAGIC    [GCP](https://docs.databricks.com/gcp/en/database-objects/tags). 
-- MAGIC       - Tagging is outside the scope of this course.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E3. Silver Status Table Creation (`2_silver_db.status_silver_demo5`)
-- MAGIC
-- MAGIC Use the code in section `B. Bronze -> Silver`, to understand how the Silver streaming table is created and how data quality is enforced.
-- MAGIC
-- MAGIC 1. This statement creates the streaming table **2_silver_db.status_silver_demo5** from the Bronze streaming table **1_bronze_db.status_bronze_demo5**.
-- MAGIC
-- MAGIC 2. The `SELECT` clause:
-- MAGIC    - Selects only the required columns for the Silver layer.
-- MAGIC    - Casts `status_timestamp` to a proper timestamp as `order_status_timestamp`.
-- MAGIC
-- MAGIC 3. The `CONSTRAINT` clauses define data quality expectations:
-- MAGIC    - `valid_timestamp` drops rows where the timestamp is not valid.
-- MAGIC    - `valid_order_status` warns when the status is not in the allowed list.
-- MAGIC
-- MAGIC 4. The `COMMENT` and `TBLPROPERTIES` document the table and label it as Silver in the medallion architecture.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E4. Materialized View to Join Two Streaming Tables (`3_gold_db.full_order_info_gold_demo5`)
-- MAGIC
-- MAGIC > One way to join two streaming tables in Spark Declarative Pipelines is by creating a materialized view that performs the join.
-- MAGIC
-- MAGIC > This approach takes all rows from each streaming table and executes a full inner join operation and incorporates optimizations where applicable.
-- MAGIC
-- MAGIC
-- MAGIC Use the code in section `C. Use a Materialized View to Join Two Streaming Tables`, to understand how the Gold materialized view is created.
-- MAGIC
-- MAGIC 1. This statement creates the materialized view **3_gold_db.full_order_info_gold_demo5** by joining the following streaming tables:
-- MAGIC    - **2_silver_db.status_silver_demo5**
-- MAGIC    - **2_silver_db.orders_silver_demo5**
-- MAGIC
-- MAGIC 2. The `COMMENT` and `TBLPROPERTIES` document the view and label it as Gold in the medallion architecture.
-- MAGIC
-- MAGIC 3. Notice that the `STREAM` keyword is not used when referencing the streaming tables when creating the materialized view.
-- MAGIC    - This will join **all data** from both streaming tables and return your final materialized view.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### E5. Gold Materialized Views for `Cancelled` and `Delivered Orders`
-- MAGIC
-- MAGIC Use the code in section `D. Create Gold Materialized Views for Cancelled and Delivered Orders`, to understand how the final Gold views are created.
-- MAGIC
-- MAGIC 1. This section creates two Gold materialized views from **3_gold_db.full_order_info_gold_demo5**:
-- MAGIC    - **3_gold_db.cancelled_orders_gold_demo5**, cancelled orders with days to cancel.
-- MAGIC    - **3_gold_db.delivered_orders_gold_demo5**, delivered orders with days to delivery.
-- MAGIC
-- MAGIC 2. Each materialized view filters on a specific status and calculates a simple business metric using `datediff`.
-- MAGIC    - `datediff` function:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/datediff) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/datediff) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/sql/language-manual/functions/datediff)
-- MAGIC
-- MAGIC 3. The `COMMENT` and `TBLPROPERTIES` document each view and label them as Gold in the medallion architecture.

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
-- MAGIC - **Materialized views include built-in optimizations where applicable:**
-- MAGIC
-- MAGIC   - Incremental refresh for materialized views: [AWS](https://docs.databricks.com/aws/en/optimizations/incremental-refresh) |[Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/incremental-refresh) |
-- MAGIC   [GCP](https://docs.databricks.com/gcp/en/optimizations/incremental-refresh)
-- MAGIC
-- MAGIC   - [Delta Live Tables Announces New Capabilities and Performance Optimizations](https://www.databricks.com/blog/2022/06/29/delta-live-tables-announces-new-capabilities-and-performance-optimizations.html)
-- MAGIC
-- MAGIC   - [Cost-effective, incremental ETL with serverless compute for Delta Live Tables pipelines](https://www.databricks.com/blog/cost-effective-incremental-etl-serverless-compute-delta-live-tables-pipelines)
-- MAGIC
-- MAGIC - **Stateful joins (Stream to Stream):** For stateful joins in pipelines (i.e., joining incrementally as data is ingested), refer to the Optimize stateful processing in Spark Declarative Pipelines with watermarks documentation:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/stateful-processing) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/stateful-processing) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/stateful-processing)
-- MAGIC    - **Stateful joins are an advanced topic and outside the scope of this course.**
-- MAGIC
-- MAGIC   </div>
-- MAGIC </div>
-- MAGIC
-- MAGIC
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## F. Create the Production Pipeline
-- MAGIC Follow the steps below to modify the pipeline settings and run the production pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### F1. Review and Modify the Pipeline Settings
-- MAGIC
-- MAGIC 1. Complete the following steps in your **Lakeflow Editor** to configure your Spark Declarative Pipeline for **production**:
-- MAGIC
-- MAGIC    a. Select **Settings** to view your pipeline settings.
-- MAGIC
-- MAGIC    b. In the **Pipeline settings** section, you can:
-- MAGIC       - Modify the **Pipeline name** and **Run as** settings (this lab does not give you permission to modify **Run as**).
-- MAGIC
-- MAGIC          - If you had permission, you could select the pencil icon ![pencil_settings_icon.png](./Includes/images/common/pencil_settings_icon.png) next to **Run as** to modify the option.
-- MAGIC
-- MAGIC          - You can optionally change the executor of the pipeline to a service principal. A service principal is an identity you create in Databricks for use with automated tools, jobs, and applications.
-- MAGIC             - For more information, see the **What is a service principal?** documentation: [AWS](https://docs.databricks.com/aws/en/admin/users-groups/service-principals#what-is-a-service-principal) |
-- MAGIC             [Azure](https://learn.microsoft.com/en-us/azure/databricks/admin/users-groups/service-principals#what-is-a-service-principal) |
-- MAGIC             [GCP](https://docs.databricks.com/gcp/en/admin/users-groups/service-principals#what-is-a-service-principal)
-- MAGIC
-- MAGIC       - In **Pipeline mode**, ensure **Triggered** is selected so the pipeline runs on a schedule to incrementally process data.
-- MAGIC         - Alternatively, you can choose **Continuous** mode to keep the pipeline running at all times.
-- MAGIC         - For more details, see **Triggered vs. continuous pipeline mode**: [AWS](https://docs.databricks.com/aws/en/dlt/pipeline-mode) |
-- MAGIC         [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/pipeline-mode) |
-- MAGIC         [GCP](https://docs.databricks.com/gcp/en/dlt/pipeline-mode)
-- MAGIC
-- MAGIC    c. In the **Code assets** section, confirm that:
-- MAGIC
-- MAGIC       - **Root folder** points to this pipeline project (**5 - Deploying a Pipeline to Production Project**).
-- MAGIC
-- MAGIC       - **Source code** references the **orders** and **status** folders within this project.
-- MAGIC
-- MAGIC    d. In the **Default location for data assets** section, confirm the following:
-- MAGIC
-- MAGIC       - **Default catalog** is your **labuser** catalog.
-- MAGIC
-- MAGIC       - **Default schema** is the **default** schema.
-- MAGIC
-- MAGIC    e. In the **Compute** section, confirm that **Serverless** compute is selected.
-- MAGIC
-- MAGIC    f. In the **Configuration** section, ensure that the `source` key is set to your data source volume path: `/Volumes/labuser_/sdp_1_bronze/source`

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC 2. In the **Advanced settings** section at the bottom:
-- MAGIC
-- MAGIC    a. Expand **Advanced settings**.
-- MAGIC
-- MAGIC    b. Click **Edit advanced settings**.
-- MAGIC
-- MAGIC    c. For **Channel**, you can leave it as **Current** for training purposes:
-- MAGIC     - **Current** - Uses the latest stable Databricks Runtime version, recommended for production.
-- MAGIC     - **Preview** - Uses a more recent, potentially less stable Runtime version, ideal for testing upcoming features.
-- MAGIC     - View the **Lakeflow Spark Declarative Pipelines release notes** and the release upgrade process documentation for more information: [AWS](https://docs.databricks.com/aws/en/release-notes/dlt/) |
-- MAGIC     [Azure](https://learn.microsoft.com/en-us/azure/databricks/release-notes/dlt/) |
-- MAGIC     [GCP](https://docs.databricks.com/gcp/en/release-notes/dlt/)
-- MAGIC
-- MAGIC
-- MAGIC <div style="background: #FFFDE7; border: 2px solid #FFAB00; border-radius: 8px; padding: 16px 20px; font-size: 14pt; line-height: 1.8; color: #0b2026; margin: 8px 0 8px 28px;">
-- MAGIC   <div style="font-weight: 700; font-size: 15pt; margin-bottom: 10px;">   d. ⚠️ REQUIRED — In the <strong>Event logs</strong> section:</div>
-- MAGIC   <ul style="margin: 0; padding-left: 20px;">
-- MAGIC     <li>Select <strong>Publish event log to Unity Catalog</strong>.</li>
-- MAGIC     <li><strong>Event log name</strong> - <code>event_log_demo_5</code>.</li>
-- MAGIC     <li><strong>Event log catalog</strong> - <strong>labuser</strong> catalog.</li>
-- MAGIC     <li><strong>Event log schema</strong> - <strong>sdp_1_bronze</strong> schema.</li>
-- MAGIC     <li>Select <strong>Save</strong>.</li>
-- MAGIC   </ul>
-- MAGIC   <div style="margin-top: 12px; font-size: 13.5pt; color: #5A6F77;">
-- MAGIC     <strong>NOTE:</strong> If the event log is not saved to the correct location, the later event log exploration steps will not work properly.
-- MAGIC   </div>
-- MAGIC </div>
-- MAGIC
-- MAGIC 3\. Click **Save** to save your pipeline settings.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### F2. Schedule the Pipeline
-- MAGIC 1. Once your pipeline is production-ready, you'll want to **schedule it to run either on a time interval or continuously**.
-- MAGIC
-- MAGIC    For this demonstration, we'll:
-- MAGIC    - Schedule the pipeline to run every day at 8:00 PM.
-- MAGIC    - Optionally configure notifications to alert you upon job **Start**, **Success**, and **Failure**.
-- MAGIC      *(If you don't want email notifications, you can skip this step.)*
-- MAGIC
-- MAGIC    Complete the following steps to schedule the pipeline:
-- MAGIC
-- MAGIC    a. Select the **Schedule** button (might be a small calendar icon if your screen is minimized).
-- MAGIC
-- MAGIC    b. For the job name, leave it as **5 - Deploying a Pipeline to Production Project - labuser-name**.
-- MAGIC
-- MAGIC    c. Below **Job name**, select **Advanced**.
-- MAGIC
-- MAGIC    d. In the **Schedule** section, configure the following:
-- MAGIC    - Set the **Day**.
-- MAGIC    - Set the time to **20:00** (8:00 PM).
-- MAGIC    - Leave the **Timezone** as default.
-- MAGIC    - Select **More options**, and under **Notifications**, add your email to receive alerts for:
-- MAGIC      - **Start**
-- MAGIC      - **Success**
-- MAGIC      - **Failure**
-- MAGIC
-- MAGIC    e. Click **Create** to save and schedule the job.
-- MAGIC
-- MAGIC   **NOTE:** You could also set the pipeline to run a few minutes after your current time to see it start through the scheduler.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## G. Run and View the Spark Declarative Pipeline for `orders` and `status`
-- MAGIC
-- MAGIC 1. Manually run (instead of waiting for the job for training purposes) your Spark Declarative Pipeline and view the results.
-- MAGIC     - **NOTE:** Currently we have one JSON file in both the **status** and **orders** volumes.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. After the pipeline has completed its first run, complete the following:
-- MAGIC
-- MAGIC    a. Examine the **Pipeline graph** and confirm:
-- MAGIC       - **status flow**
-- MAGIC          - 536 rows were read into the **status_bronze_demo5** and **status_silver_demo5** streaming tables
-- MAGIC       - **orders flow**
-- MAGIC          - 174 rows were read into the **orders_bronze_demo5** and **orders_silver_demo5** streaming tables
-- MAGIC          - 7 rows are in the **gold_orders_by_date_demo5** materialized view
-- MAGIC       - **streaming tables join and gold materialized views**
-- MAGIC          - 536 rows are in the **full_order_info_gold_demo5** materialized view (JOIN)
-- MAGIC             - 8 rows are in the **cancelled_orders_gold_demo5** materialized view
-- MAGIC             - 94 rows are in the **delivered_orders_gold_demo5** materialized view
-- MAGIC
-- MAGIC
-- MAGIC #### Checkpoint
-- MAGIC
-- MAGIC   ![Final Demo 5 Pipeline](./Includes/images/deploying-a-pipeline-to-production/demo5_pipeline_image_run1.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## H. Incrementally Process new Data in your Pipeline

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### H1. Land More Files in your Volume
-- MAGIC 1. Run the cell below to add **4** more JSON files to your volumes to simulate new files being landed into cloud storage:
-- MAGIC     - `/Volumes/labuser/sdp_1_bronze/source/orders`
-- MAGIC     - `/Volumes/labuser/sdp_1_bronze/source/status`

-- COMMAND ----------

-- DBTITLE 1,Copy files into the data source volumes
-- MAGIC %python
-- MAGIC
-- MAGIC ## Find data in workspace data folder
-- MAGIC data_path = find_folder('Includes/data')
-- MAGIC
-- MAGIC ## Land JSON files to your orders volume
-- MAGIC copy_workspace_files_to_volume(
-- MAGIC     src_workspace_folder=f'{data_path}/orders',
-- MAGIC     target_volume_path=f'{source_volume_path}/orders',
-- MAGIC     n=5
-- MAGIC )
-- MAGIC
-- MAGIC ## Land JSON files to your status volume
-- MAGIC copy_workspace_files_to_volume(
-- MAGIC     src_workspace_folder=f'{data_path}/status',
-- MAGIC     target_volume_path=f'{source_volume_path}/status',
-- MAGIC     n=5
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC orders_list = spark.sql(f"LIST '/Volumes/{my_catalog}/sdp_1_bronze/source/orders'")
-- MAGIC status_list = spark.sql(f"LIST '/Volumes/{my_catalog}/sdp_1_bronze/source/status'")
-- MAGIC display(orders_list)
-- MAGIC display(status_list)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### H2. Run the Pipeline to Incrementally Process New Data
-- MAGIC 1. After you have landed **4** new files into the data source volumes, **run the pipeline to process the newly landed JSON files**.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. After the pipeline completes, view your Pipeline run. Notice the following:
-- MAGIC
-- MAGIC     - **status flow**
-- MAGIC         - The **status** bronze to silver flow ingests 410 new rows.
-- MAGIC
-- MAGIC     - **orders flow**
-- MAGIC         - The **orders** bronze to silver flow ingests 98 new rows.
-- MAGIC         - The **orders_by_date_gold_demo5** materialized view contains 11 rows.
-- MAGIC
-- MAGIC     - **streaming tables join and gold materialized views**
-- MAGIC         - The **full_order_info_gold_demo5** materialized view join contains a total of 946 rows (the previous 536 rows + the new 410 rows).
-- MAGIC         - The **cancelled_orders_gold_demo5** materialized view contains 21 rows.
-- MAGIC         - The **delivered_orders_gold_demo5** materialized view contains 176 rows.
-- MAGIC
-- MAGIC #### Checkpoint - 4 New Files
-- MAGIC ![Pipeline Demo 5](./Includes/images/deploying-a-pipeline-to-production/demo5_pipeline_image_run2.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. In the window at the bottom of your pipeline:
-- MAGIC
-- MAGIC     a. Select the **Expectations** link for the **status_silver_demo5** table.
-- MAGIC
-- MAGIC     b. It should contain the value **1 met | 1 unmet**. Notice that in this run, 7.6% (31 rows) for the **valid_order_status** expectation returned a warning.
-- MAGIC
-- MAGIC     c. This is something we would want to investigate and address in future stages of the pipeline.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## I. Introduction to the Pipeline Event Log (Advanced Topic)
-- MAGIC
-- MAGIC After running your pipeline and successfully publishing the event log as a table named **event_log_demo_5** in your **labuser.default** schema (database), begin exploring the event log.
-- MAGIC
-- MAGIC Here we will quickly introduce the event log. **To process the event log you will need knowledge of parsing JSON formatted strings.**
-- MAGIC
-- MAGIC   - Monitor Lakeflow Spark Declarative Pipelines documentation:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/observability) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/observability) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/observability)
-- MAGIC
-- MAGIC **TROUBLESHOOT:**
-- MAGIC - **REQUIRED:** If you did not run the pipeline and publish the event log, the code below will not run. Please make sure to complete all steps before starting this section.
-- MAGIC
-- MAGIC - **HIDDEN EVENT LOG:** By default, Spark Declarative Pipelines writes the event log to a hidden Delta table in the default catalog and schema configured for the pipeline. While hidden, the table can still be queried by all sufficiently privileged users. By default, only the owner of the pipeline can query the event log table. By default, the name for the hidden event log is formatted as:
-- MAGIC
-- MAGIC   - `catalog.schema.event_log_{pipeline_id}` - where the pipeline ID is the system-assigned UUID with dashes replaced by underscores.
-- MAGIC
-- MAGIC   - Query the Event Log: [AWS](https://docs.databricks.com/aws/en/ldp/monitor-event-logs#query-the-event-log) |
-- MAGIC   [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-logs#query-event-log) |
-- MAGIC   [GCP](https://docs.databricks.com/gcp/en/ldp/monitor-event-logs#query-the-event-log)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Complete the following steps to view the **labuser.default.event_log_demo_5** event log in your catalog:
-- MAGIC
-- MAGIC    a. Select the catalog icon ![Catalog Icon](./Includes/images/common/catalog_icon.png) from the left navigation pane.
-- MAGIC
-- MAGIC    b. Expand your **labuser** catalog.
-- MAGIC
-- MAGIC    c. Expand the following schemas (databases):
-- MAGIC       - **sdp_1_bronze**
-- MAGIC       - **sdp_2_silver**
-- MAGIC       - **sdp_3_gold**
-- MAGIC
-- MAGIC    d. Notice the following:
-- MAGIC       - In the **sdp_1_bronze**, **sdp_2_silver**, and **sdp_3_gold** schemas, the pipeline streaming tables and materialized views were created (they end with **demo5**).
-- MAGIC       - In the **sdp_1_bronze** schema, the pipeline has published the event log as a table named **event_log_demo_5**.
-- MAGIC
-- MAGIC **NOTE:** You might need to refresh the catalogs to view the streaming tables, materialized views, and event log.
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Query your **labuser.sdp_1_bronze.event_log_demo_5** table to see what the event log looks like.
-- MAGIC
-- MAGIC    Notice that it contains all events within the pipeline as **STRING** columns (typically JSON-formatted strings) or **STRUCT** columns. Databricks supports the `:` (colon) operator to parse JSON fields. See the `:` operator documentation: [AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/colonsign) | 
-- MAGIC    [Azure](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/colonsign) |
-- MAGIC    [GCP](https://docs.databricks.com/gcp/en/sql/language-manual/functions/colonsign)
-- MAGIC
-- MAGIC    The following table describes the event log schema. Some fields contain JSON data—such as the **details** field—which must be parsed to perform certain queries.

-- COMMAND ----------

-- DBTITLE 1,View the event log
SELECT *
FROM sdp_1_bronze.event_log_demo_5;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC | Field          | Description |
-- MAGIC |----------------|-------------|
-- MAGIC | `id`           | A unique identifier for the event log record. |
-- MAGIC | `sequence`     | A JSON document containing metadata to identify and order events. |
-- MAGIC | `origin`       | A JSON document containing metadata for the origin of the event, for example, the cloud provider, the cloud provider region, user_id, pipeline_id, or pipeline_type to show where the pipeline was created, either DBSQL or WORKSPACE. |
-- MAGIC | `timestamp`    | The time the event was recorded. |
-- MAGIC | `message`      | A human-readable message describing the event. |
-- MAGIC | `level`        | The event type, for example, INFO, WARN, ERROR, or METRICS. |
-- MAGIC | `maturity_level` | The stability of the event schema. The possible values are:<br><br>- **STABLE**: The schema is stable and will not change.<br>- **NULL**: The schema is stable and will not change. The value may be NULL if the record was created before the maturity_level field was added (release 2022.37).<br>- **EVOLVING**: The schema is not stable and may change.<br>- **DEPRECATED**: The schema is deprecated and the pipeline runtime may stop producing this event at any time. |
-- MAGIC | `error`        | If an error occurred, details describing the error. |
-- MAGIC | `details`      | A JSON document containing structured details of the event. This is the primary field used for analyzing events. |
-- MAGIC | `event_type`   | The event type. |
-- MAGIC
-- MAGIC **Event Log Schema:**
-- MAGIC [AWS](https://docs.databricks.com/aws/en/ldp/monitor-event-log-schema) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-log-schema) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/ldp/monitor-event-log-schema)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 3. The majority of the detailed information you will want from the event log is located in the **details** column, which is a JSON-formatted string. You will need to parse this column.
-- MAGIC
-- MAGIC    You can find more information in the Databricks documentation on how to query JSON strings: [AWS](https://docs.databricks.com/aws/en/semi-structured/json) |
-- MAGIC    [Azure](https://learn.microsoft.com/en-us/azure/databricks/semi-structured/json) |
-- MAGIC    [GCP](https://docs.databricks.com/gcp/en/semi-structured/json)
-- MAGIC
-- MAGIC    The code below will:
-- MAGIC
-- MAGIC    - Return the **event_type** column.
-- MAGIC
-- MAGIC    - Return the entire **details** JSON-formatted string.
-- MAGIC
-- MAGIC    - Parse out the **flow_progress** values from the **details** JSON-formatted string, if they exist.
-- MAGIC
-- MAGIC    - Parse out the **user_action** values from the **details** JSON-formatted string, if they exist.
-- MAGIC

-- COMMAND ----------

SELECT
  id,
  event_type,
  details,
  details:flow_progress,
  details:user_action
FROM sdp_1_bronze.event_log_demo_5

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 4. One use case for the event log is to examine data quality metrics for all runs of your pipeline. These metrics provide valuable insights into your pipeline, both in the short term and long term. Metrics are captured for each constraint throughout the entire lifetime of the table.
-- MAGIC
-- MAGIC    Below is an example query to obtain those metrics. We won't dive into the JSON parsing code here. This example simply demonstrates what's possible with the **event_log**.
-- MAGIC
-- MAGIC    Run the cell and observe the results. Notice the following:
-- MAGIC    - The **passing_records** for each constraint are displayed.
-- MAGIC    - The **failing_records** (WARN) for each constraint are displayed.
-- MAGIC
-- MAGIC **NOTE:** If you have selected **Run pipeline with full table refresh** at any time during your pipeline, your results will include metrics from previous runs as well as from the full refresh. Additional logic is required to isolate results after the full table refresh. This is outside the scope of this course.
-- MAGIC

-- COMMAND ----------

CREATE OR REPLACE TEMPORARY VIEW dq_source_vw AS
SELECT explode(
            from_json(details:flow_progress:data_quality:expectations,
                      "array<struct<name: string, dataset: string, passed_records: int, failed_records: int>>")
          ) AS row_expectations
   FROM sdp_1_bronze.event_log_demo_5
   WHERE event_type = 'flow_progress';


-- View the data
SELECT
  row_expectations.dataset as dataset,
  row_expectations.name as expectation,
  SUM(row_expectations.passed_records) as passing_records,
  SUM(row_expectations.failed_records) as warnings_records
FROM dq_source_vw
GROUP BY row_expectations.dataset, row_expectations.name
ORDER BY dataset;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Summary
-- MAGIC
-- MAGIC This was a quick introduction to the pipeline **event_log**. With the **event_log**, you can investigate all aspects of your pipeline runs to explore the runs as well as create overall reports. Feel free to investigate the **event_log** further on your own.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - Lakeflow Spark Declarative Pipelines properties reference:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/properties#dlt-table-properties) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/properties#pipeline-table-properties) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/properties#dlt-table-properties)
-- MAGIC
-- MAGIC - Table properties and table options:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-tblproperties) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties)
-- MAGIC
-- MAGIC - Triggered vs. continuous pipeline mode:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/pipeline-mode) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/pipeline-mode) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/pipeline-mode)
-- MAGIC
-- MAGIC - Development and production modes:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/ldp/updates#development-mode) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/updates#development-mode) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/ldp/updates#development-mode)
-- MAGIC
-- MAGIC - Monitor Lakeflow Spark Declarative Pipelines:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/observability) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/observability) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/observability)
-- MAGIC
-- MAGIC - **Materialized views include built-in optimizations where applicable:**
-- MAGIC   - Incremental refresh for materialized views:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/optimizations/incremental-refresh) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/incremental-refresh) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/optimizations/incremental-refresh)
-- MAGIC   - [Delta Live Tables Announces New Capabilities and Performance Optimizations](https://www.databricks.com/blog/2022/06/29/delta-live-tables-announces-new-capabilities-and-performance-optimizations.html)
-- MAGIC   - [Cost-effective, incremental ETL with serverless compute for Delta Live Tables pipelines](https://www.databricks.com/blog/cost-effective-incremental-etl-serverless-compute-delta-live-tables-pipelines)
-- MAGIC
-- MAGIC - **Stateful joins:** For stateful joins in pipelines (i.e., joining incrementally as data is ingested), refer to the Optimize stateful processing in Lakeflow Spark Declarative Pipelines with watermarks documentation:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/stateful-processing) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/stateful-processing) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/stateful-processing). 
-- MAGIC   - **Stateful joins are an advanced topic and outside the scope of this course.**

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC
-- MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.
-- MAGIC Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
-- MAGIC <script>
-- MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
-- MAGIC </script>