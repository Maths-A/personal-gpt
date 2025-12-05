#!/bin/bash

cd ..

# Build and run the Docker Compose services
docker compose up -d --build

# Check if the services are running
if [ $? -eq 0 ]; then
  echo "Docker Compose services are up and running!"
  echo "You can access the web service at http://localhost:8080"
else
  echo "Failed to start Docker Compose services."
fi