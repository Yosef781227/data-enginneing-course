# Section 7: Governance and Security — 15%

Give the right people the right view of data.

Know the catalog hierarchy, least privilege, managed/external lifecycle, row filters and column masks. Understand lineage and sharing without confusing them with access enforcement.

You should reason through a read-only grant, explain what remains after a DROP, and choose row filtering versus column masking.


## Who can use which data?

**Questions:** 11, 22, 44, 45, 61, 83, 85, 89, 96, 163, 176, 195, 197, 210, 226, 260

**Think of it like this:** A library card may let you enter the building without letting you borrow every book.

**What the question tests:** Distinguish catalog/schema traversal, object-level privileges, ownership and management of permissions. Use the least access required.

**Example:** Reading catalog.schema.table normally needs appropriate parent usage privileges plus SELECT on the table. Allowing query access is not the same as granting CREATE, MODIFY or ALL PRIVILEGES.

**Common trap:** Owning a workspace does not make every ownership-transfer statement universally valid in Unity Catalog. Separate legacy workspace-admin assumptions from current ownership/management rules. Do not assume a view grant removes all parent-usage requirements.

**Try the lab:** lab9_governance / 9a (some platform features are simulated)

**Explain without looking:** Does USE CATALOG alone grant permission to read every table?

**Self-check:** No. Access to the relevant schema and data object is also needed.


## Managed and external data

**Questions:** 23, 64, 106, 107, 165, 211, 212, 216, 248, 257

**Think of it like this:** A managed table is a storage service managing the box and its label; an external table points to a box whose storage you manage separately.

**What the question tests:** Identify who manages files, metadata and lifecycle. Distinguish locations and credentials from table privileges.

**Example:** Dropping an external table generally removes its registration while leaving underlying files. Managed-table cleanup follows the platform’s supported retention/lifecycle behaviour. An external location combines an allowed path with storage-access configuration.

**Common trap:** Do not treat DROP as identical for managed and external tables. Converting table types is a supported platform operation with requirements, not just changing an arbitrary text property.

**Try the lab:** lab9_governance / 9b (some platform features are simulated)

**Explain without looking:** If files must remain independently managed after unregistering a table, which type is relevant?

**Self-check:** An external table, provided its storage and access setup meet the requirements.


## Sharing, federation and lineage

**Questions:** 132, 142, 143, 169, 171, 184, 194, 196, 198, 199, 209

**Think of it like this:** Sharing lends access to a prepared dataset; federation asks another library a question without first copying all its books.

**What the question tests:** Distinguish controlled cross-organization sharing, querying external systems in place, and tracing where data came from.

**Example:** Delta Sharing questions concern providers, recipients and supported shared assets. Federation questions concern querying connected external systems. Lineage answers which objects supplied or consumed a dataset. Cross-region/cloud transfers can have costs.

**Common trap:** Sharing is not unrestricted write access. Supported assets depend on the recipient/protocol and version; notebook sharing is supported in specific Databricks-to-Databricks contexts. Do not generalize that capability to every recipient or assume a complete executable job is shared.

**Try the lab:** lab9_governance / 9a (some platform features are simulated)

**Explain without looking:** You must query an external database without copying its tables first. Is that primarily an ingestion or federation decision?

**Self-check:** Federation, while still checking connectivity, governance and performance constraints.


## Protect sensitive rows and columns

**Questions:** 14, 156, 161, 230, 231

**Think of it like this:** A receptionist can hide a phone number while still showing the contact’s name, or hide an entire record.

**What the question tests:** Distinguish column masking, row filtering, classification, auditing and centralized attribute-based rules.

**Example:** A mask changes what an authorized reader sees in a column. A row filter limits which records appear. An ABAC policy can use governed attributes/tags and group conditions to apply protection consistently.

**Common trap:** A comment saying ‘contains PII’ documents something; it does not itself enforce a mask or filter. Audit evidence records events; it is not the same thing as a prevention rule.

**Try the lab:** lab9_governance / 9c (some platform features are simulated)

**Explain without looking:** If users may see their own region’s records but no others, is hiding one column enough?

**Self-check:** No. That requirement concerns which rows are visible.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
