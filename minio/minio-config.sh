#!/bin/bash

/usr/bin/mc alias set myminio http://${KEYCLOAK_HOST_IP_ADDRESS}:9000 ${S3_ROOT_USER} ${S3_ROOT_PASSWORD};
/usr/bin/mc mb myminio/werkstatthub;
exit 0;
