MCP / Copilot automation examples

This folder contains simple examples to help integrate Copilot cloud agent (MCP) with this repository and the SITE_URL environment.

- ping_site.py — simple script that reads SITE_URL from the environment and performs an HTTP GET.

Usage:
- Ensure the repository or copilot environment has the SITE_URL secret set to https://siteshsdet.netlify.app/
- Locally: python3 scripts/mcp/ping_site.py
- In CI/Actions: the copilot setup steps workflow exports SITE_URL into GITHUB_ENV so scripts can access it via os.environ['SITE_URL']
