# 📅 Project Planning & Methodology
> This document outlines the strategy, task distribution, and timeline of the HMS (Hospital Management System).

## Work Breakdown Structure (WBS)
The project is divided into 6 main phases, starting from initial environment setup to the final handover and documentation. Each task has been assigned an estimated duration based on the complexity of the Hospital requirements.

### Detailed Planning Table
| Task          | Subtask                                                               | Start Date| End Date  | Est. Hours| Real Hours| Status|
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **1. Planning** | Project scope definition, requirements analysis & group doc setup   | 01/04     | 01/04     | 4h        | 5h        | [x]   |
| | Tech stack research (PostgreSQL 18, Python libraries & PowerBI)                     | 02/04     | 06/04     | 6h        | 5h        | [x]   |
| | Creation of detailed planning doc, WBS and Gantt chart (*No Gantt*)                 | 07/04     | 08/04     | 6h        | 7h        | [x]   |
| | Local environment setup: Git repo, VS Code & Python Virtual Env (venv)              | 08/04     | 09/04     | 6h        | 2h        | [x]   |
| **2. DB Design** | Entity-Relationship (ER) Diagram design based on Annex 1           | 10/04     | 13/04     | 6h        | 9h        | [x]   |
| | Relational Model transformation, normalization (3NF) & mapping                      | 13/04     | 14/04     | 4h        | 2h        | [x]   |
| | DDL Scripting: Table creation, Primary Keys, Foreign Keys & Constraints             | 14/04     | 15/04     | 8h        | 2h        | [x]   |
| | Data Dictionary creation & Database indexing strategy                               | 15/04     | 18/04     | 6h        | 4h        | [x]   |
| **3. Security** | RBAC definition: Security Matrix for Doctors, Admins & Patients     | 18/04     | 18/04     | 4h        | 3h        | [x]   |
| | SQL Scripting for Users, Roles, Privileges & RLS                                    | 18/04     | 20/04     | 6h        | 5h        | [x]   |
| | Implementation of SSL/TLS encrypted connections                                     | 20/04     | 21/04     | 4h        | 3h        | [ ]   |
| | Dynamic Data Masking setup for sensitive information                                | 21/04     | 22/04     | 4h        | 3h        | [ ]   |
| | Legal documentation for GDPR compliance & data privacy                              | 22/04     | 22/04     | 4h        |           | [ ]   |
| **4. HA & Ops** | Master-Slave Replication architecture design and configuration      | 23/04     | 28/04     | 10h       |           | [ ]   |
| | Automated Backup scripts development & Cloud synchronization                        | 30/04     | 04/05     | 12h       |           | [ ]   |
| | Disaster Recovery testing: Simulation of node failure & Restoration                 | 04/05     | 06/05     | 8h        |           | [ ]   |
| **5. Coding** | Developing the Scaffolding and base documentation of Back-end            | 07/05     | 09/05     | 6h        |           | [ ]   |
| | DB Connection handling                                                 | 09/05     | 12/05     | 5h       |           | [ ]   |
| |                                           Connectivity block & CRUD logic                                           |      10/05     |      11/05     |      5h     |           |    [ ]   |
| | Front-End Interface: Menus, navigation & input validation                            | 12/05     | 15/05     | 8h        |           | [ ]   |
| | Dummy Data generator (50k+ patients) with Cyrillic support                          | 17/05     | 20/05     | 8h        |           | [ ]   |
| **6. Handover** | Integration testing, bug fixing & code formatting                   | 21/05     | 23/05     | 6h        |           | [ ]   |
| | Creation of User Manual and Technical Installation Guide                            | 23/05     | 25/05     | 6h        |           | [ ]   |
| | Final Bibliography audit, Git repo cleanup & submission                             | 25/05     | 27/05     | 6h        |           | [ ]   |

## Workload Summary
* **Total Hours Estimated:** 156 Hours
* **Resource:** Yossef Errazik
* **Tracking:** The "Real Hours" column and "Status" checkboxes will be updated during the **[Session Logs](./Session_Logs.md)** to reflect real progress.
