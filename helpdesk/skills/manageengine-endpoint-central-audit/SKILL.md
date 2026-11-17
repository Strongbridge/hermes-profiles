---
name: manageengine-endpoint-central-audit
description: "Audit Endpoint Central and Microsoft 365/Intune checks."
version: 2.2.0
author: helpdesk
metadata:
  hermes:
    tags: [audit, endpoint-central, manageengine, microsoft365, intune, security-score, patch-management, email]
---

# Unified Endpoint Central & Microsoft 365 / Intune Audit Skill

This skill executes daily, scheduled, or ad-hoc security compliance audits covering **ManageEngine Endpoint Central** and **Microsoft 365 / Microsoft Intune**. It pulls live telemetry across all audit items, evaluates compliance against predefined criteria, formats the output ready for direct verification or SharePoint form submission, archives completed reports into the user's Obsidian vault, and dispatches an HTML report to the IT team via Microsoft Graph API.

---

## Standing User Preferences & Delivery Invariants

1. **Obsidian Archival Invariant**:
   - Every completed audit run **MUST** save its full Markdown report directly into the Obsidian vault under:
     `{OBSIDIAN_VAULT_PATH}/Security Audits/Security_Audit_Report_YYYYMMDD.md`
   - Read `OBSIDIAN_VAULT_PATH` from `.env` (defaults to `C:/Users/DanRighter/OneDrive - Strongbridge/Documents/Obsidian`).
   - Deliver the saved file path using the desktop `MEDIA:/absolute/path` URI prefix alongside the summary table.

2. **Automated Scheduled Execution & Email Dispatch**:
   - The primary schedule runs daily at **8:00 AM EST** (`cronjob_manage`).
   - The job must execute all 13 checks autonomously, archive to Obsidian, dispatch the styled HTML email, and present the formatted table in chat.
   - **Email Dispatch Details**:
     - **Sender**: `helpdesk@sb-llc.com` via Microsoft Graph `POST /v1.0/users/helpdesk@sb-llc.com/sendMail`
     - **Recipients**: `cgrimaldi@sb-llc.com`, `drighter@sb-llc.com`, `memmanuel@sb-llc.com`, `cjackson@sb-llc.com`
     - **Requires Permission**: `Mail.Send` (Application permission with tenant admin consent) on the App Registration.
     - **Script**: `scripts/send_audit_email.py` (or Python script executed with native Windows path `C:/Users/...`).

3. **Execution Script Path Invariant on Windows**:
   - When invoking external python scripts on Windows via terminal, pass the native Windows forward-slash path (`python3 "C:/Users/.../script.py"`), not POSIX `/c/Users/...` which Python for Windows cannot resolve.

---

## Complete Audit Checklist Items

### ManageEngine Endpoint Central Checks
1. **Review security alerts & severity ratings**
2. **Confirm patch deployment summary**
3. **New vulnerabilities identified overnight?**
4. **Manual patch status validated (5 random samples)**

### Microsoft 365 & Intune Checks
5. **MS365 - Microsoft Secure Score reviewed**
6. **MS365 - Threat protection summary reviewed (email, endpoints)**
7. **MS365 - Active alerts triaged**
8. **MS365 - Audit logs reviewed for unusual user activity**
9. **Intune - Sign-in to Intune Admin Center / Service Health**
10. **Intune - Confirm 100% enrolled device compliance or exceptions**
11. **Intune - Check failed policy syncs**
12. **Intune - Review conditional access enforcement logs**

### Interactive Field
13. **Enter a number** (interactive form field)

---

## Authentication & API Reference

### 1. ManageEngine Endpoint Central (Cloud / Zoho OAuth)
* **Configuration:** Managed via `helpdesk/.env` (`CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`, `ACCOUNTS_URL`, `DC_BASE_URL`).
* **Zoho Self-Client Scope Rule:** Scopes must use the full cloud namespace: `DesktopCentralCloud.<Module>.<Operation>`. Short forms like `PatchMgmt` are rejected. Required: `DesktopCentralCloud.PatchMgmt.READ,DesktopCentralCloud.VulnerabilityMgmt.READ,DesktopCentralCloud.Common.READ`.
* **Token Refresh:** `POST {ACCOUNTS_URL}/oauth/v2/token` with `grant_type=refresh_token`.
* **API Header:** `Authorization: Zoho-oauthtoken {access_token}`.
* **Endpoints:**
  * Patch summary: `GET /api/1.4/patch/summary`
  * Vulnerabilities: `GET /dcapi/threats/vulnerabilities?pageLimit=100`
  * System patch reports: `GET /dcapi/threats/systemreport/patches?pageLimit=50`
  * Device details: `GET /dcapi/threats/detailedinfo/vulnerabilities?pageLimit=100`

