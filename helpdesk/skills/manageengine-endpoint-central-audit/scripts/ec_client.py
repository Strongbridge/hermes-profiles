"""
Endpoint Central API Client & Audit Helper Script
Handles authentication via Zoho OAuth Refresh Token or Static API Key,
and executes audit queries against Endpoint Central and Microsoft Graph.
"""

import os
import sys
import json
import random
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

def load_env_credentials():
    """Load credentials from active profile .env or environment variables."""
    creds = {
        "CLIENT_ID": os.environ.get("CLIENT_ID"),
        "CLIENT_SECRET": os.environ.get("CLIENT_SECRET"),
        "REFRESH_TOKEN": os.environ.get("REFRESH_TOKEN"),
        "ACCOUNTS_URL": os.environ.get("ACCOUNTS_URL", "https://accounts.zoho.com"),
        "DC_BASE_URL": os.environ.get("DC_BASE_URL", "https://endpointcentral.manageengine.com"),
        "EC_API_KEY": os.environ.get("EC_API_KEY"),
        "CUSTOMER_ID": os.environ.get("CUSTOMER_ID") or os.environ.get("EC_CUSTOMER_ID")
    }

    # If missing, check local profile .env file
    profile_env = os.path.expanduser(r"~\AppData\Local\hermes\profiles\helpdesk\.env")
    if os.path.exists(profile_env):
        try:
            with open(profile_env, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if not creds.get(k) and v:
                            creds[k] = v
        except Exception as e:
            print(f"[WARN] Failed reading profile .env: {e}", file=sys.stderr)

    return creds

def get_auth_header(creds):
    """Obtain Authorization header via OAuth refresh or static API key."""
    if creds.get("REFRESH_TOKEN") and creds.get("CLIENT_ID") and creds.get("CLIENT_SECRET"):
        token_url = f"{creds['ACCOUNTS_URL']}/oauth/v2/token"
        params = urllib.parse.urlencode({
            "client_id": creds["CLIENT_ID"],
            "client_secret": creds["CLIENT_SECRET"],
            "refresh_token": creds["REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        }).encode("utf-8")
        req = urllib.request.Request(token_url, data=params, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "access_token" in data:
                    return {"Authorization": f"Zoho-oauthtoken {data['access_token']}"}
                else:
                    raise RuntimeError(f"OAuth response missing access_token: {data}")
        except Exception as e:
            raise RuntimeError(f"OAuth token refresh failed: {e}")
    elif creds.get("EC_API_KEY"):
        return {"Authorization": f"Bearer {creds['EC_API_KEY']}"}
    else:
        raise ValueError("No valid credentials found (need REFRESH_TOKEN/CLIENT_ID or EC_API_KEY)")

def api_get(url, headers):
    """Execute GET request returning parsed JSON."""
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def exchange_grant_code(accounts_url, client_id, client_secret, grant_code):
    """Exchange a Self Client one-time grant code for access and refresh tokens."""
    token_url = f"{accounts_url}/oauth/v2/token"
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": grant_code,
        "grant_type": "authorization_code"
    }).encode("utf-8")
    req = urllib.request.Request(token_url, data=params, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_ms_graph_token(tenant_id, client_id, client_secret):
    """Obtain Microsoft Graph application token via client credentials flow."""
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }).encode("utf-8")
    req = urllib.request.Request(token_url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8")).get("access_token")

