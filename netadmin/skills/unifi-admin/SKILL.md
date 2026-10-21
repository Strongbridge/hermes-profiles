---
name: unifi-admin
description: "Ubiquiti UniFi admin: WPA rotation, switch ports, stats."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [UniFi, Network Admin, API]
    related_skills: [hermes-agent]
---

## When to Use

Use when the IT helpdesk submits a request over Slack to (a) rotate a WLAN's
WPA passphrase, (b) modify a switch port's state or profile, or (c) retrieve
network statistics (health, clients, devices, sites, dpi). The request must be
addressed to the agent; ambient, unaddressed messages do not trigger it.

# UniFi Admin

Network administration over the Ubiquiti UniFi Network API: WPA key rotation,
switch port modification, and network-statistics retrieval.

## Output rules (Slack)

The technician reads on Slack, so run deep and reply tight:

- No wide Markdown tables. Use bulleted lists or labeled lines.
- No conversational filler ("I'd be happy to...", "Great question"). Brief,
  task-affirming confirmations only ("Processing WPA rotation for [Network]...").
- Keep verification and troubleshooting responses concise and highly readable.

## Procedure

1. Classify the request: WPA rotation, switch port modification, or statistics.
2. Extract the required parameters for that operation (see per-operation below).
3. If any required parameter is missing (site ID, WLAN name, Device MAC, port
   number, or metric), STOP and ask the user — never guess. A missing
   parameter means a change would land on the wrong object.
4. Execute the API call through the UniFi toolset.
5. Validate the response:
   - Success (200 OK): confirm the new state, output the relevant values (e.g.,
     the new key), and emit the SharePoint documentation reminder for WPA
     rotations.
   - Failure: report the exact HTTP status code and error message verbatim —
     never soften it into a generic "something went wrong."

### WPA key rotation
- Required: site ID, WLAN name.
- If no new key is supplied, generate a secure 15-character alphanumeric key.
- PUT the new passphrase to the WLAN-conf endpoint; verify 200 OK.
- After success, remind the technician to document the new credentials in
  SharePoint before sending the reply.

### Switch port modification
- Required: Device MAC/ID, target port number, and the requested state
  (enable/disable, VLAN/profile, or name).
- Merge the change for the target port only, then confirm the new port state.

### Network statistics
- Required: metric (health, clients, devices, sites, dpi).
- The console-proxy stats route (`/proxy/network/api/s/{siteId}/{metric}`) is
  DEAD — it returns HTTP 404 on the current console key. Do not re-probe it;
  treat a 404 as confirmed dead, not as a key/site problem.
- The working equivalent is the V1 integration devices endpoint
  (`GET /integration/v1/sites/{siteId}/devices`): the `unifi_get_stats` tool
  ignores the metric parameter and always queries this list of devices, each
  with a `state` field (ONLINE/offline) and `firmwareVersion`. Summarize the
  device states as the health snapshot; field the narrower metric
  (clients/sites/dpi) as a separate request if a real metric endpoint is
  provided.

## Pitfalls

- Never guess a missing critical parameter (site ID, WLAN name, Device MAC,
  port number, metric). Ask.
- WPA key: when none is given, always auto-generate a 15-character key rather
  than blocking the rotation.
- Confirmed WPA rotation → always remind the technician to document the new
  credentials in SharePoint.
- On any PUT/POST failure, quote the HTTP status code and error message
  verbatim; that is the only actionable signal the technician has.
- Before relying on a stats read, know the endpoint's status: the console-proxy
  stats route (`/proxy/network/api/s/{siteId}/{metric}`) is confirmed DEAD
  (HTTP 404) — do not re-probe; the working equivalent is the V1 integration
  devices endpoint (`/integration/v1/sites/{siteId}/devices`).

## API endpoint reference

See `references/api-endpoints.md` for the site/WLAN resolution and the WPA /
switch-port endpoint shapes.