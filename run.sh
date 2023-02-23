#!/bin/bash

echo "Starting RayaneshBackend Project..."

sudo docker-compose build &&
  sudo docker-compose up --remove-orphans