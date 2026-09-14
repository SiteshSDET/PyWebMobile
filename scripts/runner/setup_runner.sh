#!/usr/bin/env bash
# Setup script for a GitHub self-hosted runner with GUI (Chrome, Xvfb, VNC, ffmpeg).
# Run as normal user on an Ubuntu x64 VM. Provide REPO_URL and RUNNER_TOKEN as env vars.

set -euo pipefail

if [ -z "${REPO_URL:-}" ] || [ -z "${RUNNER_TOKEN:-}" ]; then
  echo "Usage: REPO_URL=https://github.com/OWNER/REPO RUNNER_TOKEN=... bash setup_runner.sh"
  exit 1
fi

RUNNER_DIR=/opt/actions-runner
sudo mkdir -p "$RUNNER_DIR"
sudo chown "$USER":"$USER" "$RUNNER_DIR"
cd "$RUNNER_DIR"

echo "Downloading Actions runner..."
ARCH=$(uname -m)
# normalize arch for GitHub release asset
if [ "$ARCH" = "x86_64" ]; then ARCH=x64; fi
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then ARCH=arm64; fi

LATEST_URL="https://github.com/actions/runner/releases/latest/download/actions-runner-linux-${ARCH}.tar.gz"
curl -O -L "$LATEST_URL"
# extract
tar xzf actions-runner-linux-*.tar.gz

# configure runner (uses RUNNER_TOKEN and REPO_URL env vars)
./config.sh --url "$REPO_URL" --token "$RUNNER_TOKEN" --labels copilot-runner --name "copilot-runner-$(hostname)"

# Install runner service
sudo ./svc.sh install
sudo ./svc.sh start

# Install system packages for browser and VNC
echo "Installing browser and display packages (may require sudo)..."
sudo apt-get update
sudo apt-get install -y wget gnupg ca-certificates x11vnc xvfb ffmpeg tigervnc-standalone-server

# Install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Start virtual display and VNC (display :1)
if ! pgrep -f "Xvfb :1" >/dev/null 2>&1; then
  Xvfb :1 -screen 0 1280x800x24 &>/var/log/xvfb.log &
  sleep 1
fi
export DISPLAY=:1

# Start VNC server; first-time run will prompt to set password
if ! pgrep -f "Xtightvnc" >/dev/null 2>&1 && ! pgrep -f "Xvnc" >/dev/null 2>&1; then
  echo "Starting VNC server on :1 (display 5901). Run 'vncpasswd' once to set a password if needed.'"
  vncserver :1 -geometry 1280x800 -depth 24 || true
fi

cat <<EOF

Setup complete.
- Runner installed at $RUNNER_DIR and registered for $REPO_URL with label 'copilot-runner'.
- DISPLAY=:1 is started (Xvfb), VNC available on port 5901.
- To connect: use a VNC client to <VM_IP>:5901 (set VNC password if prompted).
- In your workflow, set runs-on: [self-hosted, copilot-runner] and export DISPLAY=:1 before running headed tests.

Security note: the runner is trusted and has access to the host. Restrict network access and rotate registration tokens when done.
EOF
