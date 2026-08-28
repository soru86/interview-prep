#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT_DIR="${ROOT}/docker/certs"
DAYS=3650
CA_SUBJ="/CN=GraphQL Demo Local CA"

mkdir -p "${CERT_DIR}"

if [[ ! -f "${CERT_DIR}/ca.key" ]]; then
  openssl genrsa -out "${CERT_DIR}/ca.key" 4096
  openssl req -x509 -new -nodes -key "${CERT_DIR}/ca.key" -sha256 -days "${DAYS}" \
    -out "${CERT_DIR}/ca.crt" -subj "${CA_SUBJ}"
fi

gen_cert() {
  local name="$1"
  local cn="$2"
  local key="${CERT_DIR}/${name}.key"
  local csr="${CERT_DIR}/${name}.csr"
  local crt="${CERT_DIR}/${name}.crt"
  local ext="${CERT_DIR}/${name}.ext"

  cat > "${ext}" <<EOF
subjectAltName = DNS:localhost,DNS:${cn},IP:127.0.0.1
extendedKeyUsage = serverAuth, clientAuth
EOF

  openssl genrsa -out "${key}" 2048
  openssl req -new -key "${key}" -out "${csr}" -subj "/CN=${cn}"
  openssl x509 -req -in "${csr}" -CA "${CERT_DIR}/ca.crt" -CAkey "${CERT_DIR}/ca.key" \
    -CAcreateserial -out "${crt}" -days "${DAYS}" -sha256 -extfile "${ext}"
  rm -f "${csr}" "${ext}"
  echo "Generated ${crt}"
}

SERVICES=(
  "register-service:register-service"
  "login-service:login-service"
  "profile-service:profile-service"
  "order-service:order-service"
  "notification-service:notification-service"
  "catalog-service:catalog-service"
  "api-gateway:api-gateway"
  "gateway-client:gateway-client"
)

for entry in "${SERVICES[@]}"; do
  IFS=':' read -r file cn <<< "${entry}"
  gen_cert "${file}" "${cn}"
done

cp "${CERT_DIR}/ca.crt" "${CERT_DIR}/ca-bundle.crt"
echo "Certificates written to ${CERT_DIR}"
