---
name: strongbridge-hardware-evaluator
description: Use when evaluating and reporting on corporate hardware recommendations.
version: 1.0.0
author: Technical Writer
license: MIT
metadata:
  hermes:
    tags: [hardware, procurement, report, automation, recommendations]
    related_skills: [elephant-goldfish-review, obsidian]
---

# Strongbridge Hardware Evaluator Skill

## When to Use
Use when: Generating a weekly technical hardware recommendation report from the corporate Hardware-Recommendations research for the IT operations channel.

## Guidelines
1. **Source Ingestion**: Automate reading of all `Hardware-Recommendations/` files, including `User-Profiles-and-Specifications.md`, `Dell-Enterprise-Catalog.md`, `Microsoft-Surface-Business-Case.md`, `Comparative-Analysis-Matrix.md`, and `Weekly-Market-Watch.md`.
2. **Synthesis & Detailed Profile Analysis**: Consolidate the three user profiles (Developers/DevOps, Management/Executives/PMs/Writers, Power Users/Architects/BI Analysts) into a comprehensive technical report. Never use placeholder text or stub sections; fully expand each profile with compute requirements, toolchain compatibility (x86_64 vs. ARM64), display/docking demands, and real-world workflows.
3. **Fleet Recommendation Matrix with Expanded Pricing Justification**: Present the "Best Value & Best System" winners for each profile, including exact model names, vendor, estimated unit costs, and robust technical justifications. Every pricing point must be explicitly justified against performance metrics and alternative configurations.
4. **Mandatory Total Cost of Ownership (TCO) & Business Case Breakdown**:
   - **Deployment & Provisioning Labor**: Quantify labor hours and cost savings (e.g., zero-touch Windows Autopilot reducing IT setup time from 2.5 hours to 15 minutes per device).
   - **Management Licensing**: Contrast native cloud management (Microsoft Intune & Surface Management Portal) with third-party agent licensing (e.g., ~$45/user/year savings).
   - **CUI & Regulatory Compliance**: Detail NIST SP 800-171 data custody requirements, contrasting removable SSD hardware architecture with paid vendor drive retention contracts (e.g., Dell Keep Your Hard Drive).
   - **Residual Asset Value**: Include 3-year lifecycle asset depreciation and recovery estimates (e.g., ~35% residual value for premium Surface tiers vs. ~20% for standard enterprise laptops).
5. **Vendor Business Case & Trade-Off Analysis**: Provide direct head-to-head comparisons across thermal management, battery longevity under client travel conditions (16.5–22.5 hrs vs. 10–14 hrs), digital inking/executive presentation workflows, and Docker/IDE compilation benchmarks.
6. **Publication**: Format as a clean, structured federal-standard markdown report and post it directly to the designated IT operations Slack channel (`#SB-netops` / `C0C91831Y5B`) using Hermes desktop UI tools (`drive_preview`/`shows`).
7. **Review & Compliance**: Run the content through the Elephant Goldfish review protocol to verify all hardware claims, model numbers, and prices against source files in the vault.
8. **Tracking**: Log the weekly activity, audit date, and changes in `Weekly-Market-Watch.md`.
*References: https://github.com/google/elephant-goldfish-model*
