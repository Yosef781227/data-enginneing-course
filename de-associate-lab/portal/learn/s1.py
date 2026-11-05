"""Section 1 · Databricks Intelligence Platform — learn-first notes and a 'know this first' card per question."""

INTRO = """
This section asks one big question: **what is Databricks made of, and which machine should run my work?**

It is only **6% of the exam (about 3 questions)**, but the ideas come back in every other section.
The 37 practice questions test just **three ideas**:

1. **The lakehouse** — why Databricks keeps all data in one place, and what Delta Lake adds.
2. **Choosing compute** — which kind of machine (cluster, serverless, SQL warehouse) fits a job.
3. **Notebooks** — how to mix Python and SQL.

Read the three notes below first. Then press **Start guided questions**: before every question you get a
short card with the one fact you need, then the question.
"""

CONCEPTS = [
    {
        "topic": "architecture",
        "title": "The lakehouse, Delta Lake and the two planes",
        "one_line": "One copy of the data, stored in your own cloud, made reliable by Delta Lake and run by Databricks.",
        "analogy": "Think of a **library**. The **books** (your data) stay on *your* shelves. Databricks runs the "
                   "**front desk** (website, catalogue, scheduling). The **reading rooms** (machines) are where the actual reading happens.",
        "facts": [
            ("Lakehouse = lake + warehouse in one",
             "A **data lake** is cheap storage for any file. A **data warehouse** is fast and reliable for SQL. "
             "A **lakehouse** gives both in one system, so teams stop keeping separate copies (silos). "
             "Everyone reads the **same tables → one source of truth**, so reports agree."),
            ("Delta Lake is what makes the lake reliable",
             "Delta Lake is the **storage layer** (table format) under every table. It adds:\n"
             "- **ACID transactions** — a write fully succeeds or fully fails. Nobody sees half-written data → **better data quality**.\n"
             "- **Schema enforcement** — wrong-shaped writes are blocked. **Schema evolution** — new columns can be added.\n"
             "- **Time travel** — read or restore an older version → easy **rollback** and an audit history.\n"
             "- **Batch and streaming** on the same table."),
            ("Open source and open formats → no vendor lock-in",
             "Delta Lake and Spark are open source, and the files are open formats (Parquet). Other tools can read them, "
             "so you are **not trapped** with one company."),
            ("Control plane = Databricks' side",
             "Databricks runs the **web application** (the UI you click), **stores your notebooks** (encrypted), schedules "
             "jobs, **orchestrates compute** (starts/stops clusters) and runs **Unity Catalog** (permissions, lineage, audit)."),
            ("Compute plane = where the code runs. Your data stays in your cloud.",
             "Clusters — the **driver** and **worker** machines — run in the compute plane. In the classic setup, that is "
             "**your cloud account**. Your **data** always lives in **your cloud storage** (S3 / ADLS / GCS). "
             "So a scheduled notebook is **stored in the control plane** and **executes in the compute plane**."),
        ],
        "table": "| Lives in the **control plane** (Databricks) | Lives in **your cloud account** |\n|---|---|\n"
                 "| Web application · notebooks · job scheduler | Your data (cloud storage) |\n"
                 "| Compute orchestration · Unity Catalog | Classic clusters: driver + workers (VMs) |",
        "traps": [
            "“Stores data in open formats” and “allows SQL” are true, but they are **not** what improves *data quality*. ACID does.",
            "The **driver node** is not in the control plane. It is a machine in the compute plane.",
            "Unity Catalog governs who can see data. It is **not** a storage format; Delta Lake is.",
        ],
        "slides": [],
        "source": "beyond course material — the control/compute plane split is not in your 4 courses.",
    },
    {
        "topic": "compute",
        "title": "Choosing the right compute",
        "one_line": "Match the machine to the work: people developing, a scheduled job, or many SQL users.",
        "analogy": "Choosing compute is like choosing **transport**. A **rental car you keep all day** (all-purpose cluster) "
                   "is handy while you explore. A **taxi for one trip** (job cluster) is cheaper for a fixed route. "
                   "**Ride-hailing** (serverless) appears in seconds and you never park it. A **bus** (SQL warehouse) carries many SQL passengers.",
        "facts": [
            ("All-purpose (interactive) cluster → people developing",
             "You start it, attach notebooks, run cells and get **real-time results**. Good for exploring, testing, debugging. "
             "It stays on until you stop it (or it times out), so it costs more. Turn on **autoscaling** if usage spikes."),
            ("Job cluster → scheduled production runs",
             "Created when the job starts and **shut down when it ends**, so you never pay for idle time. It is the classic "
             "choice for a **tested notebook going to production** and for **nightly / daily batch ETL**. It can autoscale."),
            ("Single-node cluster → small data, interactive",
             "Only a driver, no workers. Fine for **small data** while working interactively; not for big data or scaling."),
            ("Pools → faster start",
             "A pool keeps **idle machines ready**, so clusters start much faster. Use it when something must **run or refresh as quickly as possible**."),
            ("Spot instances → cheaper, may be interrupted",
             "Spare cloud machines at a big discount. The cloud can take them back. Fine for **cheap, short, simple** jobs "
             "that can handle a rare interruption."),
            ("Serverless compute → Databricks manages everything",
             "Starts in **seconds**, **scales automatically**, applies **Photon**, upgrades the runtime and **stops when idle** — "
             "no clusters to manage, no idle cost. Chosen when a question says *minimal operational overhead*, *no cluster "
             "management*, *wind down quickly*, or *high availability without tuning*.\n"
             "- Needs **Unity Catalog** and a **region that supports it**.\n"
             "- Supports **Python and SQL** (not R or Scala) — so a Python pipeline on the latest runtime + UC is the easiest to move first."),
            ("SQL warehouses → SQL and BI dashboards",
             "- **Serverless SQL warehouse**: near-instant start, autoscaling, pay only while queries run, Photon. Best for "
             "**many BI users / high concurrency / fluctuating load**.\n"
             "- **Pro SQL warehouse**: runs **in your own cloud account/network**, so it can reach data in a "
             "**custom (private) network**.\n"
             "- **Classic SQL warehouse**: basic, fewer performance features."),
        ],
        "table": "| The question says… | Pick |\n|---|---|\n"
                 "| develop, test, debug, real-time results | All-purpose (interactive) |\n"
                 "| scheduled, production, nightly batch | Job cluster / jobs compute |\n"
                 "| …and no cluster management, no idle cost | **Serverless** jobs compute |\n"
                 "| start as fast as possible (classic) | Pools |\n"
                 "| small data, one person | Single node |\n"
                 "| many SQL / BI users, instant start | Serverless SQL warehouse |\n"
                 "| SQL on data in the company's private network | Pro SQL warehouse |",
        "traps": [
            "All-purpose clusters are **not** for scheduled production — they cost more and stay on.",
            "“Cheapest” for a small production job is a **job cluster**, not an interactive one.",
            "Serverless needs Unity Catalog and region support; that is part of the right answer when asked about constraints.",
        ],
        "slides": [["c2", 28, "Jobs can run on different compute"], ["c2", 29, "Serverless performance mode"], ["c2", 30, "Selecting compute for a task"]],
        "source": "Course 2, slides 28–30 (compute for jobs). Pools, spot and SQL warehouse types are beyond course material.",
    },
    {
        "topic": "notebooks",
        "title": "Notebooks and languages",
        "one_line": "A notebook has one default language, and each cell can switch language with a magic command.",
        "analogy": "A notebook is a **bilingual meeting**: the meeting has a main language, but any one speaker can say "
                   "“**%sql**, I'll speak SQL now” — for **their turn only**.",
        "facts": [
            ("Magic commands switch the language of one cell",
             "Put **`%sql`**, `%python`, `%scala`, `%r` or `%md` on the **first line** of a cell. Only that cell changes; "
             "the other cells keep the notebook's default language."),
            ("One language per cell",
             "You cannot mix Python and SQL lines inside the same cell. To use a Python variable in SQL, stay in Python: "
             "`spark.sql(f\"SELECT * FROM t WHERE id = {my_id}\")`."),
        ],
        "table": "",
        "traps": ["Changing the notebook's default language changes **every** cell — not what you want for one SQL cell."],
        "slides": [],
        "source": "Used throughout all 4 courses' notebooks.",
    },
]

