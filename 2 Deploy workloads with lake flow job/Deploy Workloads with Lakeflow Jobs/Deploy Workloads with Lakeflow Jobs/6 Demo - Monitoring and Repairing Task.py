# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img
# MAGIC     src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png"
# MAGIC     alt="Databricks Learning"
# MAGIC   >
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 6 - Monitoring and Repairing Tasks
# MAGIC
# MAGIC In this lesson, you will learn how to monitor jobs, intentionally cause a failure, and repair failed runs in Databricks.
# MAGIC
# MAGIC **This demo covers:**
# MAGIC - How to repair a failed run
# MAGIC - Rerunning only failed tasks
# MAGIC - Adding a dashboard task
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC
# MAGIC By the end of this lesson, you should be able to:
# MAGIC - Monitor failed job runs
# MAGIC - Repair and re-run failed tasks
# MAGIC
# MAGIC ![Lesson06_full_run](./Includes/images/Lesson06_full_run.png)
# MAGIC
# MAGIC After completing this demo, your job will look like above.

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE (The cluster named 'labuser')
# MAGIC
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC
# MAGIC
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
# MAGIC
# MAGIC 2. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
# MAGIC
# MAGIC    - Click **More** in the drop-down.
# MAGIC
# MAGIC    - In the **Attach to an existing compute resource** window, use the first drop-down to select your unique cluster.
# MAGIC
# MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
# MAGIC
# MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
# MAGIC
# MAGIC 2. Find the triangle icon to the right of your compute cluster name and click it.
# MAGIC
# MAGIC 3. Wait a few minutes for the cluster to start.
# MAGIC
# MAGIC 4. Once the cluster is running, complete the steps above to select your cluster.

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Classroom Setup
# MAGIC
# MAGIC Run the following cell to configure your working environment for this course. It will also set your default catalog to **dbacademy** and the schema to your specific schema name shown below using the `USE` statements.
# MAGIC <br></br>
# MAGIC ```
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA dbacademy.<your unique schema name>;
# MAGIC ```
# MAGIC
# MAGIC **NOTE:** The **DA** object is only used in Databricks Academy courses and is not available outside of these courses.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-6

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Explore Your Schema
# MAGIC Complete the following to explore your **dbacademy.labuser** schema:
# MAGIC
# MAGIC 1. In the left navigation bar, select the catalog icon:  ![Catalog Icon](./Includes/images/catalog_icon.png)
# MAGIC
# MAGIC 2. Locate the catalog called **dbacademy** and expand the catalog.
# MAGIC
# MAGIC 3. Expand your **labuser** schema. 
# MAGIC
# MAGIC 4. Notice that within your schema you will find the tables created by our job till now.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. View Your Files
# MAGIC
# MAGIC You can find the notebook in **Task Files** > **Lesson 6 Files**. Use the link below to view and explore the code:
# MAGIC [Task Files/Lesson 6 Files/6.1 - Transforming Customers Orders State Wise Data]($./Task Files/Lesson 6 Files/6.1 - Transforming Customers Orders State Wise Data)
# MAGIC
# MAGIC - We have ingested three tables into our job. Next, we will add tasks (as notebooks) that will clean and transform the tables created by the For Each loop. These notebooks demonstrate how we can apply transformation logic specific to each table.
# MAGIC
# MAGIC At the end, we will also add a dashboard, which you can find under Lesson 6 Task Files: [Task Files/Lesson 6 Files]($./Task Files/Lesson 6 Files)

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Creating the Starter Job
# MAGIC
# MAGIC Next, we will add the above task Notebook to our job. We'll programmatically create it using the SDK. Simply run the next command to create and configure your job, even if you haven't completed any previous demos. These commands will set up your job with all work completed so far.

# COMMAND ----------

