ARG KC_VER
FROM quay.io/keycloak/keycloak:$KC_VER

# Set the working directory
WORKDIR /opt/keycloak

# Build Keycloak
RUN /opt/keycloak/bin/kc.sh build

# Copy the script to the container
COPY keycloak-config.sh /opt/
# Copy the realm configuration file
COPY werkstatthub-realm.json /opt/

# Make the script executable
USER root
RUN chmod +x /opt/keycloak-config.sh

# Run the script as the entrypoint
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
