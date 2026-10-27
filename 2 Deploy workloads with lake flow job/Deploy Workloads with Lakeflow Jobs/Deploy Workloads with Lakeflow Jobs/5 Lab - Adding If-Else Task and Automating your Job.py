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
# MAGIC # 5 Lab - Adding If-Else Task and Automating Your Job
# MAGIC
# MAGIC #### Duration: ~15 minutes
# MAGIC
# MAGIC ## Learning Objectives
# MAGIC By the end of this lab, you will be able to:
# MAGIC * Add conditional logic to a Databricks job
# MAGIC * Schedule your job for automated execution
# MAGIC
# MAGIC ## Lab Scenario
# MAGIC You have already created two tables: **borrower_details_silver** and **loan_details_silver** from the **bank_master_data_bronze** dataset. In this lab, you will further transform these silver tables, focusing on the loan details table, and implement conditional logic to handle high-risk borrowers.

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

# MAGIC %run ./Includes/Classroom-Setup-5L

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Creating and Exploring the Starter Job
# MAGIC
# MAGIC Run the cell below to automatically create the starter job for this lab. This starter job includes all the tasks completed in **2 Lab - Create your First Job**:
# MAGIC
# MAGIC - ./Task Files/Lesson 2 Files/2.1 - Ingesting Banking Data
# MAGIC - ./Task Files/Lesson 2 Files/2.2 - Creating Borrower Details Table
# MAGIC - ./Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table
# MAGIC

# COMMAND ----------

job_tasks = [
        {
            'task_name': 'ingesting_master_data',
            'file_path': '/Task Files/Lesson 2 Files/2.1 - Ingesting Banking Data',
            'depends_on': None
        },
        {
            'task_name': 'creating_borrower_details_table',
            'file_path': '/Task Files/Lesson 2 Files/2.2 - Creating Borrower Details Table',
            'depends_on': [{'task_key':'ingesting_master_data'}]
        },
        {
            'task_name': 'creating_loan_details_table',
            'file_path': '/Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table',
            'depends_on': [{'task_key':'ingesting_master_data'}]
        }
    ]

myjob = DAJobConfig(job_name=f"Lab_05_Bank_Job_{DA.schema_name}",
                        job_tasks=job_tasks,
                        job_parameters=[])

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Explore the New Task Files
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Let's build upon the last lab by exploring the notebooks we want to add to the job. The notebooks can be found in **Task Files** > **Lesson 5 Files**.
# MAGIC
# MAGIC Use the links below to view and explore the code for each task:
# MAGIC
# MAGIC - [Task Files/Lesson 5 Files/5.1 - Processing high risk borrowers]($./Task Files/Lesson 5 Files/5.1 - Processing high risk borrowers)
# MAGIC   - This notebook identifies high-risk borrowers, processes them, and stores their data in the **high_risk_borrowers_silver** table.
# MAGIC
# MAGIC - [Task Files/Lesson 5 Files/5.2 - Processing low risk borrowers]($./Task Files/Lesson 5 Files/5.2 - Processing low risk borrowers)
# MAGIC   - This notebook identifies low-risk borrowers, processes them, and stores their data in the **low_risk_borrowers_silver** table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Adding an If/Else Conditional Task
# MAGIC
# MAGIC In this section, you will add a conditional task to your job that checks for high-risk borrowers in the **loan_details_silver** table. The relevant code can be found in [Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table]($./Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table).
# MAGIC
# MAGIC Pay close attention to the final commands, as they set the output task value. Whenever the number of borrowers with both an active loan and a credit card exceeds 100, the `risk_flag` is set to **true**.

# COMMAND ----------

