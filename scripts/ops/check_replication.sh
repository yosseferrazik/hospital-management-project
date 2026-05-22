#!/bin/bash

LAG=$(sudo -u postgres psql -d hsp_db -t -A -c \
"SELECT COALESCE(MAX(EXTRACT(EPOCH FROM replay_lag))::int, 0)
 FROM pg_stat_replication;" 2>/dev/null)

echo "Replication lag: ${LAG}s"