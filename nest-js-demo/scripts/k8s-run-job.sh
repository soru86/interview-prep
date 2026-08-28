#!/usr/bin/env bash
set -euo pipefail

JOB_MANIFEST="${1:?Job manifest path is required}"
NAMESPACE="${2:-nest-js-demo-ci}"
TEST_RUNNER_IMAGE="${3:?TEST_RUNNER_IMAGE is required}"
AUTOMATION_BASE_URL="${4:-http://nest-js-demo-staging:3000}"
JOB_NAME="${5:-}"

if [[ -z "${JOB_NAME}" ]]; then
  JOB_NAME="$(grep '^  name:' "${JOB_MANIFEST}" | head -1 | awk '{print $2}')"
fi

echo "Applying Job ${JOB_NAME} in namespace ${NAMESPACE}"

TMP_FILE="$(mktemp)"
trap 'rm -f "${TMP_FILE}"' EXIT

sed \
  -e "s|TEST_RUNNER_IMAGE|${TEST_RUNNER_IMAGE}|g" \
  -e "s|AUTOMATION_BASE_URL|${AUTOMATION_BASE_URL}|g" \
  "${JOB_MANIFEST}" > "${TMP_FILE}"

kubectl delete job "${JOB_NAME}" -n "${NAMESPACE}" --ignore-not-found=true
kubectl apply -f "${TMP_FILE}"

echo "Waiting for Job ${JOB_NAME} to complete..."
kubectl wait --for=condition=complete "job/${JOB_NAME}" -n "${NAMESPACE}" --timeout=900s

echo "Job logs:"
kubectl logs "job/${JOB_NAME}" -n "${NAMESPACE}" --all-containers=true || true

echo "Job ${JOB_NAME} completed successfully"
