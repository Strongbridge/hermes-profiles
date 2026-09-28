#!/usr/bin/env python3
"""
slack_post.py — post a message to a Slack channel as the BA bot.
Callable from BA's terminal tool.

Usage:
    python slack_post.py <channel_id_or_name> <message>
    python slack_post.py C0C2HAGS2QN "Hello from BA"
    python slack_post.py "#clin9-requirements" "Hello"           (needs channel in directory)
    python slack_post.py C0C2HAGS2QN "Reply" --thread-ts 123.45  (reply in thread)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse


BA_PROFILE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\DanRighter\AppData\Local"), "hermes", "profiles", "ba")
CHANNEL_DIR = os.path.join(BA_PROFILE_DIR, "channel_directory.json")


def get_ba_token():
    env_path = os.path.join(BA_PROFILE_DIR, ".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SLACK_BOT_TOKEN="):
                return line.split("=", 1)[1]
    return None


def load_channel_map():
    if not os.path.exists(CHANNEL_DIR):
        return {}
    with open(CHANNEL_DIR, encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for entry in data.get("platforms", {}).get("slack", []):
        cid = entry.get("id", "")
        name = entry.get("name", "")
        if ":" in cid:
            continue
        if cid and name:
            mapping[name.lower()] = cid
            mapping[cid] = cid
    return mapping


def post_message(token, channel, text, thread_ts=None):
    url = "https://slack.com/api/chat.postMessage"
    params = {
        "channel": channel,
        "text": text,
        "as_user": "true",
    }
    if thread_ts:
        params["thread_ts"] = thread_ts

    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Post to Slack as the BA bot")
    parser.add_argument("channel", help="Channel ID or name (e.g. C0C2HAGS2QN or #clin9-requirements)")
    parser.add_argument("text", help="Message text")
    parser.add_argument("--thread-ts", help="Thread timestamp to reply in")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON")
    args = parser.parse_args()

    token = get_ba_token()
    if not token:
        print("ERROR: Could not read SLACK_BOT_TOKEN from BA profile .env", file=sys.stderr)
        sys.exit(1)

    channel_map = load_channel_map()
    channel_id = args.channel

    if channel_id not in channel_map:
        lower = channel_id.lower()
        if lower in channel_map:
            channel_id = channel_map[lower]
        elif channel_id.startswith("#"):
            name = channel_id[1:].lower()
            if name in channel_map:
                channel_id = channel_map[name]

    result = post_message(token, channel_id, args.text, args.thread_ts)

    if args.raw:
        print(json.dumps(result, indent=2))
    elif result.get("ok"):
        ts = result.get("ts", "?")
        posted_channel = result.get("channel")
        if isinstance(posted_channel, dict):
            name = posted_channel.get("name", "?")
        else:
            name = posted_channel
        print(f"Posted to {channel_id} at {ts} (name={name})")
    else:
        print(f"FAILED: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

