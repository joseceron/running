#!/usr/bin/env bash
# Deploy atómico de Liebre — backend Cloud Run + migration alembic + smoke test.
#
# Orden (NO saltar pasos):
#   1. cd correcto a runner-agent
#   2. Tests locales (rápidos, abortan si fallan)
#   3. Build de la imagen Docker → tag :latest
#   4. Migration via Cloud Run Job (sólo si hay alembic nuevo)
#   5. Deploy a Cloud Run con la imagen recién construida
#   6. Smoke test contra /health
#
# Documentación completa: ~/.claude/projects/.../memory/project_deploy_proceso.md
#
# Uso:
#   scripts/deploy.sh           # deploy completo
#   scripts/deploy.sh --skip-tests   # skip pruebas locales (NO recomendado)
#   scripts/deploy.sh --no-migrate   # skip migration job

set -euo pipefail

PROJECT="liebre-mvp"
REGION="us-east1"
SERVICE="liebre-api"
JOB="liebre-migrate"
IMAGE="us-east1-docker.pkg.dev/${PROJECT}/liebre-images/${SERVICE}:latest"
SA="liebre-runtime@${PROJECT}.iam.gserviceaccount.com"
HEALTH_URL="https://${SERVICE}-948756297403.us-east1.run.app/health"

SKIP_TESTS=0
SKIP_MIGRATE=0
for arg in "$@"; do
  case "$arg" in
    --skip-tests) SKIP_TESTS=1 ;;
    --no-migrate) SKIP_MIGRATE=1 ;;
    *) echo "❌ Argumento desconocido: $arg" >&2; exit 1 ;;
  esac
done

# ── 1. cd correcto (crítico — sin esto el build falla silenciosamente) ───
cd "$(dirname "$0")/.."
if [[ ! -f cloudbuild.yaml ]]; then
  echo "❌ No estoy en runner-agent/ (no encuentro cloudbuild.yaml)" >&2
  exit 1
fi

echo "▶ Deploy Liebre — project=${PROJECT} region=${REGION}"
echo "▶ CWD: $(pwd)"

# ── 2. Tests locales ────────────────────────────────────────────────────
if [[ "$SKIP_TESTS" -eq 0 ]]; then
  echo ""
  echo "→ [2/6] Tests locales (pytest tests/unit)"
  if [[ -x .venv/bin/pytest ]]; then
    .venv/bin/pytest tests/unit -q || { echo "❌ Tests fallaron, abortando"; exit 1; }
  else
    echo "⚠️  .venv/bin/pytest no encontrado — saltando (instalar requirements-dev.txt)"
  fi
else
  echo "→ [2/6] Tests SKIPPED (--skip-tests)"
fi

# ── 3. Build de la imagen Docker ────────────────────────────────────────
echo ""
echo "→ [3/6] Build de imagen Docker (Cloud Build)"
BUILD_OUTPUT=$(gcloud builds submit --config cloudbuild.yaml --project "$PROJECT" 2>&1)
echo "$BUILD_OUTPUT" | tail -5
BUILD_STATUS=$(echo "$BUILD_OUTPUT" | grep -E "STATUS$|SUCCESS|FAILURE" | tail -1 | awk '{print $NF}')
if [[ "$BUILD_STATUS" != "SUCCESS" ]]; then
  echo "❌ Build NO terminó con SUCCESS (status: $BUILD_STATUS), abortando"
  exit 1
fi

# ── 4. Migration (sólo si la opción está activa) ────────────────────────
if [[ "$SKIP_MIGRATE" -eq 0 ]]; then
  echo ""
  echo "→ [4/6] Update + execute Cloud Run Job '$JOB' (migrations alembic)"
  gcloud run jobs update "$JOB" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$PROJECT" \
    --service-account "$SA" \
    --set-secrets DATABASE_URL=database-url:latest \
    --set-cloudsql-instances "${PROJECT}:${REGION}:liebre-db" \
    --command alembic --args upgrade,head \
    --quiet
  gcloud run jobs execute "$JOB" --region "$REGION" --project "$PROJECT" --wait
else
  echo "→ [4/6] Migration SKIPPED (--no-migrate)"
fi

# ── 5. Deploy del servicio ──────────────────────────────────────────────
echo ""
echo "→ [5/6] Deploy a Cloud Run"
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --project "$PROJECT" \
  --quiet

# ── 6. Smoke test ───────────────────────────────────────────────────────
echo ""
echo "→ [6/6] Smoke test /health"
if curl -fsSL -o /dev/null -m 30 "$HEALTH_URL"; then
  echo "✓ Health check OK"
else
  echo "❌ Health check FALLÓ — considera rollback con:"
  PREV=$(gcloud run revisions list --service "$SERVICE" --region "$REGION" --project "$PROJECT" \
    --format="value(metadata.name)" --limit=2 | tail -1)
  echo "  gcloud run services update-traffic $SERVICE --to-revisions=$PREV=100 --region $REGION --project $PROJECT"
  exit 1
fi

echo ""
echo "✅ Deploy completado correctamente."
echo "   Backend: $HEALTH_URL"
echo "   Frontend: https://liebre.run (Firebase App Hosting — automático tras git push)"
