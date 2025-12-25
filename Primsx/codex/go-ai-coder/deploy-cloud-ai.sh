#!/bin/bash
#!/usr/bin/env bash
# ==============================================================================
# PRIMSX CODEX - DEPLOY-CLOUD-AI.SH
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Deploy Cloud AI Service for Go AI Coder
# This script sets up the complete cloud AI infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLOUD_PROVIDER=${CLOUD_PROVIDER:-"aws"}
REGION=${REGION:-"us-west-2"}
INSTANCE_TYPE=${INSTANCE_TYPE:-"g4dn.xlarge"}
MODEL_NAME=${MODEL_NAME:-"go-ai-model"}
API_KEY=${API_KEY:-$(openssl rand -hex 32)}

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required tools are installed
    command -v docker >/dev/null 2>&1 || error "Docker is required but not installed"
    command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed"
    command -v helm >/dev/null 2>&1 || error "Helm is required but not installed"
    
    # Check cloud provider CLI
    case $CLOUD_PROVIDER in
        "aws")
            command -v aws >/dev/null 2>&1 || error "AWS CLI is required but not installed"
            ;;
        "gcp")
            command -v gcloud >/dev/null 2>&1 || error "gcloud CLI is required but not installed"
            ;;
        "azure")
            command -v az >/dev/null 2>&1 || error "Azure CLI is required but not installed"
            ;;
    esac
    
    log "Prerequisites check passed"
}

# Create Docker image
build_docker_image() {
    log "Building Docker image for Go AI model..."
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << 'EOF'
FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy model and code
COPY go-ai-model/ /app/model/
COPY cloud-ai-service.py /app/
COPY go-ai-model-trainer.py /app/

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 goai && chown -R goai:goai /app
USER goai

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the service
CMD ["python3", "cloud-ai-service.py"]
EOF
    fi
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << 'EOF'
torch>=1.12.0
transformers>=4.21.0
datasets>=2.0.0
accelerate>=0.20.0
gin-gonic/gin>=1.9.0
redis>=4.3.0
requests>=2.28.0
numpy>=1.21.0
scikit-learn>=1.1.0
tqdm>=4.64.0
EOF
    fi
    
    # Build image
    docker build -t $MODEL_NAME:latest .
    
    log "Docker image built successfully"
}

# Deploy to cloud
deploy_to_cloud() {
    log "Deploying to $CLOUD_PROVIDER..."
    
    case $CLOUD_PROVIDER in
        "aws")
            deploy_to_aws
            ;;
        "gcp")
            deploy_to_gcp
            ;;
        "azure")
            deploy_to_azure
            ;;
        *)
            error "Unsupported cloud provider: $CLOUD_PROVIDER"
            ;;
    esac
}

# Deploy to AWS
deploy_to_aws() {
    log "Deploying to AWS..."
    
    # Create ECR repository
    aws ecr create-repository --repository-name $MODEL_NAME --region $REGION || true
    
    # Get ECR login token
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com
    
    # Tag and push image
    ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$MODEL_NAME:latest
    docker tag $MODEL_NAME:latest $ECR_URI
    docker push $ECR_URI
    
    # Create EKS cluster (if it doesn't exist)
    CLUSTER_NAME="go-ai-cluster"
    if ! aws eks describe-cluster --name $CLUSTER_NAME --region $REGION >/dev/null 2>&1; then
        log "Creating EKS cluster..."
        eksctl create cluster \
            --name $CLUSTER_NAME \
            --region $REGION \
            --nodegroup-name workers \
            --node-type $INSTANCE_TYPE \
            --nodes 2 \
            --nodes-min 1 \
            --nodes-max 4 \
            --managed
    fi
    
    # Update kubeconfig
    aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
    
    # Deploy to Kubernetes
    deploy_to_kubernetes $ECR_URI
}

# Deploy to GCP
deploy_to_gcp() {
    log "Deploying to GCP..."
    
    # Set project
    PROJECT_ID=$(gcloud config get-value project)
    
    # Create Artifact Registry repository
    gcloud artifacts repositories create $MODEL_NAME \
        --repository-format=docker \
        --location=$REGION || true
    
    # Configure Docker authentication
    gcloud auth configure-docker $REGION-docker.pkg.dev
    
    # Tag and push image
    GCR_URI=$REGION-docker.pkg.dev/$PROJECT_ID/$MODEL_NAME/$MODEL_NAME:latest
    docker tag $MODEL_NAME:latest $GCR_URI
    docker push $GCR_URI
    
    # Create GKE cluster (if it doesn't exist)
    CLUSTER_NAME="go-ai-cluster"
    if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION >/dev/null 2>&1; then
        log "Creating GKE cluster..."
        gcloud container clusters create $CLUSTER_NAME \
            --region=$REGION \
            --machine-type=$INSTANCE_TYPE \
            --num-nodes=2 \
            --enable-autoscaling \
            --min-nodes=1 \
            --max-nodes=4 \
            --enable-autorepair \
            --enable-autoupgrade
    fi
    
    # Get cluster credentials
    gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
    
    # Deploy to Kubernetes
    deploy_to_kubernetes $GCR_URI
}