DA.Demo_6_starter_job()

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Adding a Notebook Task to our Retail Job 
# MAGIC 1. Right-click the **Jobs and Pipelines** button in the sidebar and select *Open Link in New Tab*.
# MAGIC
# MAGIC 2. Locate your job named **Demo_06_Retail_Job_<-your schema name->**.
# MAGIC
# MAGIC 3. Navigate to the **Tasks** tab and click **Add task**, then select **Notebook**. Configure the task with the following settings:
# MAGIC
# MAGIC | Setting      | Instructions |
# MAGIC |--------------|-------------|
# MAGIC | **Task name**    | Enter **transforming_customers_orders_data** |
# MAGIC | **Type**         | Ensure **Notebook** is selected |
# MAGIC | **Source**       | Ensure **Workspace** is selected |
# MAGIC | **Path**         | Use the navigator to select [./task files/Lesson 6/6.1 - Transforming Customers Orders State Wise Data]($./Task Files/Lesson 6 Files/6.1 - Transforming Customers Orders State Wise Data) under **Lesson 6 Files** |
# MAGIC | **Compute**      | Select **Serverless** |
# MAGIC | **Depends on**   | Choose **customers_orders_state_wise_report_iterator** |
# MAGIC | **Dependencies** | Set to **All Succeeded** |
# MAGIC | **Retries** | Click on Retries and **untick** "Enable serverless auto-optimization (may include at most 3 retries)" **to disable retries**.
# MAGIC
# MAGIC 4. Click on **Create Task**.
# MAGIC
# MAGIC ![Lesson06_notebook_task.png](./Includes/images/Lesson06_notebook_task.png)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## F. Running your Job
# MAGIC 1. Run the job by clicking **Run now** in the upper-right corner. 
# MAGIC
# MAGIC 2. A pop-up window appears with a link to the job run. Click **View run**.
# MAGIC     - **NOTE:** You can also select the **Runs** tab and then select the link under **Start time** to view the job run **DAG**.
# MAGIC
# MAGIC 3. Watch the tasks in the DAG. The colors change to show the progress of the task (about 2-3 minutes to complete):
# MAGIC
# MAGIC     * **Gray** -- the task has not started
# MAGIC     * **Green stripes** -- the task is currently running
# MAGIC     * **Solid green** -- the task completed successfully
# MAGIC     * **Dark red** -- the task failed
# MAGIC     * **Light red** -- an upstream task failed, so the current task never ran
# MAGIC
# MAGIC 4. When the run is finished, note that **transforming_customers_orders_data** failed. This was expected.
# MAGIC
# MAGIC ![Lesson06_fail_run.png](./Includes/images/Lesson06_fail_run.png)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## G. Repairing Job Runs
# MAGIC
# MAGIC You can view the notebooks used in a task, including their output, as part of a job run. This helps diagnose errors. You can also re-run specific tasks in a failed job run.
# MAGIC
# MAGIC Consider this example:
# MAGIC
# MAGIC You are developing a job with several notebooks. During a job run, one of the tasks fails. You can update the code in that notebook and re-run the failed task and any tasks that depend on it. You can also change task parameters and re-run the task. Let's walk through this process:
# MAGIC
# MAGIC 1. In the upper-right corner, click **Repair run**.
# MAGIC
# MAGIC 2. Open [Task Files/Lesson 6 Files/6.1 - Transforming Customers Orders State Wise Data]($./Task Files/Lesson 6 Files/6.1 - Transforming Customers Orders State Wise Data) and notice that the `def clean_common` function uses the wrong column name.
# MAGIC
# MAGIC 3. Update the column name from `customer` to `customer_name` in code script.
# MAGIC
# MAGIC ![Lesson06_script_snip.png](./Includes/images/Lesson06_script_snip.png)
# MAGIC
# MAGIC
# MAGIC 4. Return to your job run. In the upper-right corner, click **Repair run**. Make sure the **transforming_customers_orders_data** task is selected.
# MAGIC
# MAGIC 5. The "1" in the **Repair run** button indicates that Databricks has selected both the failed task and the dependent task. You can select or deselect any tasks you wish to re-run.
# MAGIC
# MAGIC 6. Wait for the run to complete.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## H. Reviewing the Run
# MAGIC
# MAGIC Once your job run is successful, go back to your job and click on the **Runs** tab. Click on the latest run, then click on **transforming_customers_orders_data**. In the top left corner, you will notice the run status, which is a dropdown list. By clicking on each dropdown option, you can see the output of your task run. Notice the code difference between the successful and failed tasks. You should see the correct column name (`customer_name`) in the successful run.
# MAGIC
# MAGIC ![Lesson06_review_run.png](./Includes/images/Lesson06_review_run.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## I. Adding a Dashboard to Your Job
# MAGIC
# MAGIC In this section, we will integrate a pre-created dashboard into your job. The dashboard has been prepared for you and is stored as a JSON input file, so you don't need to create it from scratch.
# MAGIC
# MAGIC #### I1. Configuring Your Retail Dashboard
# MAGIC Follow these steps to view and configure your dashboard:
# MAGIC
# MAGIC 1. Navigate to **Lesson 6 Files**: [Task Files/Lesson 6 Files]($./Task Files/Lesson 6 Files) to locate the input file.
# MAGIC 2. Locate the **input_file**. This file will assist in generating a user-specific dashboard JSON file.
# MAGIC 3. Run the command below to automatically create the dashboard from the input file.

# COMMAND ----------

