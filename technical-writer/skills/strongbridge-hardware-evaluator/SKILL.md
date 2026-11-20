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
6. **Publication & Cron Routing**:
   - Format as a clean, structured federal-standard markdown report.
   - For scheduled or background cron runs, **always explicitly set the `deliver` parameter to the target Slack channel (`slack:C0C91831Y5B`)** instead of using `origin` or leaving it blank, which causes the output to deliver back to the local desktop app session rather than Slack.
7. **Review & Compliance**: Run the content through the Elephant Goldfish review protocol to verify all hardware claims, model numbers, and prices against source files in the vault.
8. **Tracking**: Log the weekly activity, audit date, and changes in `Weekly-Market-Watch.md`.

## Pitfalls
- **Default Cron Deliver Target**: Background and cron executions default to `deliver: origin`. If triggered manually from a local chat session, the output will only display in the local chat panel. Always configure an explicit `slack:<channel_id>` deliver target for correct remote routing.
- **Python Environment Mismatch**: Ensure `python-docx` and related dependencies are bound directly to the active virtual environment (`venv`) using `uv pip install --python <venv_path>` rather than the global site packages, as system-level libraries are isolated from Hermes's internal environments.
- **Data Ingestion Gaps**: Always cross-reference multiple source sheets; incomplete or mismatched model specifications can lead to invalid recommendation matrices.

*References: https://github.com/google/elephant-goldfish-model*
