#!/usr/bin/env bash
# Affiche le solde de crédits KIE AI. Lit la clé depuis $KIEAI_API_KEY ou .env (jamais affichée).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -z "${KIEAI_API_KEY:-}" ] && [ -f .env ]; then set -a; . ./.env; set +a; fi
: "${KIEAI_API_KEY:?KIEAI_API_KEY absente : definir dans .env ou en variable d environnement}"
curl -sS -m 20 -H "Authorization: Bearer ${KIEAI_API_KEY}" https://api.kie.ai/api/v1/chat/credit
echo
