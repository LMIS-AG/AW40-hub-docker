#!/bin/sh

# Make a copy of the mounted file
cp /configs/$EDC_FS_CONFIG $EDC_FS_CONFIG

# Replace the placeholder in the copied properties file with the value of the environment variable
sed -i "s/\${HOST_IP_ADDRESS}/$HOST_IP_ADDRESS/g" $EDC_FS_CONFIG
java -jar connector.jar
