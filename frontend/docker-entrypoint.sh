#!/usr/bin/env sh
# Arkidi Platform frontend container entrypoint.
# Generates the real Nginx config from the committed template by substituting
# SERVER_NAME / SSL_CERT_PATH / SSL_KEY_PATH, then starts nginx.
set -eu

TEMPLATE=/etc/nginx/conf.d/default.conf.template
CONF=/etc/nginx/conf.d/default.conf

SERVER_NAME="${SERVER_NAME:-localhost}"
SSL_CERT_PATH="${SSL_CERT_PATH:-/etc/nginx/certs/fullchain.pem}"
SSL_KEY_PATH="${SSL_KEY_PATH:-/etc/nginx/certs/privkey.pem}"

echo "[arkidi-frontend] Generating nginx config..."
echo "  server_name  : ${SERVER_NAME}"
echo "  ssl_cert     : ${SSL_CERT_PATH}"
echo "  ssl_key      : ${SSL_KEY_PATH}"

# Token substitution (sed). Delimiters are | so paths with '/' are safe.
sed -e "s|__SERVER_NAME__|${SERVER_NAME}|g" \
    -e "s|__SSL_CERT_PATH__|${SSL_CERT_PATH}|g" \
    -e "s|__SSL_KEY_PATH__|${SSL_KEY_PATH}|g" \
    "${TEMPLATE}" > "${CONF}"

echo "[arkidi-frontend] Starting nginx."
exec nginx -g "daemon off;"