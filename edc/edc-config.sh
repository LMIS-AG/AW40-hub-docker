#!/bin/bash

# Replace the placeholder in the properties file with the value of the environment variable
sed -i "s/\${HOST_IP_ADDRESS}/$HOST_IP_ADDRESS/g" config.properties
