#!/usr/bin/env python3
"""
GitHub Stars Fetcher
Fetches all starred repos for the authenticated user via gh CLI.
Outputs JSON to stdout.

Usage:
    python fetch_stars.py [--limit N] [--output FILE]
"""

import json
import subprocess
import argparse
import sys


def fetch_stars(limit=None):
    """Fetch starred repos using gh CLI."""
    cmd = [
        "gh",
        "api",
        "user/starred",
        "--paginate",
        "-q",
        ".[] | {full_name, description, language, stargazers_count, html_url, topics, pushed_at, created_at, owner: {login, html_url}}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching stars: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: gh CLI not found. Please install it first.", file=sys.stderr)
        sys.exit(1)

    repos = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            try:
                repos.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit:
        repos = repos[:limit]

    return repos


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub starred repositories")
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of results"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output file path (default: stdout)"
    )
    args = parser.parse_args()

    repos = fetch_stars(limit=args.limit)

    output = json.dumps(repos, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved {len(repos)} starred repos to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