DA.dashboard_creation_from_input()

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Click the folder icon ![folder_icon.png](./Includes/images/folder_icon.png) on the left; you will see your dashboard along with other lab/demo notebooks.
# MAGIC 5. Ensure the dashboard name matches the one shown in the cell output above. Click the dashboard to open it.
# MAGIC 6. In the top left, click **Edit draft** to view and modify your dashboard.
# MAGIC 7. In the top right, make sure **shared_warehouse** is selected for compute. Do not use "unknown warehouse." Wait for the SQL Warehouse to start so your dashboard can render.
# MAGIC 8. Click the **Data** tab on the left. Verify that the following tables are selected:
# MAGIC    - `customers_orders_ny_gold`
# MAGIC    - `customers_orders_va_gold`
# MAGIC    - `customers_sales_summary_gold`
# MAGIC 9. Run queries on each table in the query box to gain insights. Ensure your catalog is set to **dbacademy** and your schema is your specific **labuser** schema.
# MAGIC 10. Click **Publish**. Here, you will find options for sharing dashboard permissions. Your dashboard was automatically published by the command above. But, if you make any changes, be sure to publish the dashboard again to update it.
# MAGIC
# MAGIC       **Note:** Publishing the dashboard is essential to use it in your job tasks.
# MAGIC
# MAGIC This ensures your dashboard is connected to the correct data and compute resources.

# COMMAND ----------

# MAGIC %md
# MAGIC #### I2. Adding a Dashboard Task to Your Job
# MAGIC This dashboard was precreated for you within the classroom setup script. Creating dashboards are outside the scope of the course.
# MAGIC
# MAGIC 1. In your job, click **Add task** and select **Dashboard**. Configure the task as follows:
# MAGIC
# MAGIC | Setting        | Instructions                                                                 |
# MAGIC |----------------|------------------------------------------------------------------------------|
# MAGIC | Task name      | Enter **refreshing_retail_dashboard**                                        |
# MAGIC | Type           | Ensure **Dashboard** is selected                                             |
# MAGIC | Dashboard      | Select your dashboard from the list of available dashboards. The name of your dashboard will be shown in the output cell of the dashboard creation command.                                                |
# MAGIC | SQL warehouse  | Select your **Warehouse** from the dropdown                                  |
# MAGIC | Subscribers    | Select email address from drop-down to receive dashboard snapshots. In our learning environment, you will not be able to add additional emails.                    |
# MAGIC | Depends on     | Select **transforming_customers_sales_table** and **transforming_customers_orders_data** |
# MAGIC | Dependencies   | Set to **All Succeeded**                                                     |
# MAGIC
# MAGIC 2. Click on **Save task**.
# MAGIC
# MAGIC ![Lesson06_dashboard_task.png](./Includes/images/Lesson06_dashboard_task.png)
# MAGIC
# MAGIC 3. Click on **Run Now** and wait for run to get completed.
# MAGIC
# MAGIC
# MAGIC **NOTE:** Please ensure that your dashboard's data section includes all gold tables (tables with the `gold` suffix from your schema) and that your dashboard is connected to your SQL Warehouse.

# COMMAND ----------

# MAGIC %md
# MAGIC #### I3. Analyze Retail Dashboard
# MAGIC After the run is complete, check your email. You should have received an email from Databricks containing the Retail_Dashboard.

# COMMAND ----------

# MAGIC %md
# MAGIC ## J. Querying Lakehouse System Tables
# MAGIC Databricks provides system catalogs that contain metadata about billing, access, Lakehouse operations, compute resources, and more. For this course, we will focus on querying the billing and Lakehouse operation details.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Start by seeing which different schemas are present under the catalog `system`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN system

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Begin by viewing the different tables available in the `lakeflow` schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN system.lakeflow

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Let's join the `jobs` and `job_task_run_timeline` tables to gain insights about recently executed jobs.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT jobs.workspace_id, 
# MAGIC         jobs.name as job_name,
# MAGIC         jobs.job_id,
# MAGIC         timeline.run_id,
# MAGIC         timeline.period_start_time,
# MAGIC         timeline.period_end_time,
# MAGIC         timeline.task_key,
# MAGIC         timeline.result_state 
# MAGIC FROM system.lakeflow.jobs as jobs
# MAGIC INNER JOIN
# MAGIC system.lakeflow.job_task_run_timeline as timeline
# MAGIC ON jobs.job_id = timeline.job_id
# MAGIC WHERE lower(jobs.name) LIKE 'demo_06_retail_job_%'
# MAGIC ORDER BY timeline.period_start_time
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Note: You can query, join, and filter different available system tables to find valuable insights. This is a broad topic and outside the scope of this course.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Additional Resources
# MAGIC If you want to learn more about Jobs system tables, refer to the following documentation:
# MAGIC https://docs.databricks.com/aws/en/admin/system-tables/jobs#jobs
# MAGIC
# MAGIC To explore the various available system tables, their relationships, and other related details, see:
# MAGIC https://docs.databricks.com/aws/en/admin/system-tables
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2026 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>