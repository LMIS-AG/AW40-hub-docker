#!/bin/bash

# Authenticate in order to use the Keycloak Admin CLI
/opt/keycloak/bin/kcadm.sh config credentials \
    --server http://${IP_ADDRESS}:8080 \
    --realm master \
    --user ${KEYCLOAK_ADMIN} \
    --password ${KEYCLOAK_ADMIN_PASSWORD}

# Create the werkstatt-hub-realm
/opt/keycloak/bin/kcadm.sh create realms -f /opt/werkstatthub-realm.json

# Create first user
/opt/keycloak/bin/kcadm.sh create users \
    -r werkstatt-hub \
    -s username=${KC_ADMIN_WERKSTATTHUB} \
    -s enabled=true \
    -s attributes.policy=consoleAdmin \
    -s credentials='[{"type":"password","value":"'${KC_ADMIN_WERKSTATTHUB_PASSWORD}'"}]'

# Get the ID of the 'minio' client in the 'werkstatt-hub' realm
CLIENT_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r werkstatt-hub -q clientId=minio -F id | grep -oP '\w{8}-(\w{4}-){3}\w{12}' | cut -f1)

echo "The client ID of 'minio' in the 'werkstatt-hub' realm is: $CLIENT_ID"

# Update the client secret for the 'minio' client in the 'werkstatt-hub' realm
/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID \
    -r werkstatt-hub \
    -s secret=${MINIO_CLIENT_SECRET}
