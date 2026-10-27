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
# MAGIC ## Deploy Workloads with Lakeflow Jobs
# MAGIC
# MAGIC Deploy Workloads with Lakeflow Jobs course teaches how to orchestrate and automate data, analytics, and AI workflows using Lakeflow Jobs. You will learn to make robust, production-ready pipelines with flexible scheduling, advanced orchestration, and best practices for reliability and efficiency-all natively integrated within the Databricks Data Intelligence Platform. Prior experience with Databricks, Python and SQL is recommended.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Beginner familiarity with basic cloud concepts (virtual machines, object storage, identity management)
# MAGIC - Ability to perform basic code development tasks (create compute, run code in notebooks, use basic notebook operations, import repos from git, etc.)
# MAGIC - Intermediate familiarity with basic SQL concepts (CREATE, SELECT, INSERT, UPDATE, DELETE, WHILE, GROUP BY, JOIN, etc.)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Course Agenda
# MAGIC
# MAGIC The following modules are part of the **Deploy workloads with Lakeflow Jobs** course by **Databricks Academy**.
# MAGIC
# MAGIC | # | Notebook Name |
# MAGIC | --- | --- |
# MAGIC | 1 | [1 Demo - Creating a Job Using the Lakeflow Jobs UI]($./1 Demo - Creating a Job Using the Lakeflow Jobs UI) |
# MAGIC | 2L | [2 Lab - Create your First Job]($./2 Lab - Create your First Job) |
# MAGIC | 3 | [3 Demo - Automating Workloads with Scheduling and Triggers]($./3 Demo - Automating Workloads with Scheduling and Triggers) |
# MAGIC | 4 | [4 Demo - Building Dynamic Workloads with Advanced Tasks]($./4 Demo - Building Dynamic Workloads with Advanced Tasks) |
# MAGIC | 5L | [5 Lab - Adding If-Else Task and Automating your Job]($./5 Lab - Adding If-Else Task and Automating your Job) |
# MAGIC | 6 | [6 Demo - Monitoring and Repairing Task]($./6 Demo - Monitoring and Repairing Task) |
# MAGIC | 7L | [7 BONUS LAB - Modular Orchestration]($./7 BONUS LAB - Modular Orchestration)  |
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC * To run demo and lab notebooks, you need to use the following Databricks runtime: **`17.3.x-scala2.13`**
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2026 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>