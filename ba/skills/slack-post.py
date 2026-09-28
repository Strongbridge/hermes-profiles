#!/usr/bin/env python3
"""
slack-post.py — post a message to a Slack channel as the BA bot.

Usage:
    python slack-post.py --channel C0C2HAGS2QN --text "Hello from BA"
    python slack-post.py --channel-name "#clin9-requirements" --text "Hello"
    python slack-post.py --channel C0C2HAGS2QN --text "Hello" --thread-ts 1234.5678

Reads the BA bot token from the per-profile .env file automatically.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse


def get_ba_token():
    """Read the BA profile's Slack bot token from its .env file."""
    env_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\hermes\profiles\ba\.env"),
        os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\DanRighter\AppData\Local"),
                     "hermes", "profiles", "ba", ".env"),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SLACK_BOT_TOKEN="):
                        return line.split("=", 1)[1]
    return None


def post_message(token, channel, text, thread_ts=None, as_user=False):
    """Post a message to Slack via chat.postMessage."""
    url = "https://slack.com/api/chat.postMessage"
    params = {
        "channel": channel,
        "text": text,
        "as_user": str(as_user).lower(),
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
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            result = {"ok": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Post a message to a Slack channel as the BA bot"
    )
    group = parser.add_argument_group("target")
    group.add_argument("--channel", help="Channel ID (e.g. C0C2HAGS2QN)")
    group.add_argument("--channel-name", help="Channel name with # (e.g. #clin9-requirements)")
    parser.add_argument("--text", required=True, help="Message text")
    parser.add_argument("--thread-ts", help="Thread timestamp to reply in")
    parser.add_argument("--as-user", action="store_true", help="Post as the bot user (default False)")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response")

    args = parser.parse_args()

    if not args.channel and not args.channel_name:
        parser.error("specify --channel or --channel-name")

    token = get_ba_token()
    if not token:
        print("ERROR: Could not read SLACK_BOT_TOKEN from BA profile .env", file=sys.stderr)
        sys.exit(1)

    channel = args.channel or args.channel_name

    result = post_message(token, channel, args.text, args.thread_ts, args.as_user)

    if args.raw:
        print(json.dumps(result, indent=2))
    elif result.get("ok"):
        print(f"Posted to {channel}: {result.get('ts')}")
        if result.get("channel"):
            print(f"Channel: {result['channel'].get('name', result['channel'].get('id'))}")
    else:
        print(f"FAILED: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
