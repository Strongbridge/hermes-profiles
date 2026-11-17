---
name: government-contract-intelligence
description: Use when researching federal SAM.gov and 50-state IT contracts.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GovCon, SAM.gov, STARS III, SWES, Procurement, Acquisition, API]
    related_skills: [obsidian, grounded-citations]
---

# Government Contract Intelligence

## When to Use
Use this skill when researching, tracking, and optimizing federal contracting opportunities (such as GSA STARS III, agency BPAs like USDOT SWES), querying the SAM.gov API, analyzing 50-state SLED contract pipelines, and maintaining an organized opportunity pipeline within Obsidian.

## 1. Core Concepts & Acquisition Vehicles

### 1.1 GSA 8(a) STARS III GWAC
*   **Best-in-Class (BIC)**: Multiple-award IDIQ contract vehicle designated by OMB for streamlined 8(a) small business IT service acquisitions.
*   **Directed Awards**: Federal contracting officers can issue sole-source task orders up to **$4.5 Million** (civilian) or $7.0M (defense) directly to an 8(a) STARS III holder, bypassing standard competition under FAR 19.8.
*   **Scope**: Centered on NAICS 541512 (Computer Systems Design Services) but includes all IT-related codes. Features sub-areas for Emerging Technologies (AI, ML, RPA) and OCONUS performance.

### 1.2 Blanket Purchase Agreements (BPAs) & Agency Vehicles
*   **BPA Structure**: Established under GSA Multiple Award Schedules (MAS) to meet recurring agency needs (e.g., USDOT Software Engineering Support Services - SWES).
*   **Recompetes**: Keep a tight tracking cadence on predecessor BPA ordering period end-dates and option extensions, as these trigger major recompete solicitations (e.g., SWES 2.0).

### 1.3 State, Local & Cooperative Vehicles (SLED & NASPO ValuePoint)
*   **NASPO ValuePoint Cooperatives**: Multi-state Master Agreements (e.g., Cloud & Software Solutions) led by a single state and adopted by all 50 states via Participating Addenda (PAs). Enables sales across states without 50 separate bids.
*   **State DOT Master Vehicles**: Pre-qualified state pools (e.g., MD CATS+, VA VITA ITCL, TX DIR DBITS) where transportation departments procure application development, DevOps, and O&M under expedited task orders.
*   **Supporting Reference**: See `references/50-state-procurement-guide.md` for complete 50-state taxonomy (NIGP/UNSPSC) and cooperative capture mechanisms.

---

## 2. Procedure: Building and Maintaining the Pipeline

### Step 1: Vehicle Intelligence Profiling
Before searching for specific opportunities, profile the contract vehicle:
1.  **Identify Sponsoring Agency & Scope**: Determine if it is a GWAC (government-wide) or agency-specific BPA.
2.  **Verify Ordering Periods & Ceilings**: Document base and option years and current obligation-to-ceiling ratios to assess vehicle utilization.
3.  **Map NAICS & PSC Codes**: Note the primary Product Service Codes (e.g., `DA01` for application development labor) and NAICS codes used by contracting officers.

### Step 2: SAM.gov API Query Formulation
When querying GSA's SAM.gov Contract Opportunities Public API (`/opportunities/v2/search`):
1.  **API Key Harvest**: Retrieve the `sam_gov_api` key dynamically from local environment variables or `.env` credential files. Do not hardcode the API key.
2.  **Mandatory Parameters**: Always supply `postedFrom` and `postedTo` formatted as `MM/dd/yyyy`.
3.  **Set-Aside Filters**: Use the standard SAM.gov Set-Aside codes:
    *   `8A` - 8(a) Set-Aside (FAR 19.8)
    *   `SBA` - Total Small Business Set-Aside (FAR 19.5)
    *   `8AN` - 8(a) Sole Source
4.  **Keyword & Organization Refinement**: Refine queries by `ncode` (NAICS), `organizationName` (Agency/Subtier), and `title`.

### Step 3: Pipeline Structuring in Obsidian
Create a dedicated `Procurement/` folder with the following standardized files:
*   `README.md`: Central scope mapping, executive summary of tracked vehicles, and pipeline governance rules.
*   `<Vehicle-Name>.md`: Detailed contract profile, ordering instructions, and teaming strategies.
*   `Opportunity-Pipeline.md`: The active opportunity register. Use a clear, tabular schema:
    ```markdown
    | Notice ID / Sol # | Opportunity Title | Sponsoring Agency | Type | Date Posted | Due Date | Set-Aside | NAICS | Details & Links |
    ```

### Step 4: Automate with Graceful Fallbacks
Implement an automated Python sync script (`update_sam_opportunities.py`) to periodically query SAM.gov. To handle inevitable rate limits (API 429 errors) and quota caps:
1.  **Quota Verification**: Catch `429` status codes explicitly.
2.  **Graceful Fallback to Offline Grooming**: If throttled, skip API requests and trigger offline grooming logic.
3.  **Self-Cleaning**: Scan the existing `Opportunity-Pipeline.md` markdown table, evaluate deadlines against the current system date, and move expired or archived items to an inactive log.
4.  **Logging**: Append a structured log entry to the "Maintenance and Ingestion Log" section of the document to document compliance-ready audit trails.

### Step 5: 50-State SLED Research & Opportunity Pipeline
When tracking state-level IT contracting:
1.  **Establish SLED Directory**: Create `Procurement/SLED-State-Local/` containing `README.md`, `NASPO-ValuePoint-IT-Services.md`, `50-State-Procurement-Portal-Directory.md`, and `SLED-Opportunity-Pipeline.md`.
2.  **Taxonomy Translation**: Translate federal NAICS codes to state commodity codes (NIGP Class 920/918 or UNSPSC 8111) before querying state portals.
3.  **Cooperative Teaming**: Track newly executed State Participating Addenda under NASPO ValuePoint to identify prime reseller partners (Carahsoft, SHI, WWT) requiring professional services subcontractors.
4.  **Multi-Feed Script**: Implement `scripts/update_state_opportunities.py` to ping state open-data endpoints and RSS feeds, perform deadline verification, and maintain audit trails.

---

## 3. Standing Rules & Pitfalls

*   **Date Range Constraint Pitfall**: Always limit the range between `postedFrom` and `postedTo` to a maximum of 1 year. Querying a wider window throws a `400 Bad Request` error.
*   **FIPS / BMI Compatibility Constraint**: Note that Carbonite Bare Metal Image (BMI) backups cannot function on Windows systems where the Federal Information Processing Standard (FIPS) setting is enabled. Ensure other backup and storage types are utilized on FIPS-enabled environments processing CUI.
*   **Set-Aside Exclusivity Rule**: When querying SAM.gov, remember that the API accepts only a single Set-Aside value in the `typeOfSetAside` field at any one time.
*   **Rate-Limit Protection Rule**: Always write automation scripts to handle 429 status codes without crashing, gracefully executing local markdown cleanups to ensure the pipeline document remains optimized and updated regardless of API availability.
*   **State Commodity Code Translation Pitfall**: Do not search state portals using federal NAICS or PSC codes alone — most state e-procurement engines require NIGP (Class 920/918) or UNSPSC codes, or they will return zero results.
*   **Cooperative Flow-Down Rule**: In SLED procurements, confirm that prime terms in the NASPO Master Agreement flow down to subcontractors, ensuring payment and intellectual property protections without requiring separate state-level licensing.
