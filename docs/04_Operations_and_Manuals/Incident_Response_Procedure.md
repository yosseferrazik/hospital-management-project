# Incident Response Procedure

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.0          |
| Last Updated   | 2026-05-04   |

## Purpose

Provide a practical incident response framework for security, availability, integrity, and confidentiality events affecting the HMS.

## Scope

This procedure applies to incidents involving:

- Unauthorized access attempts
- Credential or secret exposure
- Suspected compromise of application or database services
- Data corruption or loss
- Backup or restore failure affecting recoverability
- Network exposure or segmentation failures
- Availability interruptions of the API or database
- Possible privacy or GDPR-relevant data breaches

## Objectives

- Detect and classify incidents quickly.
- Contain the incident with minimum additional damage.
- Preserve evidence for diagnosis and auditability.
- Restore service safely and in a controlled manner.
- Support privacy and security obligations for regulated data.
- Capture lessons learned and improve procedures after the event.

## Incident Categories

| Category                | Description                                                         | Examples                                                         |
|:----------------------- |:------------------------------------------------------------------- |:---------------------------------------------------------------- |
| Security Incident       | Event affecting authentication, authorization, or system trust      | Secret exposure, unauthorized login, privilege misuse            |
| Data Integrity Incident | Event affecting correctness or consistency of data                  | Corrupted records, accidental destructive update, failed restore |
| Availability Incident   | Event affecting system access or service continuity                 | API outage, PostgreSQL outage, replication failure               |
| Privacy Incident        | Event involving possible exposure of personal or clinical data      | Backup leak, exposed logs, unauthorized patient data access      |
| Operational Incident    | Event affecting recovery, maintenance, or controlled administration | Backup job failure, expired certificate, failed VM startup       |

## Severity Levels

| Severity | Definition                                                                 | Typical Impact                                                                                     |
|:-------- |:-------------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------- |
| Critical | Major compromise or outage affecting sensitive data or core operations     | Confirmed data breach, database unavailable, secret compromise with active risk                    |
| High     | Serious degradation or likely exposure risk requiring urgent action        | Backup failure plus no recent valid copy, suspicious admin access, standby failure during incident |
| Medium   | Contained issue affecting limited functions or requiring prompt correction | Query endpoint failure, non-critical secret handling issue, failed scheduled task                  |
| Low      | Minor issue with limited operational effect                                | Misconfiguration without exploitation, documentation mismatch, warning-level event                 |

## Roles and Responsibilities

| Role                   | Responsibility                                                           |
|:---------------------- |:------------------------------------------------------------------------ |
| Incident Coordinator   | Leads the response, tracks decisions, and coordinates actions            |
| System Administrator   | Handles service-level containment, VM access, and runtime recovery       |
| Database Administrator | Handles PostgreSQL integrity, backup validation, and restore actions     |
| Security Responsible   | Evaluates exposure, secrets impact, and containment of privileged assets |
| Documentation Owner    | Updates logs, records the timeline, and captures lessons learned         |

In small project or lab contexts, one person may temporarily fulfill multiple roles, but responsibilities should still be explicitly tracked.

## Detection Sources

Incidents may be detected through:

- Application errors during login or protected operations
- PostgreSQL connectivity failures
- Replication mismatch or standby lag
- Restore or backup validation failures
- Unexpected changes in sensitive files such as `login_credentials.enc`
- Suspicious access or privilege anomalies
- Manual operator observation during demonstrations or testing

## Response Lifecycle

The incident response process follows six main phases:

1. Identification
2. Classification
3. Containment
4. Eradication
5. Recovery
6. Post-incident review

## 1. Identification

At the time of discovery:

- Record the date and time of detection.
- Identify who detected the issue.
- Record the affected environment.
- Record the initial symptoms.
- Preserve the initial error message, log snippet, or operational observation.

Minimum incident record:

| Field           | Required Content                                |
|:--------------- |:----------------------------------------------- |
| Incident ID     | Unique local identifier                         |
| Detection time  | Date and time                                   |
| Reporter        | Person or process that found the issue          |
| Environment     | Development, lab, or future hardened deployment |
| Affected asset  | API, database, backup, VM, secret, network path |
| Initial symptom | Short factual description                       |

## 2. Classification

Classify the incident as soon as enough initial facts exist:

- Assign category
- Assign severity
- Estimate affected components
- Estimate whether personal or clinical data may be involved
- Decide whether secrets may be compromised

Immediate escalation triggers:

- Confirmed or probable exposure of patient or staff data
- Exposure of `JWT_SECRET_KEY`, `ENCRYPTION_KEY`, database admin credentials, or private TLS keys
- Database corruption affecting core tables
- Loss of both primary availability and valid recovery path

## 3. Containment

Containment actions should prioritize stopping further damage while preserving evidence.

### General Containment Actions

- Stop new writes if data corruption is suspected.
- Isolate the affected VM or service if active compromise is suspected.
- Restrict privileged access temporarily if credentials may be compromised.
- Prevent further propagation before attempting cleanup.

### Containment by Incident Type

#### Secret Exposure

- Disable or rotate the affected secret.
- Restrict access to dependent services until trust is re-established.
- Identify all systems using the exposed secret.

