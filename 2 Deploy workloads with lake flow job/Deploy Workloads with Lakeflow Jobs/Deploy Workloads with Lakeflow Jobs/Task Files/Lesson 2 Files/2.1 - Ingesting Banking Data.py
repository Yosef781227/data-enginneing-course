# Databricks notebook source
## INCLUDE_HEADER_TRUE
## INCLUDE_FOOTER_TRUE

# COMMAND ----------

# MAGIC %run ../../Includes/Classroom-Setup-2L

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Defining schema for our master table
# MAGIC CREATE TABLE IF NOT EXISTS bank_master_data_bronze (
# MAGIC     id STRING PRIMARY KEY,
# MAGIC     age STRING,
# MAGIC     experience STRING,
# MAGIC     income STRING,
# MAGIC     zip_code STRING,
# MAGIC     family STRING,
# MAGIC     credit_card_average STRING,
# MAGIC     education STRING,
# MAGIC     mortgage STRING,
# MAGIC     has_personal_loan STRING,
# MAGIC     has_securities_account STRING,
# MAGIC     has_cd_account STRING,
# MAGIC     is_online STRING,
# MAGIC     has_credit_card STRING
# MAGIC );

# COMMAND ----------

# MAGIC %md
# MAGIC **Note:** All columns have the data type **String**. This ensures that no data is dropped during ingestion from the source.

# COMMAND ----------

# Reading Data from Bank Loan csv file
df = spark.read.csv(
    "/Volumes/dbacademy_bank/v01/banking/loan-clean.csv",
    header=True,
    inferSchema=True
)
# Creating a Temp View
df.createOrReplaceTempView("bank_master_data")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Deleting Records 
# MAGIC DELETE FROM bank_master_data_bronze
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Insert Records into our newly created table
# MAGIC INSERT INTO bank_master_data_bronze 
# MAGIC SELECT * 
# MAGIC FROM bank_master_data