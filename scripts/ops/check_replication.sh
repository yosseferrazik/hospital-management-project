#!/bin/bash

OUT=$(sudo -u postgres psql -d hsp_db -t -A -c \
"SELECT COALESCE(MAX(EXTRACT(EPOCH FROM replay_lag))::int, -1)
 FROM pg_stat_replication;" 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "ERROR: psql failed"
  exit 1
fi

if [ "$OUT" -eq -1 ]; then
  echo "No replication active"
else
  echo "Replication lag: ${OUT}s"
fi