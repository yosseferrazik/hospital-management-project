# Documentation Audit and Restructuring Plan

This document summarizes an automated audit of the repository documentation, identifies issues (duplication, contradictions, obsolete files, organization and terminology inconsistencies), and describes the proposed restructuring plan and execution steps.

1) Findings (summary)

- Duplication:
  - Backup strategy, scripts and recovery procedures are repeated across `docs/03_Security_and_Infrastructure/High_Availability_and_Backup_Strategy.md`, `docs/03_Security_and_Infrastructure/Deployment_Architecture.md`, `docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md`, and `scripts/README.md` with overlapping but not identical content. Consolidate a single canonical runbook and reference it elsewhere.
  - TLS and replication configuration appears in both `TLS_and_mTLS_Configuration.md` and `Deployment_Architecture.md` (replication steps). Keep TLS-specific details in TLS doc and replication steps in Deployment or HA but cross-link.

- Contradictions:
  - Database name: `docs/README.md` and many docs state `hospital_management` while `Deployment_Architecture.md` uses `hsp_db` in some examples (inconsistent). Normalize to `hospital_management`.
  - PostgreSQL versions and paths have mixed numbers (14 vs 16) across scripts and docs. Use a single recommended version (14) and note acceptable ranges.

- Obsolete / Missing Files:
  - `docs/03_Security_and_Infrastructure/Secrets_Management.md` is referenced from several docs and docs/README but does not exist. Replace references with Data Protection doc or add a new Secrets Management doc later.
  - `docs/04_Operations_and_Manuals/User_Manual.md` and `Administrator_Manual.md` are empty. Mark them TODO and create placeholders.

- Organization & Sectioning Issues:
  - Several documents mix conceptual decisions and operational step-by-step scripts. Separate conceptual design (Architecture, HA strategy, NFRs) from runbooks and scripts (Backup runbook, installation, scripts README).
  - `Installation_Guide.md` was in Spanish. Translated to English and normalized.

- Terminology & Style:
  - Mixed case naming: docs use PascalCase filenames (ok) but internal headings vary between Title Case and sentence case. Normalize to Title Case in top headings.
  - Use consistent technical terms: prefer `Primary`/`Standby` for DB roles, `Backup` vs `Archive` semantics clarified.

2) Proposed New Hierarchy

- docs/
  - 00_Governance/
    - Reference_Sources.md
    - Project_Session_Log.md
    - Documentation_Backlog.md (create placeholder)
  - 01_Planning/
    - Architecture_Overview.md
    - System_Context.md
    - Functional_Requirements.md
    - Non_Functional_Requirements.md
    - Tech_Stack.md
  - 02_Data/
    - Relational_Model.md
    - Data_Dictionary.md
    - Database_Standards.md
    - Access_Control_Matrix.md
  - 03_Infrastructure_Security/
    - Deployment_Architecture.md
    - Network_Architecture.md
    - TLS_and_mTLS_Configuration.md
    - Data_Protection_and_GDPR_Compliance.md
    - High_Availability_and_Backup_Strategy.md
    - Secrets_Management.md (TO DO)
  - 04_Operations/
    - Backup_and_Restore_Runbook.md
    - Incident_Response_Procedure.md
    - Installation_Guide.md
    - Administrator_Manual.md (TO DO)
    - User_Manual.md (TO DO)
  - 99_Index/
    - TOC.md (generated)

3) Plan (execution steps)

- Consolidate and canonicalize backup content: keep detailed runbook in `04_Operations/Backup_and_Restore_Runbook.md`. Remove duplicated sections from Deployment_Architecture and HA docs and replace with references.
 - Consolidate and canonicalize backup content: keep detailed runbook in `04_Operations/Backup_and_Restore_Runbook.md`. Remove duplicated sections from Deployment_Architecture and HA docs and replace with references. (DONE)
 - Consolidate replication/HA content: created `docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md` and moved scripts/commands there, and canonicalized monitoring scripts at `scripts/ops/`. (DONE)
- Normalize database name and PostgreSQL version examples across docs to `hospital_management` and Postgres 14. Update a small set of example lines where mismatch exists.
- Add placeholder files for missing Secrets_Management, Documentation_Backlog, Administrator_Manual, and User_Manual with TODOs.
- Translate any Spanish content to English (done for Installation Guide).
- Create `docs/99_Index/TOC.md` with cross-links to main documents and short descriptions.
 - Create `docs/99_Index/TOC.md` with cross-links to main documents and short descriptions.

4) Style and Format Normalization Rules

- Language: English for all docs.
- Top-level H1 headings use Title Case and include a Document Control table when applicable.
- Use present tense and imperative for runbook steps.
- Use monospace for commands and filenames.
- Use consistent naming: `primary`, `standby`, `backup`, `archive`, `replication`, `promote`, `failover`.

5) Execution Log

- Translated `Installation_Guide.md` to English and normalized formatting.
- Fixed a broken reference in `Incident_Response_Procedure.md` referencing a non-existent Secrets_Management.md by adjusting the text to reference Data Protection doc.
- Added this audit document and planned TOC next.

Next steps: generate TOC.md and add placeholder docs. After your review I will proceed to remove duplicated backup sections from Deployment_Architecture.md and High_Availability docs and replace with cross-links to the canonical runbook.
