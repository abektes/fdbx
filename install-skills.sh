#!/usr/bin/env bash
# Install the fdbx plugin for Claude Code.
# This is only needed for permanent installation.
# For one-off use, run: claude --plugin-dir /path/to/this-repo

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGINS_DIR="$HOME/.claude/plugins"
PLUGIN_LINK="$PLUGINS_DIR/fdbx"

mkdir -p "$PLUGINS_DIR"
ln -sfn "$REPO_DIR" "$PLUGIN_LINK"

echo "Installed fdbx plugin at $PLUGIN_LINK"
echo ""
echo "Skills are now available as /fdbx:<name>."
echo "Try /fdbx:help to get routed to the right method."
echo ""
echo "To uninstall: rm $PLUGIN_LINK"
