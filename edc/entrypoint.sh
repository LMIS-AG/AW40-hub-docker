#!/bin/sh

# Make a copy of the mounted file
cp /config/config.properties config.properties

# Replace the placeholder in the copied properties file with the value of the environment variable
sed -i "s/\${HOST_IP_ADDRESS}/$HOST_IP_ADDRESS/g" config.properties
java -Daws.accessKeyId=${S3_ROOT_USER} -Daws.secretAccessKey=${S3_ROOT_PASSWORD} -jar connector.jar