# Deploy to Azure
deploy_to_azure() {
    log "Deploying to Azure..."
    
    # Set subscription
    SUBSCRIPTION_ID=$(az account show --query id --output tsv)
    
    # Create ACR
    az acr create --name $MODEL_NAME --resource-group $MODEL_NAME-rg --sku Basic || true
    
    # Login to ACR
    az acr login --name $MODEL_NAME
    
    # Tag and push image
    ACR_URI=$MODEL_NAME.azurecr.io/$MODEL_NAME:latest
    docker tag $MODEL_NAME:latest $ACR_URI
    docker push $ACR_URI
    
    # Create AKS cluster (if it doesn't exist)
    CLUSTER_NAME="go-ai-cluster"
    if ! az aks show --name $CLUSTER_NAME --resource-group $MODEL_NAME-rg >/dev/null 2>&1; then
        log "Creating AKS cluster..."
        az aks create \
            --name $CLUSTER_NAME \
            --resource-group $MODEL_NAME-rg \
            --node-count 2 \
            --node-vm-size $INSTANCE_TYPE \
            --enable-cluster-autoscaler \
            --min-count 1 \
            --max-count 4 \
            --enable-managed-identity
    fi
    
    # Get cluster credentials
    az aks get-credentials --name $CLUSTER_NAME --resource-group $MODEL_NAME-rg
    
    # Deploy to Kubernetes
    deploy_to_kubernetes $ACR_URI
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    local IMAGE_URI=$1
    
    log "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl create namespace go-ai || true
    
    # Create secrets
    kubectl create secret generic go-ai-secrets \
        --from-literal=api-key=$API_KEY \
        --namespace=go-ai || true
    
    # Create deployment
    cat > k8s-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-ai-model
  namespace: go-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: go-ai-model
  template:
    metadata:
      labels:
        app: go-ai-model
    spec:
      containers:
      - name: go-ai-model
        image: $IMAGE_URI
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
        env:
        - name: MODEL_PATH
          value: "/app/model"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: go-ai-secrets
              key: api-key
        - name: PORT
          value: "8080"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: go-ai-service
  namespace: go-ai
spec:
  selector:
    app: go-ai-model
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: go-ai-hpa
  namespace: go-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: go-ai-model
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF
    
    # Apply deployment
    kubectl apply -f k8s-deployment.yaml
    
    # Wait for deployment to be ready
    log "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/go-ai-model -n go-ai
    
    # Get service URL
    if [ "$CLOUD_PROVIDER" = "aws" ]; then
        SERVICE_URL=$(kubectl get service go-ai-service -n go-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    else
        SERVICE_URL=$(kubectl get service go-ai-service -n go-ai -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    fi
    
    log "Service deployed successfully!"
    log "Service URL: http://$SERVICE_URL"
    log "API Key: $API_KEY"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Install Prometheus and Grafana
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
    
    log "Monitoring setup completed"
    log "Grafana URL: http://localhost:3000 (admin/admin)"
}

# Test deployment
test_deployment() {
    log "Testing deployment..."
    
    # Get service URL
    if [ "$CLOUD_PROVIDER" = "aws" ]; then
        SERVICE_URL=$(kubectl get service go-ai-service -n go-ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    else
        SERVICE_URL=$(kubectl get service go-ai-service -n go-ai -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    fi
    
    # Wait for service to be ready
    log "Waiting for service to be ready..."
    sleep 60
    
    # Test health endpoint
    if curl -f "http://$SERVICE_URL/health"; then
        log "Health check passed"
    else
        warn "Health check failed"
    fi
    
    # Test API endpoint
    if curl -f -H "Authorization: Bearer $API_KEY" "http://$SERVICE_URL/api/v1/models"; then
        log "API test passed"
    else
        warn "API test failed"
    fi
}

# Main deployment function
main() {
    log "Starting Go AI Cloud deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Build Docker image
    build_docker_image
    
    # Deploy to cloud
    deploy_to_cloud
    
    # Setup monitoring
    setup_monitoring
    
    # Test deployment
    test_deployment
    
    log "Deployment completed successfully!"
    log "Your Go AI model is now running in the cloud!"
    
    # Print summary
    echo ""
    echo "=========================================="
    echo "🚀 Go AI Cloud Deployment Summary"
    echo "=========================================="
    echo "Cloud Provider: $CLOUD_PROVIDER"
    echo "Region: $REGION"
    echo "Model Name: $MODEL_NAME"
    echo "API Key: $API_KEY"
    echo "Service URL: http://$SERVICE_URL"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Update your Go AI Coder client to use the cloud API"
    echo "2. Test the integration with your local client"
    echo "3. Monitor performance and usage"
    echo "4. Scale as needed"
    echo ""
}

# Run main function
main "$@"
