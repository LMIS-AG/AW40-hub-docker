#!/bin/sh

# Make a copy of the mounted file
cp /config/config.properties config.properties

# Replace the placeholder in the copied properties file with the value of the environment variable
sed -i "s/\${HOST_IP_ADDRESS}/$HOST_IP_ADDRESS/g" config.properties
java -jar connector.jar
