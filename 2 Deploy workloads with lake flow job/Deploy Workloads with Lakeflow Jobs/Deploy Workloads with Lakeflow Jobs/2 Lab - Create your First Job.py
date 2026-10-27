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
# MAGIC # 2 Lab - Create Your First Job
# MAGIC ####Duration: ~15 minutes
# MAGIC In this lab, you will configure a multi-task job using three notebooks.
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC By the end of this lesson, you should be able to:
# MAGIC
# MAGIC - Configure a job with multiple tasks.
# MAGIC - Get familiar with the Lakeflow Jobs UI.
# MAGIC
# MAGIC ## Lab Scenario
# MAGIC You are a Data Engineer responsible for setting up a job with multiple tasks. The job will:
# MAGIC
# MAGIC - Ingest bank master data (one task).
# MAGIC
# MAGIC - Create two tables from that data (two separate tasks).
# MAGIC
# MAGIC ## Data Overview
# MAGIC You will work with bank loan master data, which has borrower details and loan details in it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE (The cluster named 'labuser')
# MAGIC
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC
# MAGIC
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the Notebook will use **Serverless**.
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
# MAGIC
# MAGIC
# MAGIC ```
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA dbacademy.<your unique schema name>;
# MAGIC ```
# MAGIC
# MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically reference the information needed to run the course.
# MAGIC
# MAGIC **NOTE:** If you use Serverless V1 a warning will be returned. You can ignore the warning.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-2L

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Generate your Job Configuration
# MAGIC 1. Run the cell below to print out values you'll use to configure your job in subsequent steps. Make sure to specify the correct job name and files.
# MAGIC
# MAGIC     **NOTE:** The `DA.print_job_config` object is specific to the Databricks Academy course. It will output the necessary information to help you create the job.

# COMMAND ----------

