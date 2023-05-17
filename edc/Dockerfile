FROM openjdk:17-jdk-slim

# Copy the files into the container
COPY provider.jar provider.jar
COPY config.properties config.properties
COPY entrypoint.sh entrypoint.sh

RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

