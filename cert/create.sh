openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout cert/ssl/nginx.key \
    -out cert/ssl/nginx.crt \
    -subj "/C=CZ/ST=Czech/L=Prague/O=Dev/CN=localhost"