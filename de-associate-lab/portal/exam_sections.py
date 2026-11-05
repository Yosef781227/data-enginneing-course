"""Shared exam sections and links into the existing courses and labs."""
SECTIONS = [
    {"id": 1, "name": "Databricks Intelligence Platform", "weight": 6, "legacy": 1, "links": [("lab7_troubleshooting", "7d", "Choose compute", "5.3 / 7.4")]},
    {"id": 2, "name": "Data Ingestion and Loading", "weight": 21, "legacy": 2, "links": [("lab1_ingestion", "1c", "Load files incrementally", "1.3"), ("lab1_ingestion", "1d", "Auto Loader", "1.4")]},
    {"id": 3, "name": "Data Transformation and Modeling", "weight": 22, "legacy": 3, "links": [("lab6_transform_tuning", "6b", "Joins and unions", "6.2"), ("lab3_pipelines", "3a", "Declarative pipelines", "3.1"), ("lab5_delta_sql_streaming", "5b", "SQL and streaming", "5.4 / 5.5")]},
    {"id": 4, "name": "Working with Lakeflow Jobs", "weight": 16, "legacy": 4, "links": [("lab2_jobs", "2a", "Tasks and dependencies", "2.1 / 2.2"), ("lab2_jobs", "2d", "Repair a failed run", "2.6")]},
    {"id": 5, "name": "Implementing CI/CD", "weight": 10, "legacy": 4, "links": [("lab8_cicd_bundles", "8a", "Git workflow", "4.6 / 8.1"), ("lab8_cicd_bundles", "8b", "Bundle configuration", "4.7 / 8.2")]},
    {"id": 6, "name": "Troubleshooting, Monitoring, and Optimization", "weight": 10, "legacy": 4, "links": [("lab7_troubleshooting", "7a", "Find skew and failures", "7.1 / 7.3"), ("lab5_delta_sql_streaming", "5a", "Delta maintenance", "5.2")]},
    {"id": 7, "name": "Governance and Security", "weight": 15, "legacy": 5, "links": [("lab9_governance", "9a", "Permissions", "5.1 / 9.1"), ("lab9_governance", "9b", "Managed and external tables", "9.2")]},
]
LEGACY = ["Databricks Intelligence Platform", "Development and Ingestion", "Data Processing & Transformations", "Productionizing Data Pipelines", "Data Governance & Quality"]
