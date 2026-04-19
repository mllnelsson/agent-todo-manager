#!/usr/bin/env bash
set -euo pipefail

REPO_URL="git@github.com:mllnelsson/agent-todo-manager.git"
INSTALL_DIR="${HOME}/.local/share/atm"
DB_PATH="${INSTALL_DIR}/app.db"
ATM_DATABASE_URL="sqlite:////${DB_PATH#/}"

command -v git >/dev/null || { echo "git not found" >&2; exit 1; }
command -v uv  >/dev/null || { echo "uv not found. See https://docs.astral.sh/uv/" >&2; exit 1; }

# Clone or update
if [[ -d "${INSTALL_DIR}/.git" ]]; then
  echo "Updating existing clone at ${INSTALL_DIR}"
  git -C "${INSTALL_DIR}" pull --ff-only
else
  mkdir -p "$(dirname "${INSTALL_DIR}")"
  git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

# Install CLI globally
uv tool install --force "${INSTALL_DIR}/atm-cli"

# Sync workspace so alembic and uvicorn work from the clone
(cd "${INSTALL_DIR}" && uv sync)

# Run DB migrations
export ATM_DATABASE_URL
(cd "${INSTALL_DIR}/db" && uv run alembic upgrade head)

# Persist ATM_DATABASE_URL in shell rc — only if not already present
case "${SHELL:-}" in
  */zsh)  RC="${HOME}/.zshrc" ;;
  */bash) RC="${HOME}/.bashrc" ;;
  *)      RC="" ;;
esac

if [[ -n "${RC}" ]]; then
  if ! grep -q "ATM_DATABASE_URL" "${RC}" 2>/dev/null; then
    printf '\n# agent-todo-manager\nexport ATM_DATABASE_URL=%s\n' "${ATM_DATABASE_URL}" >> "${RC}"
    echo "Added ATM_DATABASE_URL to ${RC}"
  else
    echo "ATM_DATABASE_URL already present in ${RC} — leaving untouched"
  fi
else
  echo "Unknown shell; add manually: export ATM_DATABASE_URL=${ATM_DATABASE_URL}"
fi

cat <<EOF

atm installed at ~/.local/bin/atm
DB:  ${DB_PATH}
Reload your shell (or: source ${RC:-~/.profile}) to pick up ATM_DATABASE_URL.
Ensure ~/.local/bin is on PATH (try: uv tool update-shell).
EOF
