# Section 5: Implementing CI/CD — 10%

Deliver changes repeatably.

Git tracks code changes. Bundles describe deployable resources and environment differences. Validation, deployment and execution are three different actions.

You should explain a branch-to-review workflow, identify bundle resources/targets and choose validate, deploy or run.


## Version control and collaboration

**Questions:** 35, 46, 94, 97

**Think of it like this:** Git is the shared history of a team’s recipe book. A branch is a separate working copy of that history.

**What the question tests:** Distinguish creating a branch, committing locally, pushing to a remote, pulling changes and reviewing a pull request.

**Example:** Make a branch, edit, commit, push, request review, then merge through the team’s process. Pulling brings remote changes into your working history; pushing sends your changes to the remote.

**Common trap:** A notebook revision history is not identical to a full Git collaboration workflow. Some operations depend on the Git provider and current workspace integration.

**Try the lab:** lab8_cicd_bundles / 8a (some platform features are simulated)

**Explain without looking:** A colleague pushed a change. Which direction must information move for you to receive it?

**Self-check:** From the remote repository into your working copy, using the appropriate pull/update workflow.


## Deploy the same project safely

**Questions:** 136, 137, 189, 190, 208, 214, 228, 242, 244, 249, 262, 271, 277

**Think of it like this:** A bundle is a labelled deployment package: the same recipe with different delivery addresses for dev and production.

**What the question tests:** Recognize project configuration, resources, variables, targets and the difference between validation, deployment and execution.

**Example:** databricks.yml is the main configuration. Targets can override environment-specific values. `databricks bundle validate` checks configuration; `deploy` creates or updates resources; `run` starts a named resource.

**Common trap:** Deploying a job does not mean it executed. Do not hard-code production secrets into versioned configuration. A bundle is more than a standalone notebook file.

**Try the lab:** lab8_cicd_bundles / 8b (some platform features are simulated)

**Explain without looking:** A job appeared after deployment but has no run. What distinction explains this?

**Self-check:** Resource deployment and workload execution are separate steps.


## Sources

Local curriculum: ../../curriculum.md; official objective map: ../exam-guide-map.md

Current exam outline: https://www.databricks.com/learn/certification/data-engineer-associate

Post-May 2026 guide: https://www.databricks.com/sites/default/files/2026-05/databricks-certified-data-engineer-associate-exam-guide-may-2026.pdf

These learning explanations do not independently certify the third-party answer key.
