#!/bin/bash

DEFAULT_AGENT_NAME="Claude"

INPUT=$(cat)

session_id=$(echo "$INPUT" | jq -r '.session_id')
cwd=$(echo "$INPUT" | jq -r '.cwd')
agent_type=$(echo "$INPUT" | jq -r '.agent_type // empty')

git_root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)
project_id="${git_root:-$cwd}"

agent_name="${agent_type:-$DEFAULT_AGENT_NAME}"

if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "export ATM_SESSION_ID=$session_id" >> "$CLAUDE_ENV_FILE"
    echo "export ATM_PROJECT_ID=$project_id" >> "$CLAUDE_ENV_FILE"
    echo "export ATM_AGENT_NAME=$agent_name" >> "$CLAUDE_ENV_FILE"
fi

exit 0
