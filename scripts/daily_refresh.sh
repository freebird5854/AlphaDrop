#!/bin/bash
# ALPHA DROP - Daily Data Refresh Cron Job
# Add this to crontab: 0 6 * * * /app/scripts/daily_refresh.sh

API_URL="${REACT_APP_BACKEND_URL:-http://localhost:8001}"
CRON_KEY="${CRON_API_KEY:-alpha-drop-cron-2024}"

echo "$(date): Starting daily data refresh..."

response=$(curl -s -X POST "${API_URL}/api/cron/refresh-data?api_key=${CRON_KEY}")

echo "$(date): Response: ${response}"

# Log to file
echo "$(date): ${response}" >> /var/log/alpha_drop_cron.log
