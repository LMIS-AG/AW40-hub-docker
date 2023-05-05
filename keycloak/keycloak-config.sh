#!/bin/bash

# Authenticate in order to use the Keycloak Admin CLI
/opt/keycloak/bin/kcadm.sh config credentials \
    --server http://${IP_ADDRESS}:8080 \
    --realm master \
    --user kc-admin \
    --password zC5dCYJX0saA7db7N7ctzdVs6OlBzEA0zWPNGelfBFn5mZI1 # this should be an env, not working yet

# Create the werkstatt-hub-realm
/opt/keycloak/bin/kcadm.sh create realms -f /opt/werkstatthub-realm.json

# Create a first user
/opt/keycloak/bin/kcadm.sh create users \
    -r werkstatt-hub \
    -s username=werkstatthub-admin \
    -s enabled=true \
    -s attributes.policy=consoleAdmin \
    -s credentials='[{"type":"password","value":"rcTvQNX55nD8Fpmj5HXUMSyxd6LgBbeS"}]' # this should be an env, not working yet

# Get the ID of the 'minio' client in the 'werkstatt-hub' realm
CLIENT_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r werkstatt-hub -q clientId=minio -F id | grep -oP '\w{8}-(\w{4}-){3}\w{12}' | cut -f1)

echo "The client ID of 'minio' in the 'werkstatt-hub' realm is: $CLIENT_ID"

# Update the client secret for the 'minio' client in the 'werkstatt-hub' realm
/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID \
    -r werkstatt-hub \
    -s secret=${MINIO_CLIENT_SECRET}
