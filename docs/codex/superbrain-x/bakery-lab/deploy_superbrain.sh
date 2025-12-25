#!/bin/bash
PROJECT_ID="mythicnode"  # REPLACE WITH YOUR ACTUAL PROJECT ID

cat > Dockerfile.superbrain <<DOCKER
FROM python:3.11-slim
WORKDIR /app
COPY scripts/superbrain.py .
RUN pip install sympy numpy requests
CMD ["python3", "superbrain.py"]
DOCKER

docker build -f Dockerfile.superbrain -t gcr.io/${PROJECT_ID}/superbrain:latest .
docker push gcr.io/${PROJECT_ID}/superbrain:latest
gcloud run deploy superbrain \
  --image gcr.io/${PROJECT_ID}/superbrain:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
