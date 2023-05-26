#!/bin/bash

# Authenticate in order to use the Keycloak Admin CLI
/opt/keycloak/bin/kcadm.sh config credentials \
    --server http://keycloak:8080 \
    --realm master \
    --user ${KEYCLOAK_ADMIN} \
    --password ${KEYCLOAK_ADMIN_PASSWORD}

# Create MinIO administrator
/opt/keycloak/bin/kcadm.sh create users \
    -r werkstatt-hub \
    -s username=${MINIO_ADMIN_WERKSTATTHUB} \
    -s enabled=true \
    -s attributes.policy=consoleAdmin \
    -s credentials='[{"type":"password","value":"'${MINIO_ADMIN_WERKSTATTHUB_PASSWORD}'"}]'

# Create MinIO user with r/w access
/opt/keycloak/bin/kcadm.sh create users \
    -r werkstatt-hub \
    -s username=${MINIO_USER_WERKSTATTHUB} \
    -s enabled=true \
    -s attributes.policy=readwrite \
    -s credentials='[{"type":"password","value":"'${MINIO_USER_WERKSTATTHUB_PASSWORD}'"}]'

# Get the ID of the 'minio' client in the 'werkstatt-hub' realm
CLIENT_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r werkstatt-hub -q clientId=minio -F id | grep -oP '\w{8}-(\w{4}-){3}\w{12}' | cut -f1)

echo "The client ID of 'minio' in the 'werkstatt-hub' realm is: $CLIENT_ID"

# Update the client secret for the 'minio' client in the 'werkstatt-hub' realm
/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID \
    -r werkstatt-hub \
    -s secret=${MINIO_CLIENT_SECRET}
