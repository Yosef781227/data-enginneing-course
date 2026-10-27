# Databricks notebook source
# MAGIC %run ./Classroom-Setup-3

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Creating Volume 
# MAGIC CREATE VOLUME IF NOT EXISTS trigger_storage_location

# COMMAND ----------

DA.copy_data()