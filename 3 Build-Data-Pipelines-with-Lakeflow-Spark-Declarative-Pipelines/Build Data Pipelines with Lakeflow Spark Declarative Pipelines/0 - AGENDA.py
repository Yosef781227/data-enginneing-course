# Databricks notebook source
# MAGIC %md
# MAGIC ![Databricks Academy](./Includes/images/common/db-academy.png)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Build Data Pipelines with Lakeflow Spark Declarative Pipelines (SDP)
# MAGIC
# MAGIC This course introduces users to the essential concepts and skills needed to build data pipelines using Lakeflow Spark Declarative Pipelines (SDP) in Databricks for incremental batch or streaming ingestion and processing through multiple streaming tables and materialized views. Designed for data engineers new to Spark Declarative Pipelines, the course provides a comprehensive overview of core components such as incremental data processing, streaming tables, materialized views, and temporary views, highlighting their specific purposes and differences.
# MAGIC
# MAGIC Topics covered include:
# MAGIC
# MAGIC - Developing and debugging ETL pipelines with the multi-file editor in Spark Declarative Pipelines using SQL (with Python code examples provided)
# MAGIC
# MAGIC - How Spark Declarative Pipelines track data dependencies in a pipeline through the pipeline graph
# MAGIC
# MAGIC - Configuring pipeline compute resources, data assets, trigger modes, and other advanced options
# MAGIC
# MAGIC Next, the course introduces data quality expectations in Spark Declarative Pipelines, guiding users through the process of integrating expectations into pipelines to validate and enforce data integrity. Learners will then explore how to put a pipeline into production, including scheduling options, and enabling pipeline event logging to monitor pipeline performance and health.
# MAGIC
# MAGIC Finally, the course covers how to implement Change Data Capture (CDC) using the AUTO CDC INTO syntax within Spark Declarative Pipelines to manage slowly changing dimensions (SCD Type 1 and Type 2), preparing users to integrate CDC into their own pipelines.

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Workspace Setup Information

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### A1. Databricks Provided Vocareum Workspace (Recommended)
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC - If you are running this notebook in a <strong>Databricks Academy provided Vocareum workspace</strong>, your Unity Catalog catalog is already created for you.
# MAGIC
# MAGIC - Your catalog name matches your Vocareum username and looks like: <strong>labuser12345</strong> (series of unique numbers)
# MAGIC
# MAGIC - If a <strong>Marketplace</strong> dataset is required, the share is already installed and available in the workspace.
# MAGIC
# MAGIC   </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ### A2. Databricks Free Edition or Outside Workspaces (*as is*)
# MAGIC
# MAGIC ##### Databricks Free Edition or Other Workspaces may work for this, but it is provided **as is** and support is not guaranteed.  
# MAGIC
# MAGIC Some features may not be available depending on the capabilities of Databricks Free Edition or your Workspace.
# MAGIC
# MAGIC Please read below to setup your environment
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC <div style="color:#333;">
# MAGIC
# MAGIC #### Catalog Information
# MAGIC
# MAGIC - If you are running this notebook in your own Databricks workspace or Databricks Free Edition, the setup will <strong>create a Unity Catalog catalog and schema for you</strong>. 
# MAGIC
# MAGIC - The <strong>Create Catalog</strong> permission is required.
# MAGIC
# MAGIC - The catalog name is derived from your Databricks username and follows this pattern: <strong>labuser_username</strong>
# MAGIC
# MAGIC #### Access Marketplace Data
# MAGIC
# MAGIC Marketplace data is not required.
# MAGIC
# MAGIC </div>
# MAGIC </div>
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #ff9800;
# MAGIC   background: #fff3e0;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC
# MAGIC   <strong style="display:block; color:#e65100; margin-bottom:6px; font-size: 1.1em;">
# MAGIC     Troubleshooting Setup - Your Workspace Can't Create Catalogs
# MAGIC   </strong>
# MAGIC <details>
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC If you do not have permission to create a new catalog but already have one available, you can explicitly specify an existing catalog by setting the `catalog_forced` value to your specific catalog: `my_catalog = build_user_catalog(catalog_forced=None)`
# MAGIC
# MAGIC This function is at the end of notebook `./Includes/Classroom-Setup-Common-Python`
# MAGIC
# MAGIC   </div>
# MAGIC </details>
# MAGIC </div>
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #f44336;
# MAGIC   background: #ffebee;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC <strong style="display:block; color:#c62828; margin-bottom:6px; font-size: 1.1em;">Do Not Run in Production Environments</strong>
# MAGIC
# MAGIC <div style="color:#333;">
# MAGIC <ul>
# MAGIC <li>Only run this course in <strong>development or sandbox workspaces</strong>.</li>
# MAGIC <li>Do not run in production environments. The setup scripts create catalogs, schemas, and pipelines in your workspace.</li>
# MAGIC </ul>
# MAGIC </div>
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC ## B. Course Agenda
# MAGIC
# MAGIC The following modules are part of the **Data Engineer Learning Path** by Databricks Academy.
# MAGIC
# MAGIC <div style="max-width: 1200px; margin: 0 auto; font-family: sans-serif;">
# MAGIC <div style="background: #F9F7F4; border-radius: 10px; padding: 20px 24px; box-shadow: 0 2px 8px rgba(27,49,57,0.06);">
# MAGIC
# MAGIC <style>
# MAGIC .agenda-table td, .agenda-table th {
# MAGIC   font-size: 14pt !important;
# MAGIC }
# MAGIC </style>
# MAGIC
# MAGIC <table class="agenda-table" style="width: 100%; border-collapse: collapse; line-height: 1.5;">
# MAGIC   <thead>
# MAGIC     <tr style="background: #1B5162; color: white;">
# MAGIC       <th style="padding: 10px 14px; text-align: center; border: 1px solid #EEEDE9; width: 50px;">#</th>
# MAGIC       <th style="padding: 10px 14px; text-align: center; border: 1px solid #EEEDE9; width: 80px;">Type</th>
# MAGIC       <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">Module Name</th>
# MAGIC     </tr>
# MAGIC   </thead>
# MAGIC   <tbody>
# MAGIC     <tr style="background: white;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">1</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Demo</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Course Setup and Creating a Pipeline</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: #F9F7F4;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">2</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Demo</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Developing a Simple Pipeline</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: white;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">3</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Demo</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Adding Data Quality Expectations</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: #F9F7F4;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">4</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Lab</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Create a Pipeline</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: white;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">5</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Demo</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Deploying a Pipeline to Production</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: #F9F7F4;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">6</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Demo</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Change Data Capture with AUTO CDC with SCD TYPE 1</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: #F9F7F4;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">7</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Summary</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">Summary and Next Steps</td>
# MAGIC     </tr>
# MAGIC     <tr style="background: #F9F7F4;">
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center; font-weight: 700; color: #1B5162;">8</td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9; text-align: center;"><span style="background: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Lab</span></td>
# MAGIC       <td style="padding: 8px 14px; border: 1px solid #EEEDE9;">AUTO CDC INTO with SCD Type 1</td>
# MAGIC     </tr>
# MAGIC   </tbody>
# MAGIC </table>
# MAGIC
# MAGIC </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC
# MAGIC ### Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC <div style="
# MAGIC   border-left: 4px solid #1976d2;
# MAGIC   background: #e3f2fd;
# MAGIC   padding: 14px 18px;
# MAGIC   border-radius: 4px;
# MAGIC   margin: 16px 0;
# MAGIC ">
# MAGIC   <div style="color:#333;">
# MAGIC
# MAGIC - Use Databricks Runtime version: **`Serverless V5`** for running all demo and lab notebooks.
# MAGIC
# MAGIC   </div>
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC
# MAGIC &copy; <span id="dbx-year"></span> Databricks, Inc. All rights reserved.
# MAGIC Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
# MAGIC <script>
# MAGIC   document.getElementById("dbx-year").textContent = new Date().getFullYear();
# MAGIC </script>