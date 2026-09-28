---
name: ubiquiti-wireguard
description: Create WireGuard remote-user-vpn clients on a UniFi controller from Slack.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Ubiquiti, UniFi, WireGuard, VPN, Slack, network]
    related_skills: []
---

# Ubiquiti WireGuard Client Creation Skill

Creates a WireGuard remote-user-vpn client for a UniFi Network Application controller
and produces a `.conf` file matching the format downloaded from the UniFi cloud console.

## When to Use

Use when a Slack message addressed to the Hermes agent requests creation of a WireGuard
VPN client on a UniFi controller. Typical trigger:

- `@hermes Agent create wireguard client for "Tess laptop"`
- `@hermes Agent add wireguard user "Dan's laptop"`
- `@hermes Agent make a wireguard config for "remote dev"`

The agent must be addressed (`@hermes`, `@hermes Agent`); ambient requests are not treated
as client-creation requests.

## API Surface — Read This First

The **official UniFi Network API (developer.ui.com, v10.4.57 and current)** exposes VPN as
**read-only**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/sites/{siteId}/vpn/servers` | GET | List VPN servers (WireGuard, OpenVPN, L2TP, PPTP) |
| `/v1/sites/{siteId}/vpn/site-to-site-tunnels` | GET | List site-to-site tunnels |
| `/v1/sites/{siteId}/clients` | GET | List connected clients (including VPN type) |

**There is no officially documented endpoint to create WireGuard clients or register users.**
The creation path uses the **undocumented internal API** that the UniFi web UI calls:

```
POST /proxy/network/v2/api/site/{siteId}/wireguard/{vpnId}/users/batch
```

Payload (array of client objects):
```json
[
  {
    "name": "Tess laptop",
    "interface_ip": "192.168.3.2",
    "public_key": "wYj4tC7xs2ovtpq5zZFxiJ04mJ5ePmZFsk5ptHviXig=",
    "allowed_ips": [],
    "private_key": "4F4DP2j7g2K9GaTsZhdTbN07+Kfl53E9gFCFe50AAW0=",
    "preshared_key": ""
  }
]
```

This endpoint is confirmed working by Ubiquiti community reports (see References), but it is
**not officially supported** and may change across controller versions. The skill handles this
transparently: it generates the `.conf` file locally (always works) and optionally registers
the client on the controller.

## Prerequisites

1. **config.json** — copy `config.json.example` to `config.json` in the same skill directory
   and fill in your controller details (see Configuration below).

2. **Python dependencies** — the skill uses the `requests` library. Install once:
   ```
   python3 -m pip install requests
   ```
   (or `python -m pip install requests` on Windows if `python` maps to a working Python 3.)

3. **WireGuard key generation** — prefer the `wg` CLI (`wg genkey` / `wg pubkey`) when
   available on the system. The script falls back to a Python-based generator if `wg` is
   not on PATH. The `wg` CLI is strongly recommended for production use.

## Configuration (config.json)

Copy `config.json.example` to `config.json` and fill in:

| Key | Required | Description |
|-----|----------|-------------|
| `controller_url` | Yes | Base URL of the UniFi Network Application (e.g. `https://abc123.ui.com` or `https://192.168.1.1:8443`) |
| `api_key` | Yes | UniFi API key (X-API-KEY). Generate at `unifi.ui.com` → Settings → API Keys, or from the controller UI. |
| `site_id` | Yes | Site ID for the VPN. Usually `default` for a single-site controller, or the site UUID. |
| `vpn_id` | Yes | The WireGuard server's ID as shown in the controller UI (e.g. `WireGuard1`). |
| `vpn_subnet_cidr` | Yes | The VPN pool CIDR (e.g. `192.168.3.0/24`). Used to auto-allocate the next free IP. |
| `vpn_server_public_key` | Yes | The WireGuard server's public key (from the controller VPN settings). Used in the client's `[Peer]` section. |
| `vpn_server_endpoint` | Yes | The server's endpoint `IP:51820` (e.g. `23.31.111.185:51820`). Used in the client's `[Peer]` section. |
| `vpn_dns` | No | List of DNS servers for the client (e.g. `["192.168.3.1", "fd01:ec44:d2bd:b589::1"]`). Default: `["192.168.3.1"]`. |
| `output_dir` | Yes | Where to write the `.conf` file (e.g. `C:\\Users\\DanRighter\\OneDrive - Strongbridge\\Downloads`). |

