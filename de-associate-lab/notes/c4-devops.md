# Course 4 — DevOps Essentials for Data Engineering (study notes)

Source: `source/text/slides/c4-devops.txt` + notebooks in `source/text/notebooks/c4-devops/`
(original zip extracted to `source/course4/`).

---
## §1 Software-engineering practices; modular PySpark  (slides 6–26; 2.1, 2.2L)
Best practices: readable code, naming conventions, **modular design**, documentation,
automated testing (unit + integration), version control + code review, CI/CD, **isolated environments**.

Modular = move logic into small functions that take a DataFrame and return a DataFrame:
```python
def convert_miles_to_km(df, new_column_name, miles_column):
    return df.withColumn(new_column_name, F.round(F.col(miles_column) * 1.60934, 2))

def uppercase_columns_names(df):
    return df.select([F.col(c).alias(c.upper()) for c in df.columns])
```
Benefits: easier maintenance, reuse across projects, each function can be **unit-tested**.
Put functions in `.py` files (e.g. `src/helpers/project_functions.py`) and import them.

---
## §2 DevOps, DataOps, MLOps, CI/CD  (slides 27–45)
- **DevOps** = collaboration between development and operations + automation.
  Loop: plan → code → build → test → release → deploy → operate → monitor.
- **DataOps** = DevOps for data engineering. **MLOps** = DevOps for ML.
- **CI (continuous integration)**: merge code often to a shared repo and **run automated tests**
  to find errors early.
- **Continuous Delivery**: auto-deploy to **staging**; deploy to **production manually**.
- **Continuous Deployment**: every change that passes tests goes to production **automatically**.
- Test pyramid: **unit** (fast, many, one function) → **integration** (components together:
  notebooks/SDP/jobs) → **system** (end-to-end, slow).

---
## §3 Planning & environment isolation  (slides 46–60; 2.3)
- Dev data = small static subset (can be synthetic/anonymized); Stage = mirrors prod structure
  & volume; Prod = live data.
- Isolate dev/stage/prod by **separate workspaces** or by **separate catalogs** in Unity Catalog
  (`dev`, `stage`, `prod`), with storage isolation and UC access control.

---
## §4 Unit tests with pytest  (slides 61–68; 2.4, 2.5L)
```python
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

def test_convert_miles_to_km():
    df = spark.createDataFrame([(1.0,), (5.0,)], ["miles"])
    actual = convert_miles_to_km(df, "km", "miles")
    expected = spark.createDataFrame([(1.0, 1.61), (5.0, 8.05)], ["miles", "km"])
    assertDataFrameEqual(actual, expected)
```
- `pytest` finds files `test_*.py` / functions `test_*` automatically; uses plain `assert`.
- In Databricks: `pytest.main([".", "-v", "-p", "no:cacheprovider"])` in a notebook;
  `sys.dont_write_bytecode = True` to avoid `.pyc` cache problems.
- Shared SparkSession via a pytest **fixture** in `conftest.py`; `@pytest.mark.parametrize` for many cases.
- Other library: `chispa`.

---
## §5 Integration tests  (slides 69–73; 2.6)
1. **SDP expectations**: same pipeline code for dev/stage/prod; configuration variable `target`
   picks the input; extra test tables use `EXPECT … ON VIOLATION FAIL UPDATE` to check row counts
   and allowed values.
2. **Lakeflow Jobs**: tasks in order — Unit_Tests (notebook running pytest) → ETL (pipeline task)
   → integration test notebook → visualization. If unit tests fail, the job stops.

---
## §6 Version control with Git folders  (slides 74–84; 2.7L)
- **Databricks Git folders** (formerly Repos): clone a remote repo (GitHub, GitLab, Azure DevOps,
  Bitbucket, AWS CodeCommit) into the workspace; commit, push, pull, branch from the UI.
- Authenticate with a **Personal Access Token (PAT)** (fine-grained recommended) or GitHub app.
- Merges / pull requests are done in the Git provider (e.g. GitHub), then **pull** in Databricks.
- Git folders support arbitrary files (`.py`, `.yml`, `.csv`…) → import modules, keep configs.
- Repos API can automate keeping a production folder on a branch/tag.

---
## §7 Continuous deployment: API, CLI, SDK, DABs  (slides 85–96; 3.1)
| Tool | Best for |
|---|---|
| REST API | any language, raw HTTP |
| Databricks CLI | one-off tasks, shell scripts (wraps REST API) |
| Databricks SDK (Python, Java, Go, R) | applications, custom automation, error handling |
| **Declarative Automation Bundles (DABs)** (formerly Databricks Asset Bundles) | **recommended** for CI/CD of jobs, pipelines etc. |
- A bundle = **YAML** (`databricks.yml`) describing resources (jobs, pipelines…), code and
  **targets** (dev / staging / prod) with variables per target. "Write once, deploy everywhere".
- CLI: `databricks bundle validate`, `databricks bundle deploy -t dev`, `databricks bundle run -t dev <job>`.
- Flow: develop locally/workspace → deploy to dev → CI (e.g. GitHub Actions) runs tests and
  deploys to staging → after review, deploy to prod.
