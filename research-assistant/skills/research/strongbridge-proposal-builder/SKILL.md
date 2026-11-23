---
name: strongbridge-proposal-builder
description: Draft Strongbridge proposals and capability profiles.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Proposal, GovCon, Strongbridge, RFP, RFQ, Capabilities, CMMI, ISO, Past Performance]
    related_skills: [government-contract-intelligence, obsidian, grounded-citations]
---

# Strongbridge Proposal Builder Skill

## When to Use
Use this skill when drafting, reviewing, or structuring technical proposals, RFQ/RFP responses, TOMR evaluation defenses, or corporate capability profiles for Strongbridge LLC.

Use it to extract corporate knowledge, past performance citations, technical service line mappings, and staffing methodologies.

---

## 1. Strongbridge Corporate Identity & Credentials

*   **Legal Entity**: Strongbridge LLC
*   **Headquarters**: 21355 Ridgetop Circle, Sterling, VA 20166
*   **CAGE Code**: `33WW1` | **DUNS**: `16-7978787`
*   **Prime Federal Contracting Vehicles**:
    *   **GSA Multiple Award Schedule (MAS / IT Schedule 70)**: `#GS35F0278X` (SIN 54151S, 54151, 54151HEAL)
    *   **USDOT SWES BPA**: `#693JJ319A000016` (Department-wide Software Engineering Support Services)
    *   **FRA DevOps Support Services**: `#693JJ621F000034` (Contract CLIN 50009 / RFQ #693JJ621R000003)
*   **Quality & Information Security Certifications**:
    *   **CMMI-DEV Level 3** (Development) Appraised — Active and verified through **April 9, 2029**
    *   **CMMI-SVC Level 3** (Services) Appraised
    *   **ISO 9001:2015** (Quality Management System - QMS, Certificate #`1057UIT`)
    *   **ISO/IEC 20000-1:2018** (IT Service Management - ITSM, Certificate #`1058UIT`)
    *   **ISO/IEC 27001:2013** (Information Security Management System - ISMS, Certificate #`4136US`)
    *   **Section 508 / WCAG Compliance**: DHS Certified Trusted Testers on staff

### 1.1 Live SharePoint Knowledge Repository Access
Strongbridge maintains its proposal bank, CPARS, project data sheets, and CMMI/ISO libraries on SharePoint (`https://strongbridgecorp.sharepoint.com`). To query live proposal assets:
*   Credentials: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` in `profiles/research-assistant/.env`.
*   Endpoint: Authenticate with Entra ID OAuth2 client credentials against `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token` with scope `https://graph.microsoft.com/.default`.
*   Key Sites:
    *   *Bid Bank*: `/sites/BidBank` (Gold Set, Pink Set, SOW/PWS)
    *   *Proposal Management*: `/sites/proposal` (Teaming drive: CPARS, Project Data Sheets, Project Descriptions 2026, Resumes)
    *   *CMMI-PAL & ISO*: `/sites/CMMI-PAL`, `/sites/ISODocuments`

---

## 2. Core Technical Service Lines

When responding to solicitations, map the Statement of Work / Performance Work Statement (PWS) to Strongbridge's 7 primary lines of technical capability:

1.  **Agile & DevSecOps Engineering**:
    *   *Methodology*: Scaled Agile Framework (SAFe), Scrum, Kanban, Scrumban; over 400+ Agile Sprints successfully delivered to USDOT.
    *   *Toolchains*: Azure DevOps (TFS), GitHub Enterprise, GitLab, TeamCity, Jenkins, Puppet, Docker, Artifactory.
    *   *Stacks*: .NET Core / C#, ASP.NET, Java/J2EE, Spring MVC, PHP/Laravel, Python, React, Angular, Kendo UI.
    *   *Testing*: Test-Driven Development (TDD), automated unit testing, Selenium, Postman, SmartBear, MicroFocus Fortify, Tenable Nessus, Section 508 Compliance Sheriff.
2.  **Cloud Architecture & Infrastructure Modernization**:
    *   *Ecosystems*: AWS GovCloud, Microsoft Azure for Government (MAG).
    *   *Design*: Microservices, serverless computing (AWS Lambda), containerized applications (Docker), zero-downtime blue/green deployments.
    *   *Security & Compliance*: FIPS 140-2 validated encryption, NIST SP 800-53/171 RMF, FedRAMP High/Moderate baselines.
3.  **Business Process Re-engineering (BPR) & Human-Centered Design (HCD)**:
    *   *BPR*: Lean Six Sigma, As-Is and To-Be process mapping, workflow redesign, gap analyses, automated intake workflows.
    *   *HCD / UI/UX*: User research, clickable prototypes, wireflows, Section 508 accessible interfaces aligned with U.S. Digital Service standards.
4.  **Enterprise Portals & Content Management**:
    *   *Platforms*: Drupal enterprise CMS (supports 10 DOT operating administrations, 500K+ assets), Microsoft SharePoint Online (SPO), Dynamics 365 (CRM/ERP), PowerApps, Power BI.
5.  **Native & Cross-Platform Mobile Application Development**:
    *   *Platforms*: Native iOS (Swift/Xcode), Android Studio (Java/Kotlin), cross-platform mobile frameworks.
    *   *Deployments*: Rail Cross Indicator, SafeSpect, PATTS (Post-Accident Toxicological Testing System), TestFlight management, enterprise mobile app store deployment.
6.  **API Engineering & Systems Integration**:
    *   *Standards*: REST, SOAP (WSDL), XML/JSON interchange schemas, OpenAPI/Swagger.
    *   *External Integrations*: U.S. Treasury, max.gov SSO (UPSA federated identity), GIS engines (Bing Maps API, Google Maps API, Esri).
7.  **Federal Records Management (RM) & Tiered IT Support**:
    *   *Records Management*: 100/100 RMSA and 4/4 FEMR maturity rating; NARA compliance, record schedules, disposals, transfers.
    *   *Service Desk*: ITIL-based Tier 1, 2, and 3 helpdesk, Remedy, ServiceNow, 24-hour SLA ticket resolution.

---

## 3. Past Performance & Agency Experience Bank

| Client Agency | Major Program / Project | Core Strongbridge Work Performed |
| :--- | :--- | :--- |
| **USDOT / FRA** | FRA DevOps Support Services (`693JJ621F000034`) | Prime contractor for 20+ Web Information Systems, MCIA migration to Laravel, SafeSpect/Track Inspection POC, RSAC refresh, Quiet Zone portal, SharePoint SPO administration. |
| **USDOT / FRA** | Track Data Management System (TDMS) | Full spectrum DevOps supporting FRA Automated Track Inspection Program (ATIP) with centralized track safety databases. |
| **USDOT / FRA** | Business Intelligence Services (BIS) (`69319521F100015`) | FRA data warehousing, analytics, and business intelligence dashboards. |
| **USDOT / PHMSA**| PHMSA DataMart (PDM) Modernization | 15-year prime track record; integrates 80+ sources for 10,000+ national users; 99.99% uptime since 2015; Oracle OAS, Tableau, and AWS GovCloud migration. |
| **USDOT / FMCSA**| Low-Code SWAT Modernization | Microsoft PowerApps on AWS modernizing RICE mission applications (SCORE, Recruitment Tracker, FinDash). |
| **USDOT / FTA**  | Financial Management System (FMS) (`69319523F10025N`) | Mission-critical financial feeder connecting ECHO, TrAMS, Delphi, and Treasury SPS; 100% audit defense across perpetual OIG/PHMSA reviews. |
| **USDOT / BTS**  | BTS Data Infrastructure Modernization | Proprietary Data Lifecycle Matrix (DLM), Tableau visualizations, and digital publishing of *Pocket Guide to Transportation*. |
| **USDOT / FHWA** | Electronic Document Management System (`693JJ322F00168N`) | Dynamics 365, Azure DevOps traceability, live monthly training, and signed CPARS. |
| **USDOT / NHTSA**| Crash Data Acquisition Network (CDAN) (`693JJ923F000299`) | Full lifecycle DevSecOps across 5 core applications including CISS; Max.gov SSO integration, GIS API optimization ($200K+ licensing savings). |
| **USDOT / OST**  | Enterprise Drupal CMS | Managed enterprise web operations and Agile releases across 9 of 10 DOT Operating Administrations. |
| **Dept. of Labor**| Wage and Hour Division (WHD) | Custom software design, 2.8M unique visitor website, hybrid CMMI L3/Agile software maintenance, 100% Section 508 compliance. |
| **Dept. of State**| GDMS & FPDS Systems | Cloud migration to AWS GovCloud, microservices modernization (Docker + Lambda), automated vulnerability scanning (HPE Fortify 5-star rating). |
| **HHS / CMS**    | Enterprise SharePoint & Cloud POC | Azure cloud migration POC, SPO architecture, supporting 30 CMS business units and 5,000+ users. |

---

## 4. Proposal Engineering & Price/LOE Defenses (TOMR Lessons)

When responding to Task Order Requests or Defending Proposals (e.g., addressing Contracting Officer Technical Assessments like TOMR 50009):

1.  **Avoid Uniform Mathematical Allocations**: Never split Task Management or Project Management hours identically across tasks (e.g., dividing 1 FTE evenly by N tasks). Contracting officers flag this as non-technical. Instead, weight PM hours based on task complexity, stakeholder integration, regulatory risk, and team size.
2.  **Defend Senior Business Analyst Ratios**: When Senior BA hours exceed Senior Developer hours, explicitly justify the allocation by detailing:
    *   Heavy Business Process Re-engineering (BPR) workflows (As-Is / To-Be mapping).
    *   Requirements decomposition into Agile Epics and Gherkin/User Stories.
    *   Creation of Section 508 compliance testing packages, wireframes, and user acceptance testing (UAT) scripts.
3.  **Explicit QA & Testing Accounting**:
    *   Never leave tasks at "0 QA hours" if the proposal asserts Test-Driven Development (TDD).
    *   If dedicated QA specialists are not assigned to every task, explicitly document in the staffing narrative that Developers perform automated unit testing and CI/CD pipeline integration, while Senior BAs execute functional verification and UAT, clearly accounting for these testing hours within their labor mix.
4.  **Scope Reallocation Safeguards**: When retaining flexibility to reallocate hours across tasks, explicitly state the governance controls: PMO change approval, sprint burn-down tracking, monthly COR briefing, and earned value monitoring.

---

## 5. Teaming & Resource Network

*   **TTC, Inc.**: Longstanding FRA incumbent for eCollaboration, SharePoint, Records Management, and BPR (CPARS 100% Exceptional rating).
*   **Accenture Federal Services (AFS)**: Enterprise reachback partner with deep DOT OCIO Drupal, Microsoft Dynamics 365, and federal cloud expertise.