# The order questions come in during guided practice (similar questions sit next to each other).
ORDER = [
    # architecture
    54, 69, 29, 47, 95, 9, 91, 140, 4, 251, 203, 3, 93, 74, 15, 241,
    # compute
    166, 272, 49, 77, 193, 259, 157, 92, 148, 173, 191, 275, 207, 192, 180, 167, 220, 162, 201,
    # notebooks
    56, 147,
]

# "Know this first" — the one fact each question needs. It teaches the rule; it does not name the option letter.
BEFORE = {
    54: "Teams often keep a **data lake** for raw files and a **data warehouse** for SQL reports — two silos. "
        "The architecture that combines both into **one system** is the **data lakehouse**.",
    69: "Same idea as the last question, worded differently: the thing that **unifies** separate lake and warehouse "
        "systems is an *architecture*, the **lakehouse**. Delta Lake is a storage format *inside* it, not the architecture itself.",
    29: "Different reports usually mean **different copies of the data**. A lakehouse lets every team read the **same "
        "tables** — one **source of truth** — so the numbers agree.",
    47: "Open source + open file formats means **other tools can read your data**. You can leave or mix vendors at any time: "
        "that is called **avoiding vendor lock-in**.",
    95: "Same idea again: the benefit of **open source** is **freedom from one vendor** (no lock-in).",
    9: "Data quality improves when writes **cannot leave tables half-finished or broken**. That guarantee is called "
       "**ACID transactions**. Open formats and SQL are nice, but they don't stop bad writes.",
    91: "Same as before: the lakehouse feature that improves **data quality** is **ACID-compliant transactions**.",
    140: "The **storage layer** that gives **ACID transactions** and **schema enforcement** is **Delta Lake**. "
         "(Unity Catalog is governance, not storage.)",
    4: "Which benefit comes from **Delta Lake** itself? One Delta table can be written and read by **batch and streaming** jobs "
       "at the same time. Multiple languages and live collaboration come from Spark and notebooks, not from Delta.",
    251: "A **Delta table** natively does all three: **blocks bad-schema writes** (enforcement), **adds new columns** when "
         "allowed (evolution), and **keeps old versions** (time travel). No need to recreate the table.",
    203: "Rollback and audit history → **Delta Lake time travel** (on top of ACID). Governed, consistent access and "
         "lineage for AI and BI → **Unity Catalog**. Look for the option that uses both.",
    3: "The **control plane** is Databricks' own side. It hosts the **web application** (the UI) completely. "
       "Driver and worker nodes are machines in the **compute plane**.",
    93: "Same question as before: the **web application** is hosted completely in the control plane.",
    74: "In the control plane Databricks runs **services**: the UI, the job scheduler, **compute orchestration** (starting and "
        "stopping clusters) and **Unity Catalog**. Virtual machines and the compute itself are in the compute plane.",
    15: "Your **data** never moves into Databricks' account — it stays in **your own cloud storage**. The web app, "
        "notebooks and cluster metadata are managed by Databricks.",
    241: "A notebook is **stored (encrypted) in the control plane**. When the job runs, the code **executes on a cluster in "
         "the compute plane**.",
    166: "A small proof of concept in a notebook, wanting **real-time results** → interactive **all-purpose** cluster. "
         "When usage **spikes**, **autoscaling** adds workers automatically.",
    272: "During **development** you want to run cells, change code and debug immediately → **interactive (all-purpose) compute**. "
         "The nightly job comes later and can use job compute then.",
    49: "A **single-node** cluster has only a driver. It is good when you work **interactively with a small amount of data**.",
    77: "A **tested** notebook that must now run **on a schedule in production** → a **job cluster** (made for the run, shut "
        "down after, cheaper than all-purpose).",
    193: "Large, **scheduled daily ETL** whose size varies → **job cluster** with autoscaling: created per run, sized to "
         "the work, then terminated.",
    259: "**Nightly**, predictable batch ETL; pay only while it runs → a **job compute cluster triggered by a scheduled workflow**.",
    157: "For a **small, simple production** job, the cheapest choice is a **job cluster**, made cheaper still with **spot "
         "instances** (discounted spare machines; a rare interruption is acceptable). Photon speeds up heavy work, which this job does not have.",
    92: "**Pools** keep idle machines ready so clusters **start faster**. Pick pools when something must be "
        "**refreshed as quickly as possible** — not for version control or sharing.",
    148: "Small ad-hoc Python scripts, run **often**, that must **wind down quickly** → **serverless compute**: starts in "
         "seconds and stops when idle.",
    173: "Scale **automatically**, **no manual cluster management**, Databricks handles resources → **serverless compute**.",
    191: "Strict SLA, high availability, and **no overhead of managing or tuning clusters** → **Databricks serverless compute**.",
    275: "Scheduled batch jobs **plus** “minimize operational overhead” and “no idle cluster costs” → **serverless jobs compute** "
         "(classic job clusters still need sizing and management).",
    207: "Auto-select instances, autoscaling, Photon and runtime upgrades handled for you → **serverless compute for "
         "workflows**. Its constraints: **Unity Catalog enabled** and a **supported region**.",
    192: "Serverless supports **Python and SQL** and needs **Unity Catalog** and a recent runtime. The easiest and most "
         "valuable thing to move first is a **frequent Python pipeline already on the latest runtime with UC**.",
    180: "Serverless compute supports **SQL and Python**. R, Scala and Java are not supported on it.",
    167: "SQL on fluctuating load, **automatic scaling**, nothing to provision, **pay only while queries run** → "
         "**Serverless SQL warehouse**.",
    220: "Hundreds of BI users, high concurrency, **near-instant start**, autoscaling, best SQL speed → "
         "**Serverless SQL warehouse with Photon**.",
    162: "The key words are “database **inside the company's custom-defined network**”. A **Pro SQL warehouse** runs in "
         "**your cloud account / network**, so it can reach that data, and it has the performance features.",
    201: "Same as the previous question: SQL on data in the company's **private network** → **Pro SQL warehouse**.",
    56: "To run SQL in **one cell** of a Python notebook, put the magic command **`%sql`** on the **first line** of that cell. "
        "Other cells stay Python.",
    147: "A cell runs in **one language only**. Mixing Python and SQL lines in one cell fails. "
         "Use `spark.sql(f\"…{var}…\")` in a Python cell instead.",
}
