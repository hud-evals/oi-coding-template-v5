#!/bin/bash
# Entrypoint script for OI evaluation container
# Starts the secure grading server before running the main command
# 
# The grading server runs as the 'grader' user who has exclusive access to /grading
# The agent (ubuntu user) cannot access /grading directly
#
# This script runs as root to:
# 1. Start the grading server as 'grader' user
# 2. Execute the main command as 'ubuntu' user

set -e

GRADING_LOG="/tmp/grading_server.log"

# Ensure venv is in PATH
export PATH="/mcp_server/.venv/bin:$PATH"

echo "Starting grading server..." >&2

# Start grading server as grader user in background (runs as root, switches to grader)
su -s /bin/bash grader -c "
    source /mcp_server/.venv/bin/activate
    python -m hud_controller.grading_server > $GRADING_LOG 2>&1
" &

GRADING_PID=$!

# Wait for grading server to be ready
echo "Waiting for grading server to start..." >&2
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
        echo "Grading server is ready!" >&2
        break
    fi
    sleep 0.5
    WAITED=$((WAITED + 1))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo "WARNING: Grading server may not have started properly" >&2
    echo "Last log output:" >&2
    tail -20 "$GRADING_LOG" >&2 2>/dev/null || echo "(no log available)" >&2
fi

# Execute the main command as root (MCP server needs access to env.py and tasks/)
# Tool calls (bash/edit) demote to ubuntu user
echo "Starting main command: $@" >&2

if [ $# -eq 0 ]; then
    exec bash
fi

exec "$@"
