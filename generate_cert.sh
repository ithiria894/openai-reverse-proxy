#!/bin/bash

# 設置證書儲存目錄
CERT_DIR="/etc/nginx/ssl"
mkdir -p "$CERT_DIR"

# 生成私鑰 (nginx.key)
echo "Generating private key (nginx.key)..."
sudo openssl genrsa -out "$CERT_DIR/nginx.key" 2048

# 使用內聯 SAN 配置生成證書簽名請求 (nginx.csr)
echo "Generating certificate signing request (nginx.csr) with SAN..."
sudo openssl req -new -key "$CERT_DIR/nginx.key" -out "$CERT_DIR/nginx.csr" -subj "/CN=localhost" -config <(cat <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = nginx
EOF
)

# 生成自簽名證書 (nginx.crt)，有效期 365 天
echo "Generating self-signed certificate (nginx.crt) with SAN..."
sudo openssl x509 -req -days 365 -in "$CERT_DIR/nginx.csr" -signkey "$CERT_DIR/nginx.key" -out "$CERT_DIR/nginx.crt" -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = nginx
EOF
) -extensions v3_req

# 設置證書權限
echo "Setting permissions for certificate files..."
sudo chmod 600 "$CERT_DIR/nginx.key" "$CERT_DIR/nginx.crt"

echo "Certificates generated successfully in $CERT_DIR!"