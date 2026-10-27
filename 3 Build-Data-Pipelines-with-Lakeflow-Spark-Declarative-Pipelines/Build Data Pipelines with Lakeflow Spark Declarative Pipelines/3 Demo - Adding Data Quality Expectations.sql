-- Databricks notebook source
-- MAGIC %md
-- MAGIC ![Databricks Academy](./Includes/images/common/db-academy.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 3 - Adding Data Quality Expectations
-- MAGIC
-- MAGIC In this demonstration, we will add data quality expectations to apply quality constraints that validate data as it flows through Lakeflow Spark Declarative Pipelines. Expectations provide greater insight into data quality metrics and allow you to fail updates or drop records when detecting invalid records.
-- MAGIC
-- MAGIC
-- MAGIC ### Learning Objectives
-- MAGIC
-- MAGIC By the end of this lesson, you will be able to:
-- MAGIC - Add quality constraints within a Lakeflow Spark Declarative Pipeline to trigger appropriate actions (warn, drop, or fail) based on data expectations.
-- MAGIC - Analyze pipeline metrics to identify and interpret data quality issues across different data flows.

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
-- MAGIC 2. Run the cell below to programmatically view the files in your `/Volumes/labuser_USERNAME/sdp_1_bronze/source/orders/` volume.
-- MAGIC
-- MAGIC     Confirm you only see the original **00.json** file in the **orders** folder.

-- COMMAND ----------

-- DBTITLE 1,View files in the orders volume
-- MAGIC %python
-- MAGIC spark.sql(f'LIST "{source_volume_path}/orders"').display()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## B. Adding Data Quality Expectations
-- MAGIC
-- MAGIC This demonstration includes the simple starter Spark Declarative Pipeline that has already been created in the previous demonstration.
-- MAGIC
-- MAGIC   We will continue to build on it to explore its capabilities.
-- MAGIC
-- MAGIC   **Manage data quality with pipeline expectations**:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/ldp/expectations) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/ldp/expectations)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC
-- MAGIC 1. Run the cell below to create your starter pipeline for this demonstration (pipeline from the previous demonstration).
-- MAGIC
-- MAGIC     The setup code will set the following for you:
-- MAGIC
-- MAGIC     - Your default catalog: **labuser**
-- MAGIC
-- MAGIC     - Your configuration parameter: `source` = `/Volumes/labuser_USERNAME/sdp_1_bronze/source/`
-- MAGIC
-- MAGIC       **NOTE:** If the pipeline already exists, an error will be returned. In that case, you'll need to delete the existing pipeline and rerun this cell.
-- MAGIC
-- MAGIC       To delete the pipeline:
-- MAGIC
-- MAGIC       - Select **Jobs and Pipelines** from the far-left navigation bar.
-- MAGIC
-- MAGIC       - Find the pipeline you want to delete.
-- MAGIC
-- MAGIC       - Click the three-dot menu ![ellipsis icon](./Includes/images/common/ellipsis_icon.png).
-- MAGIC
-- MAGIC       - Select **Delete**.
-- MAGIC
-- MAGIC **NOTE:**  The `create_declarative_pipeline` function is a custom function built for this course to create the sample pipeline using the Databricks REST API. This avoids manually creating the pipeline and referencing the pipeline assets.

-- COMMAND ----------

