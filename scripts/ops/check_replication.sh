#!/bin/bash
# Check replication lag on primary
psql -U postgres -d hsp_db -t -c \
  "SELECT EXTRACT(EPOCH FROM replay_lag)::int \
   FROM pg_stat_replication;" 2>/dev/null || echo "No replication active"
