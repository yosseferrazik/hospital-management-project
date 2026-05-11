#!/bin/bash
# Check replication lag on primary
psql -U postgres -d hospital_management -t -c \
  "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::int \
   FROM pg_stat_replication;" 2>/dev/null || echo "No replication active"
