#!/usr/bin/env bash
# Install the fdbx plugin for Claude Code from its marketplace.
#
#   ./install-skills.sh           install from GitHub (abektes/fdbx)
#   ./install-skills.sh --local   install from this checkout (for development)
#
# Inside Claude Code the same thing is two commands:
#   /plugin marketplace add abektes/fdbx
#   /plugin install fdbx@fdbx
# For a one-off session without installing: claude --plugin-dir /path/to/this-repo

set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed. See https://code.claude.com/docs for setup." >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="abektes/fdbx"
[ "${1:-}" = "--local" ] && SOURCE="$REPO_DIR"

claude plugin marketplace add "$SOURCE"
claude plugin install fdbx@fdbx

echo ""
echo "fdbx is installed. In Claude Code:"
echo "  /fdbx:help                                   get routed to the right method"
echo "  /fdbx:<method>                               run one directly, e.g. /fdbx:four-futures"
echo "  claude --agent fdbx:futures-design-specialist   start a session with the futures agent"
echo ""
echo "Update:    claude plugin marketplace update fdbx && claude plugin update fdbx@fdbx"
echo "Uninstall: claude plugin uninstall fdbx@fdbx"