## Trigger Behavior

When triggered, the agent (or the script directly) does the following:

### Phase 1 — Local (always works, no controller interaction)

1. **Reads the request** — extract the client display name from the Slack message
   (e.g. `"Tess laptop"` from `@hermes Agent create wireguard client for "Tess laptop"`).

2. **Loads config.json** — resolves controller_url, api_key, site_id, vpn_id, subnet,
   server public key, server endpoint, DNS, and output directory.

3. **Generates a WireGuard keypair** — private key + public key for the new client.
   Uses `wg genkey` + `wg pubkey` if `wg` is on PATH; otherwise falls back to a
   Python-based generator.

4. **Allocates an interface IP** — picks the next free /32 IPv4 from `vpn_subnet_cidr`
   after the gateway (.1), skipping IPs already in use by existing VPN clients
   (discovered via the documented `GET /v1/sites/{siteId}/clients` endpoint).

5. **Builds the .conf file** — matches the downloaded format exactly:
   ```ini
   [Interface]
   PrivateKey = <client_private_key>
   Address = <allocated_ip>/32
   DNS = <dns1>,<dns2>

   [Peer]
   PublicKey = <vpn_server_public_key>
   AllowedIPs = 0.0.0.0/0,::/0
   Endpoint = <vpn_server_endpoint>
   ```

6. **Writes the .conf** — to `output_dir` with a timestamped filename:
   ```
   WireGuard-{vpn_id}-{client_name_slug}-{YYYYMMDD-HHMMSS}.conf
   ```
   Example: `WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf`

### Phase 2 — Controller registration (optional, undocumented API)

7. **POSTs to the batch endpoint** — registers the client on the controller so it
   appears in the VPN client list and gets an IP from the pool:
   ```
   POST /proxy/network/v2/api/site/{siteId}/wireguard/{vpnId}/users/batch
   ```
   Auth header: `X-API-KEY: <api_key>`.

   This step can be skipped with `--no-register` (or `--dry-run`) to only generate the
   `.conf` file and leave registration to the user via the UniFi console UI.

8. **Confirms in Slack** — the agent replies with the filename, the allocated IP,
   and a summary line. Example:
   ```
   Created WireGuard client "Tess laptop" on UniFi controller.
   Config file: WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
   IP: 192.168.3.2/32
   Download: C:\Users\DanRighter\OneDrive - Strongbridge\Downloads\WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
   ```

## Script Usage (standalone)

The skill includes `create_client.py` which can be run directly from the terminal
or invoked by the agent.

```
python create_client.py "Tess laptop" [--config config.json] [--dry-run] [--no-register] [--interface-ip 192.168.3.2]
```

