# Stage 1: Build stage
FROM gradle:8.0.0 AS builder

# Create a directory for the project
WORKDIR /app

# Copy the Gradle wrapper files
COPY gradlew .
COPY gradlew.bat .
COPY gradle/ gradle/

# Copy the build files
COPY build.gradle.kts settings.gradle.kts gradle.properties ./

# Perform the build
RUN ./gradlew clean build

# Stage 2: Production stage
FROM openjdk:17-jdk-slim

# Create a directory for the application
WORKDIR /app

# Copy the built JAR file from the builder stage
COPY --from=builder /app/build/libs/connector.jar .

# Copy any other necessary files
COPY config.properties .
COPY entrypoint.sh .

# Set permissions for the entrypoint script
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]