DA.print_job_config(job_name_extension="Lab_02_Bank_Job", 
                    file_paths='/Task Files/Lesson 2 Files',
                    Files=[
                            '2.1 - Ingesting Banking Data',
                            '2.2 - Creating Borrower Details Table',
                            '2.3 - Creating Loan Details Table'
                        ])

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Configure a Job with Multiple Tasks
# MAGIC
# MAGIC This job will complete three simple tasks:
# MAGIC
# MAGIC 1. **File #1** – Ingest a CSV file and create the **bank_master_data_bronze** table in your schema.
# MAGIC
# MAGIC 2. **File #2** – Create a table named **borrower_details_bronze** in your schema.
# MAGIC
# MAGIC 3. **File #3** – Create a table named **loan_details_bronze** in your schema.
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Add a Single Notebook Task
# MAGIC
# MAGIC Let's start by scheduling the first notebook [Task Files/Lesson 2 Files/2.1 - Ingesting Banking Data]($./Task Files/Lesson 2 Files/2.1 - Ingesting Banking Data) notebook. Click the hotlink in previous sentence to review the code.
# MAGIC
# MAGIC The notebook creates a table named **bank_master_data_bronze** in your schema from the CSV file in the volume `/Volumes/dbacademy_bank/v01/banking/loan-clean.csv`. 
# MAGIC
# MAGIC 1. Right click on the **Jobs and Pipelines** button on the sidebar and select *Open Link in New Tab*. 
# MAGIC
# MAGIC 2. Select the **Jobs & Pipeline** tab, and then click the **Create** button and choose **Job** from the dropdown.
# MAGIC
# MAGIC 3. In the top-left of the screen, enter the **Job Name** provided above to add a name for the job (must use the job name specified above).
# MAGIC
# MAGIC 4. Choose **Notebook** from the recommended task. If it's not in the recommended list, select it by clicking **+Add another task type**.
# MAGIC
# MAGIC 5. Configure the task as specified below. You'll need the values provided in the cell output above for this step.
# MAGIC
# MAGIC
# MAGIC | Setting | Instructions |
# MAGIC |--|--|
# MAGIC | Task name | Enter **ingesting_master_data** |
# MAGIC | Type | Choose **Notebook** |
# MAGIC | Source | Choose **Workspace** |
# MAGIC | Path | Use the navigator to specify the **File #1** path provided above (notebook **Task Files/Lesson 2 Files/2.1 - Ingesting Banking Data**) |
# MAGIC | Compute | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) <br></br>**NOTE**: When selecting your all-purpose cluster, you may get a warning about how this will be billed as all-purpose compute. Production jobs should always be scheduled against new job clusters appropriately sized for the workload, as this is billed at a much lower rate. |
# MAGIC
# MAGIC <br>
# MAGIC
# MAGIC 6. Click the **Create task** button.
# MAGIC
# MAGIC 7. #####For better performance, please enable Performance Optimized Mode in Job Details. Otherwise, it might take 6 to 8 minutes to initiate execution.
# MAGIC
# MAGIC 8. Click the blue **Run now** button in the top right to start the job.
# MAGIC
# MAGIC 9. Select the **Runs** tab in the navigation bar and verify that the job completes successfully.
# MAGIC
# MAGIC 10. From left-hand pane, select **Catalog**, navigate to your schema in the **dbacademy** catalog and confirm the table **bank_master_data_bronze** was created (you might have to refresh your schema).
# MAGIC
# MAGIC <br></br>
# MAGIC ![Lesson02_Task_1__Notebook](./Includes/images/Lesson02_Task_1_Notebook.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Add the Second Task to the Job
# MAGIC
# MAGIC Now, configure a second task that depends on the first task, **Ingesting_master_data**, successfully completing. The second task will be the notebook [Task Files/Lesson 2 Files/2.2 - Creating Borrower Details Table]($./Task Files/Lesson 2 Files/2.2 - Creating Borrower Details Table). Open the notebook and review the code.
# MAGIC
# MAGIC This notebook creates a table named **borrower_details_bronze** in your schema from the **bank_master_data_bronze** table created by the previous task.
# MAGIC
# MAGIC Steps:
# MAGIC 1. Go back to your job. On the Job details page, click the **Tasks** tab.
# MAGIC
# MAGIC 2. Click the **+ Add task** button at below the **ingesting_master_data** task and select **Notebook** from the dropdown menu.
# MAGIC
# MAGIC 3. Configure the task as follows:
# MAGIC
# MAGIC | Setting      | Instructions |
# MAGIC |--------------|--------------|
# MAGIC | Task name    | Enter **creating_borrower_details_table** |
# MAGIC | Type         | Choose **Notebook** |
# MAGIC | Source       | Choose **Workspace** |
# MAGIC | Path         | Use the navigator to specify the **File #2** path provided above (notebook **Task Files/Lesson 2 Files/2.2 - Creating Borrower Details Table**) |
# MAGIC | Compute      | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC | Depends on   | Make sure **Ingesting_master_data** (the previous task) is listed |
# MAGIC
# MAGIC 4. Click the blue **Create task** button.
# MAGIC
# MAGIC <br></br>
# MAGIC ![Lesson02_Task_2_Notebook](./Includes/images/Lesson02_Task_2_Notebook.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. Add the Third Task to the Job
# MAGIC
# MAGIC Now, configure a third task that depends on the first task, **Ingesting_master_data**, successfully completing. The third task will be the notebook [Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table]($./Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table). Open the notebook and review the code.
# MAGIC
# MAGIC This notebook creates a table named **loan_details_silver** in your schema from the **bank_master_data_bronze** table created by the previous task.
# MAGIC Also, Pay close attention to the final few commands, these set the output task value.
# MAGIC
# MAGIC Steps:
# MAGIC 1. In your job select the  **+ Add task** button below your tasks and select **Notebook** from the dropdown menu.
# MAGIC
# MAGIC 3. Configure the task as follows:
# MAGIC
# MAGIC | Setting      | Instructions |
# MAGIC |--------------|--------------|
# MAGIC | Task name    | Enter **creating_loan_details_table** |
# MAGIC | Type         | Choose **Notebook** |
# MAGIC | Source       | Choose **Workspace** |
# MAGIC | Path         | Use the navigator to specify the **File #3** path provided above (notebook **Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table**) |
# MAGIC | Compute      | From the dropdown menu, select a **Serverless** cluster (We will be using Serverless clusters for jobs in this course. You can also specify a different cluster if required outside of this course) |
# MAGIC | Depends on   | Make sure that only **Ingesting_master_data** (the previous task) is selected, and not **Creating_borrower_details_table**|
# MAGIC | Run If Dependencies | Select **All Succeeded** from drop down|
# MAGIC | Create task | Click **Create task** |
# MAGIC
# MAGIC #####For better performance, please turn on Performance Optimized Mode in Job Details.
# MAGIC
# MAGIC #####Performance Optimized Mode
# MAGIC Enables fast compute startup and improved execution speed.
# MAGIC
# MAGIC #####Standard Mode
# MAGIC Disabling performance optimization results in startup times similar to Classic infrastructure and may reduce your cost.
# MAGIC
# MAGIC
# MAGIC <br>
# MAGIC
# MAGIC **NOTE**: If you selected your all-purpose cluster, you may get a warning about how this will be billed as all-purpose compute. Production jobs should always be scheduled against new job clusters appropriately sized for the workload, as this is billed at a much lower rate.
# MAGIC
# MAGIC <br></br>
# MAGIC ![Lesson02_Task_3_Notebook](./Includes/images/Lesson02_Task_3_Notebook.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Run the Job
# MAGIC 1. Click the blue **Run now** button in the top right to run this job. It should take a few minutes to complete.
# MAGIC
# MAGIC 2. From the **Runs** tab, you will be able to click on the start time for this run under the **Active runs** section and visually track task progress.
# MAGIC
# MAGIC 3. On the **Runs** tab confirm that the job completed successfully.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Explore and Validate the Job Tables
# MAGIC 1. In the left pane, select **Catalog**.
# MAGIC
# MAGIC 2. Expand the **dbacademy** catalog.
# MAGIC
# MAGIC 3. Expand your unique schema name.
# MAGIC
# MAGIC 4. Confirm that the job created the following tables:
# MAGIC   - **bank_master_data_bronze**
# MAGIC   - **borrower_details_silver**
# MAGIC   - **loan_details_silver**

# COMMAND ----------

# MAGIC %md
# MAGIC You can also use the `SHOW TABLES` statement to view available tables in your schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES;

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2026 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>