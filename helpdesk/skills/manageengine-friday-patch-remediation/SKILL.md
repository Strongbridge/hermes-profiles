---
name: manageengine-friday-patch-remediation
description: "Schedule Friday patch remediation for Endpoint Central."
version: 1.1.0
author: helpdesk
license: MIT
metadata:
  hermes:
    tags: [patch-management, remediation, manageengine, endpoint-central, automation]
---

# ManageEngine Friday Patch Remediation Skill

## When to Use
Use this skill when scheduling weekly patch remediation tasks in Endpoint Central for missing vulnerabilities identified during daily audits, targeting the Friday maintenance window for deployment after 8:00 AM.

---

## Deployment Windows & Policy Templates

Endpoint Central has pre-configured Friday deployment policies available:
* **`79468000003821028`**: *Deploy any time at the earliest_Friday Window*
* **`79468000003723109`**: *New Patch Friday*
* **`79468000001726041`**: *Patch Friday*
* **Default policy fallback:** `79468000000203205` (*Deploy any time at the earliest*)

---

## Authentication & API Reference

* Uses the existing Zoho OAuth configuration from `helpdesk/.env` (`CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`, `ACCOUNTS_URL`, `DC_BASE_URL`).
* Header: `Authorization: Zoho-oauthtoken {access_token}`

### Endpoints
1. **Query Missing Patches & System Reports:**
   * `GET /dcapi/threats/systemreport/patches?pageLimit=100`
   * `GET /api/1.4/patch/summary`
2. **Retrieve Policies:**
   * `GET /api/1.4/patch/deploymentpolicies`
3. **Trigger / Schedule Patch Installation:**
   * `POST /api/1.4/patch/installpatch`
   * **Timing Parameter:** Set `installaftertime` to the current Friday's date with time `08:00` (format: `yyyy-MM-dd HH:mm`, e.g. `2026-11-20 08:00`).
   * **Payload Structure:**
     ```json
     {
       "ConfigName": "Weekly Friday Patch Remediation - YYYY-MM-DD",
       "ConfigDescription": "Automated remediation for Critical and Important missing patches identified in daily audits scheduled after 08:00 AM",
       "DeploymentPolicyTemplateID": 79468000003821028,
       "deploymentType": 0,
       "actionToPerform": "Deploy",
       "forceRebootOption": 1,
       "isOnlyApproved": "true",
       "installaftertime": "YYYY-MM-DD 08:00",
       "PatchIDs": [45988, 46071],
       "ResourceIDs": [79468000002356087]
     }
     ```

---

## Remediation Workflow

1. **Step 1: Identify Targets**
   * Fetch all systems with missing patches from `/dcapi/threats/systemreport/patches`.
   * Filter for missing patches rated **Critical** and **Important**.
   * Collect unique `patch_id`s and target `resource_id`s.

2. **Step 2: Set Deployment Window After 8:00 AM**
   * Calculate current Friday's date in `YYYY-MM-DD` format.
   * Explicitly set `installaftertime: "<YYYY-MM-DD> 08:00"`.
   * Attach policy template `79468000003821028` (*Deploy any time at the earliest_Friday Window*).

3. **Step 3: Create & Deploy Remediation Task**
   * POST to `/api/1.4/patch/installpatch`.
   * Validate response status `success`.

4. **Step 4: Audit & Log**
   * Append remediation action to the Obsidian vault at:
     `Obsidian/SB-Hermes/Security Audits/Friday_Remediation_Log_YYYYMMDD.md`
   * Include task name, target count, patch count, scheduled start time (`08:00 AM`), and affected CVEs.
