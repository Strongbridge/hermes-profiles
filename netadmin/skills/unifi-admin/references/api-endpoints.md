# UniFi API endpoint reference

Patterns from the tool module (`tools/unifi_api.py`). Verify each path
against the live console before relying on it — the stats route currently
returns 404, so do not treat an unverified path as working.

## Resolution

- List sites: `GET {base}/integration/v1/sites` — returns `data[]` with each
  site's `id` (use that ID in every subsequent call).
- WLAN by name: `GET {base}/integration/v1/sites/{siteId}/wifi/broadcasts?filter=name.eq('{wlanName}')` — returns `data[]` with each WLAN's `id`.
- Resolve a device by MAC on the devices list (the `mac`/`macAddress` field).

## WPA key rotation

- Fetch config: `GET {base}/integration/v1/sites/{siteId}/wifi/broadcasts/{wlanId}`
- PUT the same URL with the config, setting the passphrase inside
  `securityConfiguration.{wpa2Personal|wpa3Personal|wpa2Wpa3Personal}.passphrase`.
- `200 OK` means the key was updated. After success, the technician must
  document the new credentials in SharePoint.

## Switch port modification

- List devices: `GET {base}/integration/v1/sites/{siteId}/devices`
- Fetch device: `GET {base}/integration/v1/sites/{siteId}/devices/{deviceId}`
- PUT device config with a merged `portOverrides` entry:
  `{"portIdx": <n>, "networkId": <profileId>}`, removing any existing entry
  for the same `portIdx`.

## Stats
- The console-proxy stats route (`GET {base}/proxy/network/api/s/{siteId}/{metric}`)
  is DEAD on the current console key — confirmed HTTP 404. Do not re-probe it;
  treat a 404 as confirmed dead, not a key problem.
- Working equivalent: the V1 integration devices endpoint
  (`GET {base}/integration/v1/sites/{siteId}/devices`). The `unifi_get_stats`
  tool ignores the metric parameter and always queries this list; each device
  carries `state` (ONLINE/offline), `macAddress`, `name`, and
  `firmwareVersion`. Summarize the device states as the health snapshot.
- For narrower metrics (clients/sites/dpi), re-probe with the console-proxy
  route only if a live endpoint path is confirmed — never re-probe a known-dead
  route.

## Endpoint scheme status
- The V1 integration scheme (`/integration/v1/sites/{siteId}/...`) is the
  working scheme and is what `unifi_get_stats` and the WPA/switch tools use.
- The console-proxy scheme (`/proxy/network/api/s/{siteId}/{metric}`) is
  DEAD on the current console key — confirmed HTTP 404. Do not re-probe it.