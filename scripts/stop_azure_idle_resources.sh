#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

RESOURCE_GROUP="${FICOPILOT_RESOURCE_GROUP:-rg-ai-learning}"
POSTGRES_NAME="${FICOPILOT_PG_NAME:-ficopilot-pg-kudou-dev}"
APP_NAME="${FICOPILOT_APP_NAME:-ficopilot-app-kudou-dev}"

if ! command -v az >/dev/null; then
  echo "az CLI is not installed." >&2
  exit 1
fi

if ! az account show >/dev/null 2>&1; then
  echo "az is not logged in. Run: az login" >&2
  exit 1
fi

pg_state="$(
  az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_NAME" \
    --query state \
    --output tsv
)"

if [[ "$pg_state" != "Stopped" ]]; then
  echo "Stopping PostgreSQL (state=$pg_state)"
  az postgres flexible-server stop \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_NAME"
else
  echo "PostgreSQL already Stopped"
fi

echo "Scaling Container App to min=0"
az containerapp update \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --min-replicas 0 \
  --max-replicas 1 \
  --output none

echo "Idle shutdown finished."