| Flag | Purpose |
|------|---------|
| `--config` | Path to config.json (default: `config.json` in the script's directory). |
| `--dry-run` | Generate keypair + .conf, print the would-be API payload, but skip the controller call. |
| `--no-register` | Generate keypair + .conf and skip only the batch registration (conf file still written). Use this when you want the .conf but want to register manually in the console. |
| `--interface-ip` | Force a specific IP instead of auto-allocation. |
| `--list-servers` | List VPN servers on the site using the **documented** GET endpoint and exit. |
| `--list-clients` | List connected clients on the site using the **documented** GET endpoint and exit. |

The script prints a `SUMMARY|...` line the agent can relay to Slack.

## Verification of the .conf Format

The generated `.conf` matches the format of files downloaded from the UniFi cloud console.
Verified against a real downloaded config (`WireGuard-Server-1-Tess-Int.conf`):

```
[Interface]
PrivateKey = KMRngllJbYrvvZqZCupMJH3Q9qQeq/YIJnKoOBWI0Vk=
Address = 192.168.3.5/32,fd01:ec44:d2bd:b589::5/128
DNS = 192.168.3.1,fd01:ec44:d2bd:b589::1

[Peer]
PublicKey = oC1SzPBjRURW213U+kpsbsCMIJHARt7iG9cqA55c1zw=
AllowedIPs = 0.0.0.0/0,::/0
Endpoint = 23.31.111.185:51820
```

Differences to note:
- The downloaded config may include an IPv6 address in the `Address` field. The script
  generates IPv4-only by default. Add `vpn_ipv6_address` to config.json and update
  `build_conf()` in the script if you need IPv6.
- The downloaded config uses the server's actual endpoint IP. The script reads this from
  `vpn_server_endpoint` in config.json — make sure it matches what the controller shows.

## Answer / Confirmation Format in Slack

The agent replies in Slack with:

```
Created WireGuard client "Tess laptop" on UniFi controller.
Config file: WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
IP: 192.168.3.2/32
Download: C:\Users\DanRighter\OneDrive - Strongbridge\Downloads\WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
```

If `--dry-run` or the API call fails, the agent says what happened and does not claim
the client was created on the controller. The `.conf` file is still written locally.

## API Notes

- The batch endpoint (`.../users/batch`) is **not** in the official developer.ui.com API
  surface. It is reverse-engineered from the UniFi web UI and confirmed working in practice
  by Ubiquiti community reports. It may break across controller versions.
- The documented read endpoints (`GET /v1/sites/{siteId}/vpn/servers`, `GET .../clients`)
  are stable and part of the official Network API.
- The controller's API key must have rights to modify WireGuard clients on the target site.
- Cloud-hosted UniFi controllers (UI.com managed) use the same API surface as self-hosted
  controllers; the `controller_url` is the console URL.
- To call the documented API through the UniFi cloud connector (for cloud-hosted consoles),
  use the proxy base URL:
  ```
  https://api.ui.com/v1/connector/consoles/{consoleId}/proxy/network/integration
  ```
  instead of the console's direct URL. Set `controller_url` to this proxy URL in config.json
  when using cloud-hosted UniFi.

## What Not to Do

- Do not create clients without a valid config.json — ask the user to fill it in first.
- Do not guess the API key or controller URL.
- Do not reuse a private key across clients.
- Do not skip the IP collision check in production (use `--dry-run` to verify first).
- Do not silently claim a client was registered when the batch endpoint failed — report the
  failure and note that the `.conf` is still available locally.

## Example Exchange

**User (Slack):**
```
@hermes Agent create wireguard client for "Tess laptop"
```

**Agent:**
1. Extracts client name: "Tess laptop"
2. Loads config.json
3. Generates keypair (using `wg` CLI if available)
4. Discovers existing VPN clients via `GET /v1/sites/{siteId}/clients` (documented)
5. Allocates IP 192.168.3.2/32 (next free after gateway)
6. POSTs to the batch endpoint — success (or failure, handled)
7. Writes `WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf`
8. Replies:

```
Created WireGuard client "Tess laptop" on UniFi controller.
Config file: WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
IP: 192.168.3.2/32
Download: C:\Users\DanRighter\OneDrive - Strongbridge\Downloads\WireGuard-WireGuard1-Tess-laptop-20260825-153000.conf
```

**Dry-run example:**

**User (Slack):**
```
@hermes Agent dry run wireguard client for "Test device"
```

**Agent:** Runs `create_client.py "Test device" --dry-run` and reports the would-be
filename, keypair, and IP without touching the controller.

**List servers example:**

**User (Slack):**
```
@hermes Agent list wireguard servers
```

**Agent:** Runs `create_client.py --list-servers` and reports the VPN servers on the site
using the documented GET endpoint.

## Folder Structure

```
ubiquiti-wireguard/
├── SKILL.md                  # this file
├── create_client.py          # main script (keygen + API + .conf)
├── config.json.example       # template to copy to config.json
└── config.json               # (created by user, not committed)
```

## References

- UniFi Network API documentation (official): https://developer.ui.com/network
- API reference v10.4.57 OpenAPI spec: https://developer.ui.com/network/v10.4.57/openapi.json
- Ubiquiti Community — Bulk Creation of WireGuard VPN users (reverse-engineered endpoint):
  https://community.ui.com/questions/c68afe65-a3f7-4479-b1dc-102deaae6b4a
- UniFi Gateway WireGuard VPN Client help: https://help.ui.com/hc/en-us/articles/16357883221015
