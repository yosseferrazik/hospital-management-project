#!/bin/bash
# /usr/local/bin/check_cert_expiry.sh -> scripts/ops/check_cert_expiry.sh

CERT="/etc/ssl/certs/postgresql.crt"

if [ ! -f "$CERT" ]; then
  echo "ERROR: cert not found"
  logger -t cert-check "missing cert"
  exit 1
fi

EXP=$(openssl x509 -in "$CERT" -noout -enddate 2>/dev/null | cut -d= -f2)
[ -z "$EXP" ] && echo "ERROR: unreadable cert" && exit 1

DAYS=$(( ( $(date -d "$EXP" +%s) - $(date +%s) ) / 86400 ))

if [ "$DAYS" -lt 30 ]; then
  echo "WARN: expires in $DAYS days"
  logger -t cert-check "expires in $DAYS days"
else
  echo "OK: $DAYS days left"
fi
