"""
Pytest-compatible smoke test for SITE_URL.
"""
import os
import urllib.request

SITE_URL = os.environ.get("SITE_URL", "https://siteshsdet.netlify.app/")


def test_site_returns_200():
    with urllib.request.urlopen(SITE_URL, timeout=15) as r:
        assert r.status == 200


def test_site_is_html():
    with urllib.request.urlopen(SITE_URL, timeout=15) as r:
        body = r.read(1024*100).decode('utf-8', errors='ignore')
        assert '<html' in body.lower()
