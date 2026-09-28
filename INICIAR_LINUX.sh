#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 run_portal.py &
PORTAL_PID=$!
(cd datacenter_original && python3 main.py) &
DC_PID=$!
python3 run_physics.py &
PHYSICS_PID=$!
echo "UnifiedLab portal: http://127.0.0.1:8000"
trap 'kill "$PORTAL_PID" "$DC_PID" "$PHYSICS_PID" 2>/dev/null || true' EXIT
wait