-- DBTITLE 1,Create pipeline 3
-- MAGIC %python
-- MAGIC create_declarative_pipeline(
-- MAGIC     pipeline_name=f'3 - Adding Data Quality Expectations Project - {my_catalog}',
-- MAGIC     root_path_folder_name='3 - Adding Data Quality Expectations Project',
-- MAGIC     catalog_name=my_catalog,
-- MAGIC     schema_name='default',
-- MAGIC     source_folder_names=['orders'],
-- MAGIC     configuration={'source': source_volume_path}
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. Complete the following steps to open the starter Spark Declarative Pipeline project for this demonstration:
-- MAGIC
-- MAGIC    a. In the main navigation bar, right-click on **Jobs & Pipelines** and select **Open Link in New Tab**.
-- MAGIC
-- MAGIC    b. In **Jobs & Pipelines** select your **3 - Adding Data Quality Expectations Project - labuser** pipeline.
-- MAGIC       - **REQUIRED:** At the top near your pipeline name, turn on **New pipeline monitoring**.
-- MAGIC
-- MAGIC    c. In the **Pipeline details** pane on the far right, select **Open in Editor** (field to the right of **Source code**) to open the pipeline in the **Lakeflow Pipeline Editor**.
-- MAGIC
-- MAGIC    d. In the new tab:
-- MAGIC       - Select the **orders** folder (The main folder also contains the extra **python_excluded** folder that contains the Python version)
-- MAGIC
-- MAGIC       - Click on **orders_pipeline.sql**.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## C. Explore and Run the `orders_pipeline.sql` Pipeline with Data Quality Expectations

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 1. Select the **Run pipeline** button to run the pipeline.
-- MAGIC
-- MAGIC     *While the pipeline is running, proceed to step 2.*

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2. While the pipeline is executing:
-- MAGIC
-- MAGIC    a. Examine `CREATE OR REFRESH STREAMING TABLE 2_silver_db.orders_silver_demo3` (Section **Bronze -> Silver (Contains Data Quality Expectations)**)
-- MAGIC
-- MAGIC    b. Notice that it includes **3 data quality expectations** applied as data is ingested into **orders_silver_demo3**:
-- MAGIC
-- MAGIC       | Constraint | Rule | Action |
-- MAGIC       |------------|------|--------|
-- MAGIC       | `valid_notifications` | `notifications` must be `'Y'` or `'N'` | **Warn** — rows are kept, violation is logged |
-- MAGIC       | `valid_date` | `order_timestamp` must be after `'2021-12-26'` | **Drop Row** — invalid rows are removed |
-- MAGIC       | `valid_id` | `customer_id` must not be `NULL` | **Fail Update** — pipeline fails if violated |
-- MAGIC
-- MAGIC       <br></br>
-- MAGIC       - **notifications** column only contains `Y` or `N` values - so `N` values will trigger a warning
-- MAGIC       - **order_timestamp** column contains dates on `2021-12-25` - so those rows will be dropped
-- MAGIC       - **customer_id** has no nulls in this demo - so the pipeline will pass
-- MAGIC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## D. Explore the Pipeline Run
-- MAGIC
-- MAGIC 1. After the pipeline completes, explore the **Pipeline graph** on the right.
-- MAGIC
-- MAGIC    - It creates the:
-- MAGIC       - **orders_bronze_demo3** > **orders_silver_demo3** > **gold_orders_by_date_demo3** pipeline
-- MAGIC
-- MAGIC    - Notice:
-- MAGIC       - **174 rows** were read into the bronze table
-- MAGIC       - Only **148 rows** were read into the silver table (the table with constraints)
-- MAGIC
-- MAGIC 2. In the bottom window, make sure you are in the **Tables** tab.
-- MAGIC
-- MAGIC    - Select **orders_silver_demo3**, then select **Table metrics**
-- MAGIC
-- MAGIC    - Note the following in the table:
-- MAGIC
-- MAGIC      | Metric | Value | Description |
-- MAGIC      |--------|-------|-------------|
-- MAGIC      | **Output records** | 148 | Rows that passed all expectations and were written to the table |
-- MAGIC      | **Expectations** | 1 met \| 2 unmet | Total data quality expectations set on the streaming table |
-- MAGIC      | **Dropped** | 26 | Rows that failed the `DROP ROW` expectation (14.9% failure rate) |
-- MAGIC      | **Warnings** | 32 | Rows that failed the `WARN` expectation (14.9% failure rate) |
-- MAGIC
-- MAGIC    - Select the link in the **Expectations** column to view detailed breakdown:
-- MAGIC
-- MAGIC      | Constraint | Action | Failure Rate | Failed Rows |
-- MAGIC      |------------|--------|--------------|-------------|
-- MAGIC      | `valid_notifications` | **Allow** (warn) | 22.4% | 39 |
-- MAGIC      | `valid_date` | **Drop** | 14.9% | 26 |
-- MAGIC
-- MAGIC
-- MAGIC - **NOTES:**
-- MAGIC   - If the `WARN` counts differ between the table and the popup, it's because the table view de-duplicates overlapping rows, while the popup counts failures per expectation, even when the same row fails multiple expectations.
-- MAGIC   - Expectation metrics in the UI are per update run. To analyze data quality across multiple runs, query the pipeline event log (covered later in the course).

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Checkpoint
-- MAGIC ![](./Includes/images/data-quality-expectations/quality-expectations-run.png)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Additional Resources
-- MAGIC
-- MAGIC - Manage data quality with pipeline expectations:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/expectations) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/expectations)
-- MAGIC
-- MAGIC - Expectation recommendations and advanced patterns:
-- MAGIC [AWS](https://docs.databricks.com/aws/en/dlt/expectation-patterns) |
-- MAGIC [Azure](https://learn.microsoft.com/en-us/azure/databricks/ldp/expectation-patterns) |
-- MAGIC [GCP](https://docs.databricks.com/gcp/en/dlt/expectation-patterns)
-- MAGIC
-- MAGIC - [Data Quality Management With Databricks](https://www.databricks.com/discover/pages/data-quality-management)

-- COMMAND ----------

-- MAGIC %md-sandbox
-- MAGIC
-- MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.
-- MAGIC Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
-- MAGIC <script>
-- MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
-- MAGIC </script>