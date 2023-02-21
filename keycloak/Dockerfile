ARG KC_VER 
FROM quay.io/keycloak/keycloak:$KC_VER as builder

ENV KC_DB=postgres
WORKDIR /opt/keycloak
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:$KC_VER
WORKDIR /opt/keycloak
COPY --from=builder /opt/keycloak/ opt/keycloak/
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