# MAGIC %md
# MAGIC ### D1. Review the Notebook: Check for High-Risk Borrowers
# MAGIC
# MAGIC 1. Refer to the notebook [Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table]($./Task Files/Lesson 2 Files/2.3 - Creating Loan Details Table) to review the `risk_flag` logic for identifying high-risk borrowers in the **loan_details_silver** table.
# MAGIC
# MAGIC   - The **creating_loan_details_table** task creates the **loan_details_silver** table.
# MAGIC
# MAGIC   - Your goal is to check whether this table contains more than the allowed number of high-risk borrowers.
# MAGIC
# MAGIC   - Stores the result of this check (a boolean value) as `risk_flag` in the task output.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### D2. Create an If/Else Conditional Task
# MAGIC
# MAGIC 1. Navigate to the job that was created, go to the Tasks tab, and add a new task named **checking_for_risky_borrowers**.
# MAGIC
# MAGIC 2. Set the task type to **If/Else condition**.
# MAGIC
# MAGIC 3. Set this task to depend on the **creating_loan_details_table** task.
# MAGIC
# MAGIC 4. Select the condition by clicking on the `{}` button, then choose tasks.`creating_loan_details_table.values.my_value` and replace `my_value` with `risk_flag`.
# MAGIC
# MAGIC <!-- 5. For the condition, use the output value from the **creating_loan_details_table** task: `tasks.creating_loan_details_table.values.risk_flag` (Include the condition in double quotes) -->
# MAGIC
# MAGIC 5. Set the condition to check if this value is `== true`: `tasks.creating_loan_details_table.values.risk_flag == true`
# MAGIC
# MAGIC 6. Click on **Save Task**.
# MAGIC
# MAGIC ![Lesson05_ifelse](./Includes/images/Lesson05_ifelse.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### D3. Handle the True Condition
# MAGIC
# MAGIC 1. If high-risk borrowers are found (`risk_flag == true`), add a notebook task named **processing_high_risk_borrowers**.
# MAGIC
# MAGIC 2. This task should depend on the **True** branch of the **checking_for_risky_borrowers** task.
# MAGIC
# MAGIC 3. Use the notebook [Task Files/Lesson 5 Files/5.1 - Processing high risk borrowers]($./Task Files/Lesson 5 Files/5.1 - Processing high risk borrowers) for this condition.
# MAGIC
# MAGIC
# MAGIC ![Lesson05_if_task.png](./Includes/images/Lesson05_if_task.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### D4. Handle the False Condition
# MAGIC
# MAGIC 1. If high-risk borrowers are less than threshold (`risk_flag == false`), add a notebook task named **processing_low_risk_borrowers**.
# MAGIC
# MAGIC 2. This task should depend on the **False** branch of the **checking_for_risky_borrowers** task.
# MAGIC
# MAGIC 3. Use the notebook [Task Files/Lesson 5 Files/5.2 - Processing low risk borrowers]($./Task Files/Lesson 5 Files/5.2 - Processing low risk borrowers) for this condition.
# MAGIC
# MAGIC 4. This setup ensures your job processes high-risk and low-risk borrowers separately.
# MAGIC ![Lesson05_else_task](./Includes/images/Lesson05_else_task.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## E. Scheduling Your Job Using the Jobs UI
# MAGIC
# MAGIC Follow these steps to schedule your Databricks job:
# MAGIC
# MAGIC 1. **Open Your Job:** Go to the job you just created.
# MAGIC
# MAGIC 2. **Go to the Tasks Tab:** Make sure you are viewing the **Tasks** tab within your job.
# MAGIC
# MAGIC 3. **Expand Job Details:**  On the right side of the Jobs UI, find the **Job Details** panel.  
# MAGIC    - **NOTE:** If the panel is collapsed, click the arrow icon to expand it.
# MAGIC
# MAGIC 4. **Add a Schedule:**  In the **Schedules & Triggers** section, click **Add trigger**. You will see three scheduling options:  
# MAGIC    - **Scheduled** (run at specific times)
# MAGIC
# MAGIC    - **Continuous** (run as soon as previous run finishes)
# MAGIC
# MAGIC    - **Table Update** (run automatically whenever one or more specified tables are updated)
# MAGIC
# MAGIC    - **File arrival** (run when files arrive in a location)
# MAGIC
# MAGIC 5. **Set Up a Scheduled Run:**  
# MAGIC    - Choose **Scheduled**.
# MAGIC
# MAGIC    - Click on the **Advanced** section to see more options.
# MAGIC
# MAGIC 6. **Configure the Schedule:**  
# MAGIC    - Set the job to run **every day** at a time of your choice.
# MAGIC
# MAGIC    - Make sure to select your specific time zone.
# MAGIC
# MAGIC    - **Tip:** Set the schedule to start two minutes from your current time so you don’t have to wait long for the job to run.
# MAGIC
# MAGIC **NOTE:** Scheduling your job ensures it runs automatically at the times you specify. You can also start your job run by clicking **Run Now** at the top of your job.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## F. Validate your Job
# MAGIC
# MAGIC Check if the table **high_risk_borrowers_silver** exists under your schema.
# MAGIC
# MAGIC Also, run the below command to verify data of **high_risk_borrowers_silver**
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT count(*) FROM high_risk_borrowers_silver

# COMMAND ----------

# MAGIC %md
# MAGIC Please ensure that the number of high-risk borrowers is **143**, which should match the total row count in the **high_risk_borrowers_silver** table.

# COMMAND ----------

# MAGIC %md
# MAGIC ## G. Cancel Trigger
# MAGIC
# MAGIC Once your job has executed, make sure to **delete** the trigger under **Schedules & Triggers** on the right side of the Tasks tab. Otherwise, it will continue to run indefinitely until cancelled.

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2026 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>