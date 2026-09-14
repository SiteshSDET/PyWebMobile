#!/usr/bin/env python3
"""
Simple smoke test runner for SITE_URL. Checks:
- HTTP status is 200
- Response contains HTML ("<html")

Exits with code 0 on success, 2 on failure.
"""
import os
import sys
import urllib.request

url = os.environ.get("SITE_URL", "https://siteshsdet.netlify.app/")
print(f"Running smoke tests against: {url}")

try:
    with urllib.request.urlopen(url, timeout=15) as r:
        status = r.status
        body = r.read(1024*100).decode('utf-8', errors='ignore')
        print(f"HTTP status: {status}")
        if status != 200:
            print("FAIL: Status not 200")
            sys.exit(2)
        if "<html" not in body.lower():
            print("FAIL: Response does not look like HTML")
            sys.exit(2)
except Exception as e:
    print(f"ERROR: Exception during request: {e}")
    sys.exit(2)

print("OK: Smoke tests passed")
sys.exit(0)