#### Database Integrity Incident

- Stop the application if necessary to prevent further writes.
- Preserve current database state for analysis.
- Validate the latest known-good backup before any destructive recovery action.

#### Availability Incident

- Determine whether the issue is isolated to the API, database, VM, or network path.
- Preserve logs and current runtime state before restarting services repeatedly.

#### Privacy Incident

- Restrict access to affected data immediately.
- Preserve evidence of potential exposure.
- Escalate for privacy impact assessment without delay.

## 4. Eradication

Once the incident is contained, remove the root cause where possible.

Examples:

- Remove insecure files or credentials.
- Reconfigure exposed services.
- Correct broken permissions.
- Replace compromised certificates.
- Patch or reconfigure the affected runtime service.
- Remove corrupted temporary artifacts if they are not required as evidence.

Important rule:

- Do not erase critical evidence before the scope and cause of the incident are understood.

## 5. Recovery

Recovery must restore the service in a controlled manner, not just restart components blindly.

### Recovery Principles

- Use validated backups if data restoration is needed.
- Re-enable services only after verifying that the incident cause has been addressed.
- Validate authentication, protected routes, database access, and operational queries after service restoration.
- Monitor closely after recovery for repeat symptoms.

### Recovery Options by Scenario

| Scenario             | Recovery Approach                                                                          |
|:-------------------- |:------------------------------------------------------------------------------------------ |
| API service failure  | Restart or redeploy the Flask runtime after configuration and log review                   |
| Database corruption  | Restore from validated backup or use controlled standby promotion path                     |
| Primary node failure | Promote standby if required and adjust runtime service placement                           |
| Secret compromise    | Rotate secrets, reissue tokens or certificates as appropriate, then restore normal service |
| Backup failure       | Re-establish backup generation before considering the environment fully recovered          |

## 6. Post-Incident Review

After stabilization:

- Document the final timeline.
- Record root cause or best-known cause.
- Record systems affected.
- Record actions taken.
- Record whether personal or clinical data was at risk.
- Identify preventive improvements.
- Update related runbooks or architecture documents if needed.

Post-incident review outputs:

- Incident summary
- Corrective actions
- Preventive actions
- Documentation updates required

## Evidence Handling

Evidence to preserve where applicable:

- Error messages
- Application logs
- PostgreSQL logs
- Backup validation output
- Configuration snapshots
- VM state observations
- Timestamps of key operator actions

Rules:

- Do not alter logs unnecessarily.
- Keep copies in protected locations.
- Limit access to evidence containing sensitive data.

## Privacy and GDPR Considerations

If the incident may involve personal or clinical data:

- Treat it as a potential privacy incident until proven otherwise.
- Assess whether identity, contact, clinical, employment, or audit data was affected.
- Record the potential scope of exposed data categories.
- Preserve a clear incident timeline for future compliance review.
- Escalate quickly if a breach notification assessment becomes necessary.

This project documentation does not replace formal legal advice, but the process must support the ability to review and report incidents responsibly.

## VMware Simulation Considerations

For the VMware-based lab environment:

- Identify whether the incident affects `vm-hms-primary`, `vm-hms-secondary`, `vm-admin-client`, or the host workstation.
- Use VM isolation or shutdown carefully to prevent evidence loss.
- VMware snapshots may help lab recovery, but they must not replace PostgreSQL-consistent backup and restore procedures.
- If a standby VM is promoted, document the exact moment and the recovery rationale.

## Decision Matrix

| Condition                         | Immediate Action                                       |
|:--------------------------------- |:------------------------------------------------------ |
| Suspected secret exposure         | Contain access and rotate or invalidate the secret     |
| Database corruption suspected     | Stop writes and validate latest good backup            |
| API unavailable, database healthy | Isolate API issue and restore service after log review |
| Primary VM unavailable            | Evaluate standby promotion path                        |
| Possible personal data exposure   | Escalate as privacy incident and preserve evidence     |

## Recovery Validation Checklist

Before closing the incident:

- Confirm the affected service is reachable.
- Confirm authentication works as expected.
- Confirm critical database tables are accessible.
- Confirm backup integrity if backup or recovery was involved.
- Confirm no temporary elevated access remains in place.
- Confirm updated secrets or certificates are active where needed.
- Confirm the incident record is complete.

## Communication Guidelines

- Use factual, time-based updates.
- Avoid speculation in early incident reports.
- Separate confirmed facts from pending analysis.
- Do not include real secret values or unnecessary sensitive payloads in status updates.

## Known Gaps

- The repository does not yet include centralized monitoring or alerting.
- Secrets rotation and certificate replacement are still manually managed.
- Formal legal notification criteria are not defined in detail here.
- Automated incident ticketing or evidence collection is not yet implemented.

## Related Documents

- `docs/03_Security_and_Infrastructure/Data_Protection_and_GDPR_Compliance.md`
 - `docs/03_Security_and_Infrastructure/Data_Protection_and_GDPR_Compliance.md` (Secrets & credentials guidance)
- `docs/03_Security_and_Infrastructure/Network_Architecture.md`
- `docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md`
