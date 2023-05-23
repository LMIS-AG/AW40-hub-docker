#!/bin/bash

/usr/bin/mc alias set myminio http://${HOST_IP_ADDRESS}:9000 ${S3_ROOT_USER} ${S3_ROOT_PASSWORD};
/usr/bin/mc mb myminio/werkstatthub;
exit 0;
