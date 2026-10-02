#!/bin/bash
set -e

echo "Waiting for Ollama to be ready..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
  echo "Ollama not ready, waiting..."
  sleep 2
done

echo "Ollama is ready!"

# Pull Laya model
echo "Pulling Laya decision model..."
ollama pull laya

echo "Starting the application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1