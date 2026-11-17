---
name: strongbridge-hardware-evaluator
description: Research and recommend enterprise laptops for Strongbridge.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Hardware, Laptops, Dell, Surface, Procurement, IT, Strongbridge]
    related_skills: [obsidian, microsoft-office]
---

# Strongbridge Hardware Evaluator Skill

## When to Use
Use this skill when evaluating, comparing, or recommending corporate laptops and workstation hardware for Strongbridge employees across Developers, Management, and Power User roles.

## Standing Selection Rule
*   **Best Value & Performance Principle**: Do not force a single vendor (neither Dell nor Microsoft Surface is mandatory). Select the best system for each role profile based on technical performance, user ergonomics, and cost-effectiveness.
*   **Developer Priority**: Choose native x86_64 architecture (Dell Precision/Latitude) to ensure 100% Docker/VM toolchain compatibility and lower acquisition costs ($1,649–$2,349) unless a specific developer requests Surface Laptop Studio 2.
*   **Management Priority**: Select Microsoft Surface Pro 11th Edition ($949–$1,399) where 2-in-1 mobility, digital document signatures/markup, and long battery life provide clear productivity gains; select Dell Latitude 7450 ($1,499) for standard non-touch clamshell preference.

---

## 1. User Role Profiles & Standard Requirements

When evaluating hardware for Strongbridge employees, map requirements against these three standardized user profiles:

### Profile A: Software Developers & DevOps Engineers
*   **Workload**: Docker containers, local VMs, IDEs (VS Code, Visual Studio, IntelliJ), local database instances (SQL Server, PostgreSQL), continuous builds, multi-monitor 4K docking.
*   **Target Specifications**:
    *   *RAM*: 32GB to 64GB DDR5 / LPDDR5x
    *   *Storage*: 1TB to 2TB PCIe Gen4 NVMe SSD (Removable SSD preferred for CUI compliance)
    *   *CPU*: High-performance multi-core x86_64 (Intel Core Ultra 7/9 H-series, AMD Ryzen 7/9 Pro) or high-efficiency ARM64 (Qualcomm Snapdragon X Elite with verified toolchain compatibility)
    *   *Ports*: Minimum 2x Thunderbolt 4 / USB4, HDMI 2.1, USB-A, 3.5mm audio
*   **Dell Primary**: Dell Precision 5690 / 3590, Dell Latitude 7650
*   **Surface Primary**: Microsoft Surface Laptop Studio 2 for Business (Intel Core i7 13th Gen, up to 64GB RAM, NVIDIA RTX 4050/4060 or RTX 2000 Ada)

### Profile B: Management, Executives, PMs & Technical Writers
*   **Workload**: Microsoft 365 (Word, Excel, PowerPoint), Teams video calls, Slack, browser research, PDF markup and document signing, client presentations, frequent travel.
*   **Target Specifications**:
    *   *RAM*: 16GB to 32GB LPDDR5x
    *   *Storage*: 512GB to 1TB NVMe SSD
    *   *Form Factor*: Ultra-portable (under 3.0 lbs), long battery life (14–20+ hours), high-resolution webcam (1080p / 1440p Quad-HD), touchscreen/pen support
*   **Dell Primary**: Dell Latitude 7450 / 9450 2-in-1, Dell XPS 13
*   **Surface Primary**: Microsoft Surface Pro 11th Edition Copilot+ PC (Snapdragon X Elite, 13" 2.8K OLED/IPS, 1.97 lbs + Flex Keyboard) OR Surface Laptop 7 (13.8" / 15")

### Profile C: Power Users, Systems Architects & BI Analysts
*   **Workload**: Heavy data engineering, Power BI data modeling, multi-cloud architecture design, complex financial/statistical modeling, multi-tasking across heavy applications.
*   **Target Specifications**:
    *   *RAM*: 32GB to 64GB LPDDR5x
    *   *Storage*: 1TB to 2TB NVMe SSD
    *   *Graphics*: Dedicated GPU (NVIDIA RTX Ada / RTX 40-series) or integrated NPU/GPU with multi-display 4K output capabilities
*   **Dell Primary**: Dell Precision 5690, Dell Latitude 7650, Dell XPS 16
*   **Surface Primary**: Microsoft Surface Laptop Studio 2 for Business (Intel Core i7, NVIDIA RTX 4060/2000 Ada, 14.4" PixelSense Flow touchscreen with 3-position dynamic woven hinge)

---

## 2. Business Case Framework: Dell vs. Microsoft Surface

When making a business case to transition or hybridize from Dell to Microsoft Surface, evaluate across four key operational pillars:

### 1. Management & Deployment (Zero-Touch Intune Integration)
*   **Surface Advantage**: Surface Management Portal is natively built into Microsoft Intune/Autopilot. Provides direct firmware management (DFCI), hardware health telemetry, battery wear tracking, and zero-touch out-of-box deployment without 3rd-party software agents.
*   **Dell Comparison**: Requires Dell Command | Suite, SupportAssist, or third-party endpoint management packages.

### 2. Versatility & Executive Mobility
*   **Surface Advantage**: Surface Pro 11 provides a 1.97 lb 2-in-1 form factor with detachable Flex Keyboard and haptic Surface Slim Pen 2, enabling direct PDF annotation, electronic signature capture during client meetings, and whiteboarding in Stage mode.
*   **Dell Comparison**: Standard clamshell Latitudes lack native pen/whiteboard ergonomics unless configured as heavier 2-in-1 convertibles.

### 3. Data Retention & CUI Security
*   **Both Vendors**: Feature Hardware TPM 2.0, Windows Hello Face Sign-in, and Secured-Core PC status.
*   **Crucial Compliance Note**: Both Surface for Business (Laptop Studio 2, Surface Pro 11) and Dell Latitude/Precision feature **removable SSDs**, allowing Strongbridge to retain hard drives upon hardware servicing or RMA in accordance with NIST SP 800-171 CUI rules.

### 4. Warranty & Support
*   **Dell**: ProSupport Plus with Next Business Day On-Site Service and Keep Your Hard Drive.
*   **Microsoft**: Microsoft Complete for Business with Next Business Day Advanced Exchange and Drive Retention.

---

## 3. Maintenance Procedure in Obsidian

1.  Maintain all research in the dedicated vault folder: `SB-Hermes/Hardware-Recommendations/`
2.  Update `Weekly-Market-Watch.md` weekly with active vendor list prices, promotional bundles, and model announcements.
3.  Run the automated maintenance script `scripts/update_hardware_research.py` to refresh current pricing metrics and append maintenance logs.
