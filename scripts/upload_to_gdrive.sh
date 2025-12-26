#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-outputs}"
REMOTE="${2:-gdrive:archon-backups}"

if [ -z "${REMOTE}" ]; then
  echo "RCLONE remote must be provided (e.g. gdrive:folder)."
  exit 2
fi

if [ ! -f /tmp/rclone_sa.json ]; then
  echo "/tmp/rclone_sa.json (service account JSON) not found. Exiting."
  exit 3
fi

mkdir -p ~/.config/rclone
cat > ~/.config/rclone/rclone.conf <<'EOF'
[gdrive]
type = drive
scope = drive
service_account_file = /tmp/rclone_sa.json
token = {}
EOF
chmod 600 ~/.config/rclone/rclone.conf

echo "rclone config written"

rclone copy "${OUT_DIR}" "${REMOTE}" --no-traverse --verbose

echo "Uploaded ${OUT_DIR} -> ${REMOTE}"
