#!/bin/bash

# Authenticate in order to use the Keycloak Admin CLI
/opt/keycloak/bin/kcadm.sh config credentials \
    --server http://keycloak:8080 \
    --realm master \
    --user ${KEYCLOAK_ADMIN} \
    --password ${KEYCLOAK_ADMIN_PASSWORD}

/opt/keycloak/bin/kcadm.sh create roles \
    -r werkstatt-hub \
    -s name=${WERKSTATT_ANALYST_ROLE}

/opt/keycloak/bin/kcadm.sh create roles \
    -r werkstatt-hub \
    -s name=${WERKSTATT_MECHANIC_ROLE}

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
    -s username=${WERKSTATT_ANALYST} \
    -s enabled=true \
    -s attributes.policy=readwrite \
    -s credentials='[{"type":"password","value":"'${WERKSTATT_ANALYST_PASSWORD}'"}]'

# Assign Analyst role
/opt/keycloak/bin/kcadm.sh add-roles \
    -r werkstatt-hub \
    --uusername ${WERKSTATT_ANALYST} \
    --rolename ${WERKSTATT_ANALYST_ROLE}

# Create MinIO user with r/w access
/opt/keycloak/bin/kcadm.sh create users \
    -r werkstatt-hub \
    -s username=${WERKSTATT_MECHANIC} \
    -s enabled=true \
    -s attributes.policy=readwrite \
    -s credentials='[{"type":"password","value":"'${WERKSTATT_MECHANIC_PASSWORD}'"}]'

# Assign Mechanic role
/opt/keycloak/bin/kcadm.sh add-roles \
    -r werkstatt-hub \
    --uusername ${WERKSTATT_MECHANIC} \
    --rolename ${WERKSTATT_MECHANIC_ROLE}

# Get the ID of the 'minio' client in the 'werkstatt-hub' realm
CLIENT_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r werkstatt-hub -q clientId=minio -F id | grep -oP '\w{8}-(\w{4}-){3}\w{12}' | cut -f1)

echo "The client ID of 'minio' in the 'werkstatt-hub' realm is: $CLIENT_ID"

# Update the client secret for the 'minio' client in the 'werkstatt-hub' realm
/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID \
    -r werkstatt-hub \
    -s secret=${MINIO_CLIENT_SECRET}

# Get the ID of the 'aw40hub-frontend' client in the 'werkstatt-hub' realm
CLIENT_ID=$(/opt/keycloak/bin/kcadm.sh get clients -r werkstatt-hub -q clientId=aw40hub-frontend -F id | grep -oP '\w{8}-(\w{4}-){3}\w{12}' | cut -f1)

echo "The client ID of 'aw40hub-frontend' in the 'werkstatt-hub' realm is: $CLIENT_ID"

# Update the client secret for the 'aw40hub-frontend' client in the 'werkstatt-hub' realm
/opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID \
    -r werkstatt-hub \
    -s secret=${HUB_UI_CLIENT_SECRET}
