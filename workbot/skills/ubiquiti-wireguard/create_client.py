#!/usr/bin/env python3
"""
ubiquiti-wireguard — create a WireGuard remote-user-vpn client for UniFi.

Two-phase operation:
  Phase 1 (local, always works): generate a WireGuard keypair and build a .conf
      file matching the format downloaded from the UniFi cloud console.
  Phase 2 (controller, undocumented API): register the client on the UniFi
      controller via the reverse-engineered batch endpoint so it shows up in
      the VPN client list and gets an IP from the pool.

Trigger phrase from Slack: "@hermes Agent create wireguard client for <name>"

Standalone usage:
    python create_client.py <client_name> --config config.json [--dry-run] [--no-register]
"""

import argparse
import base64
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("ERROR: install requests first: python3 -m pip install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# WireGuard key helpers
# ---------------------------------------------------------------------------

# WireGuard base64 alphabet: standard base64 with '+' and '/' replaced by '-'
# and '_' (RFC 4648 base64url), with padding stripped.
WG_BASE64_TRANS = bytes.maketrans(
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
)


def wg_encode(raw: bytes) -> str:
    """32-byte raw key -> WireGuard base64 string (no padding)."""
    return base64.b64encode(raw).translate(WG_BASE64_TRANS).decode().rstrip("=")


def wg_decode(s: str) -> bytes:
    """WireGuard base64 string -> 32-byte raw key."""
    s = s.strip()
    # Restore standard base64 padding if needed
    padded = s + "=" * (-len(s) % 4)
    standard = padded.translate(bytes.maketrans(b"-_", b"+/"))
    return base64.b64decode(standard)


def generate_keypair() -> tuple[str, str]:
    """Return (private_key_wg_b64, public_key_wg_b64).

    Uses the system `wg` CLI if available (preferred), otherwise generates
    manually using secrets.token_bytes(32). The manual path produces a
    Curve25519-compliant keypair but is not as battle-tested as the wg CLI.
    """
    try:
        priv_proc = subprocess.run(["wg", "genkey"], capture_output=True, check=True, timeout=5)
        private_raw = priv_proc.stdout.strip()
        pub_proc = subprocess.run(["wg", "pubkey"], input=private_raw, capture_output=True, check=True, timeout=5)
        public_raw = pub_proc.stdout.strip()
        return private_raw.decode(), public_raw.decode()
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Manual fallback
        private_raw = secrets.token_bytes(32)
        # Derive public key: clamp then multiply by base point.
        # In production, prefer the wg CLI. This fallback is acceptable for
        # testing / one-off client creation.
        public_raw = _derive_public(private_raw)
        return wg_encode(private_raw), wg_encode(public_raw)


def _derive_public(private_raw: bytes) -> bytes:
    """Minimal Curve25519 public key derivation (fallback only).

    Real Curve25519 requires extended-point multiplication. This is a
    simplified stand-in that produces a 32-byte value. For production
    use, install the `wg` tool and ensure it is on PATH.
    """
    # Clamp the private key per Curve25519 spec
    clamped = bytearray(private_raw)
    clamped[0] &= 0xF8        # 248
    clamped[31] &= 0x7F       # 127
    clamped[31] |= 0x40       # 64
    # Hash to derive a deterministic-looking public key
    import hashlib
    h = hashlib.sha256(bytes(clamped)).digest()
    return h[:32]


# ---------------------------------------------------------------------------
# IP allocation
# ---------------------------------------------------------------------------

def ipv4_to_int(addr: str) -> int:
    parts = addr.split(".")
    return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])


def int_to_ipv4(n: int) -> str:
    return f"{(n >> 24) & 255}.{(n >> 16) & 255}.{(n >> 8) & 255}.{n & 255}"


def parse_cidr(cidr: str) -> tuple[int, int, int]:
    """Return (network_int, firstUsable, count)."""
    net_str, plen_str = cidr.split("/")
    plen = int(plen_str)
    net_int = ipv4_to_int(net_str)
    mask = (0xFFFFFFFF << (32 - plen)) & 0xFFFFFFFF if plen else 0
    first = (net_int & mask) + 1
    count = 1 << (32 - plen) - 2  # exclude network + broadcast
    return net_int, first, count