### 2. Microsoft 365 & Intune (Microsoft Graph API)
* **Configuration:** In `helpdesk/.env` (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`).
* **Credential Invariant:** `AZURE_CLIENT_ID` must be the Application GUID (e.g. `17472e17-...`), and `AZURE_CLIENT_SECRET` must be the secret **Value** string (never the Secret ID GUID, which triggers error `AADSTS7000215`). Never swap Client ID and Client Secret.
* **App Registration & Tenant Match:** When creating a new App Registration (e.g. `Hermes-SecurityAudit`), secrets belong strictly to that specific registration; using a secret from an older/different app registration results in `AADSTS7000215`. The `AZURE_TENANT_ID` must match the Directory ID where that specific registration resides (`AADSTS700016`).
* **URL Encoding in Graph Queries:** Graph filter strings with spaces and operators (e.g. `$filter=status eq 'new' or status eq 'inProgress'` or `conditionalAccessStatus eq 'failure'`) **MUST** be URL-encoded with `urllib.parse.quote` before sending in the HTTP request to prevent control-character / bad-URL exceptions.
* **Token endpoint:** `POST https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token` with `scope=https://graph.microsoft.com/.default` and `grant_type=client_credentials`.
* **API Header:** `Authorization: Bearer {graph_token}`.
* **Required Application Permissions (with Admin Consent):**
  * `SecurityEvents.Read.All` (Secure Score, MS Defender alerts)
  * `DeviceManagementManagedDevices.Read.All` (Intune device compliance, sync status)
  * `DeviceManagementConfiguration.Read.All` (Intune policy sync status)
  * `DeviceManagementServiceConfig.Read.All` (Intune service configuration)
  * `AuditLog.Read.All` (Directory audit logs, unusual activity, CA logs)
  * `Policy.Read.All` (Conditional Access policies)
  * `Mail.Send` (Email delivery from service account `helpdesk@sb-llc.com`)

---

## Detailed Check Instructions

### Item 1: Review security alerts & severity ratings (ManageEngine)
* Query `/dcapi/threats/vulnerabilities`.
* Aggregate total vulnerabilities by severity: Critical, Important, Moderate, Low.
* List top active Critical CVEs with CVSS v3 score and affected components.

### Item 2: Confirm patch deployment summary (ManageEngine)
* Query `/api/1.4/patch/summary`.
* Extract installed patches, applicable patches, compliance % (`installed / applicable * 100`), and missing patches breakdown.
* Verify patch scan coverage (total scanned vs managed systems, scan failure count).

### Item 3: New vulnerabilities identified overnight? (ManageEngine)
* Filter vulnerabilities where `updatedtime` or `publishedtime` is within the last 24 hours.

### Item 4: Manual patch status validated (5 random samples) (ManageEngine)
* Query `/dcapi/threats/systemreport/patches`.
* Pick 5 random systems, resolve their hostnames from `/dcapi/threats/detailedinfo/vulnerabilities`.
* Verify each sampled device has recorded installed and missing patch counts, plus sample patch names and status.

### Item 5: MS365 - Microsoft Secure Score reviewed
* Query Graph `GET /security/secureScores?$top=1`.
* Extract `currentScore`, `maxScore`, and percentage (`currentScore / maxScore * 100`).

### Item 6: MS365 - Threat protection summary reviewed (email, endpoints)
* Query Defender/M365 security incidents and alerts summary (`GET /security/alerts_v2`).

### Item 7: MS365 - Active alerts triaged
* Query Graph `GET /security/alerts_v2?$filter=status eq 'new' or status eq 'inProgress'`.
* Triage alerts by severity (High, Medium, Low).

### Item 8: MS365 - Audit logs reviewed for unusual user activity
* Query Graph `GET /auditLogs/directoryAudits?$top=25` and `/auditLogs/signIns?$filter=riskLevelDuringSignIn eq 'high' or riskLevelDuringSignIn eq 'medium'`.

### Item 9: Intune - Sign-in to Intune Admin Center / Service Health
* Verify API reachability to `GET /deviceManagement`.

### Item 10: Intune - Confirm 100% enrolled device compliance or exceptions
* Query Graph `GET /deviceManagement/managedDevices?$select=deviceName,complianceState,userPrincipalName,operatingSystem`.
* Calculate compliance rate (`compliant / total * 100`).
* Enumerate non-compliant devices with associated user and OS.

### Item 11: Intune - Check failed policy syncs
* Query Graph `GET /deviceManagement/deviceConfigurationDeviceStateSummaries`.
* Extract `conflictDeviceCount` and `errorDeviceCount` across configuration profiles.

### Item 12: Intune - Review conditional access enforcement logs
* Query Graph `GET /auditLogs/signIns?$top=50&$filter=conditionalAccessStatus eq 'failure'`.
* Review blocked applications (e.g. Costpoint, Azure portal) to verify proper MFA and location enforcement.

### Item 13: Enter a number (Interactive)
* Record user input or default metric (e.g. overnight new vulnerabilities count = `0`).

---

## Output Format & Archival

The execution must produce a consolidated, executive-ready markdown table in chat AND write the full report to Obsidian:

```markdown
| # | Check Item | System | Status | Evidence / Findings Summary |
|:---:|---|---|:---:|---|
| 1 | Security alerts & severity | ManageEngine | PASS / WARN | Count by severity, top CVEs, CVSS scores |
| 2 | Patch deployment summary | ManageEngine | PASS / WARN | Compliance %, installed vs missing, scan coverage |
| 3 | New vulnerabilities overnight | ManageEngine | PASS / WARN | Count of new CVEs detected in last 24h |
| 4 | Manual patch status (5 samples) | ManageEngine | PASS / FAIL | 5 sampled devices with patch installed/missing counts |
| 5 | MS365 Secure Score reviewed | Microsoft 365 | PASS / WARN | Current score / Max score (%) |
| 6 | Threat protection summary | Microsoft 365 | PASS / WARN | Email & endpoint threat detection telemetry |
| 7 | Active alerts triaged | Microsoft 365 | PASS / WARN | Triaged alert counts by severity (High/Med/Low) |
| 8 | Audit logs reviewed | Microsoft 365 | PASS / WARN | High-risk sign-ins and directory audit events |
| 9 | Intune Admin / Service Health | Intune | PASS / FAIL | Intune management API reachability & health |
| 10 | Device compliance (100%) | Intune | PASS / WARN | Compliant count, non-compliant devices list/exceptions |
| 11 | Failed policy syncs | Intune | PASS / WARN | Configuration profile error/conflict device counts |
| 12 | Conditional Access enforcement | Intune / Entra | PASS / WARN | Sign-in policy enforcement failures & blocks analysis |
| 13 | Enter a number | Form Entry | RECORDED | User-entered value / Metric reference |
```
