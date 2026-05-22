#!/bin/bash
# /usr/local/bin/check_cert_expiry.sh -> scripts/ops/check_cert_expiry.sh
EXPIRY=$(openssl x509 -in /etc/ssl/certs/postgresql.crt -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "WARNING: PostgreSQL certificate expires in $DAYS_LEFT days" | logger -t cert-check
fi