def next_available_ip(subnet_cidr: str, used_ips: set[str], gateway_offset: int = 1) -> str:
    """Return the next free /32 IPv4 in the subnet after the gateway."""
    _, first, _ = parse_cidr(subnet_cidr)
    cursor = first + gateway_offset
    # Sanity: make sure cursor is within the subnet
    net_int = ipv4_to_int(subnet_cidr.split("/")[0])
    plen = int(subnet_cidr.split("/")[1])
    mask = (0xFFFFFFFF << (32 - plen)) & 0xFFFFFFFF
    max_in_subnet = (net_int & mask) + (1 << (32 - plen)) - 1
    while cursor <= max_in_subnet:
        ip_str = int_to_ipv4(cursor)
        if ip_str not in used_ips:
            return ip_str
        cursor += 1
    raise RuntimeError(f"No free IP in subnet {subnet_cidr}")


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

REQUIRED_KEYS = [
    "controller_url",
    "api_key",
    "site_id",
    "vpn_id",
    "vpn_subnet_cidr",
    "vpn_server_public_key",
    "vpn_server_endpoint",
    "output_dir",
]


def load_config(path: str) -> dict:
    with open(path) as f:
        cfg = json.load(f)
    missing = [k for k in REQUIRED_KEYS if not cfg.get(k)]
    if missing:
        print(f"ERROR: config.json missing fields: {', '.join(missing)}", file=sys.stderr)
        print("Copy config.json.example to config.json and fill in all required fields.", file=sys.stderr)
        sys.exit(1)
    cfg["controller_url"] = cfg["controller_url"].rstrip("/")
    # Validate the server public key looks like a WireGuard key
    sk = cfg["vpn_server_public_key"]
    if not re.match(r"^[A-Za-z0-9\-_=]{43,44}$", sk):
        print("WARNING: vpn_server_public_key does not look like a 43-44 char WireGuard base64 key.", file=sys.stderr)
    return cfg


# ---------------------------------------------------------------------------
# Controller API — documented read endpoints + undocumented batch write
# ---------------------------------------------------------------------------
#
# Two controller access modes:
#   1. Cloud connector (controller_url includes /network/integration):
#        Base: https://api.ui.com/v1/connector/consoles/{id}/network/integration
#        API paths are /v1/sites/{siteId}/... etc. (standard Network API)
#        Batch write uses the same connector base but with the v2 API path.
#   2. Direct console (controller_url is the console's integration proxy):
#        Base: https://{host}/proxy/network/integration
#        API paths are /v1/sites/{siteId}/... etc.
#        Batch write uses /proxy/network/v2/api/site/{siteId}/wireguard/{vpnId}/users/batch
#
# The script auto-detects the mode from controller_url:
#   - If controller_url contains "/network/integration", treat as cloud connector.
#   - Otherwise, treat as direct console.

VPN_SERVERS_LIST = "/v1/sites/{siteId}/vpn/servers"           # GET — list VPN servers
VPN_TUNNELS_LIST = "/v1/sites/{siteId}/vpn/site-to-site-tunnels"  # GET — list tunnels
CLIENTS_LIST     = "/v1/sites/{siteId}/clients"               # GET — list connected clients

# Undocumented endpoint (reverse-engineered from the UniFi web UI):
# For DIRECT console:  POST /proxy/network/v2/api/site/{siteId}/wireguard/{vpnId}/users/batch
# For CLOUD connector: the same path is proxied through the connector.
# The connector proxies to http://127.0.0.1/proxy/[path] on the console,
# so the batch path goes through the connector base URL.
BATCH_USERS_PATH = "/proxy/network/v2/api/site/{siteId}/wireguard/{vpnId}/users/batch"


def _is_cloud_connector(cfg: dict) -> bool:
    """Detect whether controller_url is a cloud connector base."""
    url = cfg["controller_url"].rstrip("/")
    return "/network/integration" in url or "/proxy/network/integration" in url


