#!/usr/bin/env python3
"""
Simple script to ping SITE_URL (reads SITE_URL from environment).
Run locally: python3 scripts/mcp/ping_site.py
In GitHub Actions the copilot setup workflow exports SITE_URL to GITHUB_ENV so this script can use it.
"""
import os
import urllib.request

url = os.environ.get("SITE_URL", "https://siteshsdet.netlify.app/")
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        print(f"{url} -> {r.status}")
except Exception as e:
    print(f"Error accessing {url}: {e}")
