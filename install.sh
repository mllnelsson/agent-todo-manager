#!/bin/sh
set -eu

REPO_URL="git@github.com:mllnelsson/agent-todo-manager.git"
INSTALL_DIR="${HOME}/.local/share/atm"
DB_PATH="${INSTALL_DIR}/app.db"
ATM_DATABASE_URL="sqlite:////${DB_PATH#/}"

command -v git  >/dev/null || { echo "git not found" >&2; exit 1; }
command -v uv   >/dev/null || { echo "uv not found. See https://docs.astral.sh/uv/" >&2; exit 1; }
command -v jq   >/dev/null || { echo "jq not found" >&2; exit 1; }
command -v node >/dev/null || { echo "node not found (required to build the GUI)" >&2; exit 1; }
command -v npm  >/dev/null || { echo "npm not found (required to build the GUI)" >&2; exit 1; }

# Clone or update
if [ -d "${INSTALL_DIR}/.git" ]; then
  echo "Updating existing clone at ${INSTALL_DIR}"
  git -C "${INSTALL_DIR}" pull --ff-only
else
  mkdir -p "$(dirname "${INSTALL_DIR}")"
  git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

# Install CLI globally
uv tool install --force --reinstall-package db --reinstall-package dashboard "${INSTALL_DIR}/atm-cli"

# Sync workspace so alembic and uvicorn work from the clone
(cd "${INSTALL_DIR}" && uv sync)

# Build the GUI so `atm admin serve` has assets to serve
(cd "${INSTALL_DIR}/gui" && npm install && npm run build)
GUI_DIST="${INSTALL_DIR}/gui/dist"

# Patch plugin hooks.json with the resolved absolute script path
PLUGIN_DIR="${INSTALL_DIR}/resources/plugin"
HOOK_SCRIPT="${PLUGIN_DIR}/hooks/atm_session_start.sh"

chmod +x "${HOOK_SCRIPT}"

TMP=$(mktemp)
jq --arg cmd "${HOOK_SCRIPT}" '
  (.hooks.SessionStart[].hooks[] | select(.command == "INSTALL_PATH_PLACEHOLDER" or .command != $cmd)).command = $cmd
' "${PLUGIN_DIR}/hooks/hooks.json" > "${TMP}" && mv "${TMP}" "${PLUGIN_DIR}/hooks/hooks.json"

# Run DB migrations
export ATM_DATABASE_URL
(cd "${INSTALL_DIR}/db" && uv run alembic upgrade head)

# Persist ATM_DATABASE_URL in shell rc — only if not already present
case "${SHELL:-}" in
  */zsh)  RC="${HOME}/.zshrc" ;;
  */bash) RC="${HOME}/.bashrc" ;;
  *)      RC="" ;;
esac

if [ -n "${RC}" ]; then
  if ! grep -q "ATM_DATABASE_URL" "${RC}" 2>/dev/null; then
    printf '\n# agent-todo-manager\nexport ATM_DATABASE_URL=%s\n' "${ATM_DATABASE_URL}" >> "${RC}"
    echo "Added ATM_DATABASE_URL to ${RC}"
  else
    echo "ATM_DATABASE_URL already present in ${RC} — leaving untouched"
  fi
  if ! grep -q "ATM_GUI_DIST" "${RC}" 2>/dev/null; then
    printf 'export ATM_GUI_DIST=%s\n' "${GUI_DIST}" >> "${RC}"
    echo "Added ATM_GUI_DIST to ${RC}"
  else
    echo "ATM_GUI_DIST already present in ${RC} — leaving untouched"
  fi
else
  echo "Unknown shell; add manually:"
  echo "  export ATM_DATABASE_URL=${ATM_DATABASE_URL}"
  echo "  export ATM_GUI_DIST=${GUI_DIST}"
fi

cat <<EOF

atm installed at ~/.local/bin/atm
DB:       ${DB_PATH}
GUI:      ${GUI_DIST}
Dashboard: launch with  atm admin serve  then open http://127.0.0.1:8000/
Plugin:   load once in Claude Code with:
          claude --plugin-dir ${PLUGIN_DIR}
Reload your shell (or: source ${RC:-~/.profile}) to pick up ATM_DATABASE_URL and ATM_GUI_DIST.
Ensure ~/.local/bin is on PATH (try: uv tool update-shell).
EOF
