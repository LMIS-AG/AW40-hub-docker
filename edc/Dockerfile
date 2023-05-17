FROM openjdk:17-jdk-slim

# Copy the files into the container
COPY provider.jar provider.jar
COPY config.properties config.properties
COPY edc-config.sh edc-config.sh

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "-c", "chmod +x edc-config.sh && ./edc-config.sh && java -Dedc.fs.config=config.properties -Daws.accessKeyId=${S3_ROOT_USER} -Daws.secretAccessKey=${S3_ROOT_PASSWORD} -jar provider.jar"]

