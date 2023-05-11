FROM openjdk:17-jdk-slim

# Copy the files into the container
COPY provider.jar provider.jar
COPY config.properties config.properties
COPY edc-config.sh edc-config.sh

# Make the script executable
RUN chmod +x edc-config.sh

# Execute the script to update the properties file and start the conector
ENTRYPOINT ["/bin/bash", "-c", "./edc-config.sh && java -Dedc.fs.config=config.properties -Daws.accessKeyId=${S3_ROOT_USER} -Daws.secretAccessKey=${S3_ROOT_PASSWORD} -jar provider.jar"]