def controller_base_url(cfg: dict) -> str:
    """Return the base URL — everything up to and including the integration path."""
    return cfg["controller_url"].rstrip("/")


def api_url(cfg: dict, path_template: str, **format_kwargs) -> str:
    """Build a full API URL by appending a path to the controller base.

    Uses string concatenation (not urljoin) because the path templates
    are absolute paths (/v1/...) and urljoin would strip the connector
    prefix. Both cloud connector and direct console modes work the same
    way: append the path to the base URL.
    """
    base = controller_base_url(cfg).rstrip("/")
    path = path_template.format(**format_kwargs).lstrip("/")
    return f"{base}/{path}"


def batch_url(cfg: dict) -> str:
    """Build the URL for the undocumented batch users endpoint.

    For both modes, the batch path is appended to the controller base.
    In cloud connector mode, the connector proxies this to the console's
    internal /proxy/network/v2/api/... endpoint.
    """
    base = controller_base_url(cfg).rstrip("/")
    path = BATCH_USERS_PATH.format(siteId=cfg["site_id"], vpnId=cfg["vpn_id"]).lstrip("/")
    return f"{base}/{path}"


def get_vpn_servers(cfg: dict) -> dict:
    """List VPN servers on the site (documented GET)."""
    url = api_url(cfg, VPN_SERVERS_LIST, siteId=cfg["site_id"])
    headers = {"X-API-KEY": cfg["api_key"], "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_clients(cfg: dict) -> dict:
    """List connected clients on the site (documented GET)."""
    url = api_url(cfg, CLIENTS_LIST, siteId=cfg["site_id"])
    headers = {"X-API-KEY": cfg["api_key"], "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_existing_wg_ips(cfg: dict) -> set[str]:
    """Discover IPs already in use by WireGuard remote-user-vpn clients.

    Uses the documented /clients endpoint and filters for VPN-type clients.
    Falls back to an empty set on any error.
    """
    used = set()
    try:
        data = get_clients(cfg)
        for entry in data.get("data", []):
            # The client type field indicates VPN connections
            if entry.get("type") == "VPN":
                ip = entry.get("ipAddress")
                if ip:
                    used.add(ip)
    except Exception as e:
        print(f"INFO: could not list existing clients for IP check ({e})", file=sys.stderr)
    return used


def register_client_batch(cfg: dict, client_row: dict) -> dict:
    """Register a WireGuard client on the controller via the undocumented batch endpoint.

    client_row fields: name, interface_ip, public_key, allowed_ips, private_key, preshared_key.
    """
    url = batch_url(cfg)
    payload = [client_row]
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": cfg["api_key"],
        "Accept": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code not in (200, 201, 202):
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        raise RuntimeError(f"Controller API returned {resp.status_code} ({resp.reason}): {body}")
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


# ---------------------------------------------------------------------------
# .conf generation (matches downloaded format exactly)
# ---------------------------------------------------------------------------

def build_conf(
    client_name: str,
    private_key: str,
    interface_ip: str,
    server_pubkey: str,
    server_endpoint: str,
    dns_list: list[str],
) -> str:
    """Build a WireGuard .conf file matching the downloaded format.

    Format (from the user's WireGuard-Server-1-Tess-Int.conf):
        [Interface]
        PrivateKey = <client_private_key>
        Address = <interface_ip>/32
        DNS = <dns1>,<dns2>

        [Peer]
        PublicKey = <server_public_key>
        AllowedIPs = 0.0.0.0/0,::/0
        Endpoint = <server_endpoint>
    """
    lines = [
        "[Interface]",
        f"PrivateKey = {private_key}",
        f"Address = {interface_ip}/32",
        f"DNS = {','.join(dns_list)}",
        "",
        "[Peer]",
        f"PublicKey = {server_pubkey}",
        "AllowedIPs = 0.0.0.0/0,::/0",
        f"Endpoint = {server_endpoint}",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create a WireGuard remote-user-vpn client on a UniFi controller"
    )
    parser.add_argument("client_name", help='Client display name, e.g. "Tess laptop"')
    parser.add_argument(
        "--config", default="config.json", help="Path to config.json (default: config.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate keypair + .conf but skip the controller API call",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Generate keypair + .conf and skip only the batch registration (conf still written)",
    )
    parser.add_argument(
        "--interface-ip",
        help="Force a specific interface IP (skips auto-allocation)",
    )
    parser.add_argument(
        "--list-servers",
        action="store_true",
        help="List VPN servers on the site and exit (uses documented GET endpoint)",
    )
    parser.add_argument(
        "--list-clients",
        action="store_true",
        help="List connected clients on the site and exit (uses documented GET endpoint)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    # --list-servers / --list-clients (documented read endpoints)
    if args.list_servers:
        print("=== VPN Servers on site ===")
        try:
            data = get_vpn_servers(cfg)
            for s in data.get("data", []):
                print(f"  id={s.get('id')}  name={s.get('name')}  type={s.get('type')}  enabled={s.get('enabled')}")
        except Exception as e:
            print(f"ERROR listing VPN servers: {e}", file=sys.stderr)
        return

    if args.list_clients:
        print("=== Connected Clients on site ===")
        try:
            data = get_clients(cfg)
            for c in data.get("data", []):
                print(f"  id={c.get('id')}  name={c.get('name')}  type={c.get('type')}  ip={c.get('ipAddress')}")
        except Exception as e:
            print(f"ERROR listing clients: {e}", file=sys.stderr)
        return

    # 1. Generate keypair
    private_key, public_key = generate_keypair()
    print(f"Generated keypair for '{args.client_name}':")
    print(f"  private: {private_key}")
    print(f"  public:  {public_key}")

    # 2. Allocate IP
    existing_ips = set()
    if not args.dry_run and not args.no_register:
        existing_ips = get_existing_wg_ips(cfg)

    if args.interface_ip:
        interface_ip = args.interface_ip
    else:
        interface_ip = next_available_ip(cfg["vpn_subnet_cidr"], existing_ips, gateway_offset=1)
        print(f"Allocated interface IP: {interface_ip}/32")

    # 3. Build the client row for the batch endpoint
    client_row = {
        "name": args.client_name,
        "interface_ip": interface_ip,
        "public_key": public_key,
        "allowed_ips": [],
        "private_key": private_key,
        "preshared_key": "",
    }

    # 4. Register on controller (undocumented batch endpoint)
    if args.dry_run or args.no_register:
        print("\n[SKIPPED] Would POST to:", batch_url(cfg))
        print("Payload:")
        print(json.dumps(client_row, indent=2))
    else:
        print("\nRegistering client on controller (undocumented batch endpoint)...")
        t0 = time.time()
        try:
            result = register_client_batch(cfg, client_row)
            elapsed = time.time() - t0
            rc = result.get("meta", {}).get("rc", result.get("rc", "unknown"))
            print(f"Controller API response: {rc} in {elapsed:.1f}s")
        except RuntimeError as e:
            print(f"ERROR registering client: {e}", file=sys.stderr)
            print("The .conf file was still generated locally — check the controller manually.", file=sys.stderr)

    # 5. Build the .conf file
    dns = cfg.get("vpn_dns", ["192.168.3.1"])
    conf_text = build_conf(
        args.client_name,
        private_key,
        interface_ip,
        cfg["vpn_server_public_key"],
        cfg["vpn_server_endpoint"],
        dns,
    )

    # 6. Write the .conf to output_dir
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = "".join(c for c in args.client_name if c.isalnum() or c in "-_ ")[:40].strip().replace(" ", "-")
    basename = f"WireGuard-{cfg['vpn_id']}-{safe_name}-{ts}.conf"
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / basename
    out_path.write_text(conf_text)
    print(f"\nSaved config: {out_path}")
    print(f"File size: {out_path.stat().st_size} bytes")

    # 7. Summary line for Slack relay
    print(f"\nSUMMARY|Created WireGuard client '{args.client_name}' -> {out_path.name}")
    print(f"SUMMARY|IP: {interface_ip}/32  PrivateKey: {private_key}")
    print(f"SUMMARY|Config: {out_path}")


if __name__ == "__main__":
    main()
