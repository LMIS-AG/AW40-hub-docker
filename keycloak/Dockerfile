ARG KC_VER
FROM quay.io/keycloak/keycloak:$KC_VER

# Set the working directory
WORKDIR /opt/keycloak

# Build Keycloak
RUN /opt/keycloak/bin/kc.sh build --health-enabled=true

# Run the script as the entrypoint
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
