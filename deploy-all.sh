#!/bin/sh

# Build and push the Docker image (commented out if already pushed)
# docker build -t bhuv005/flask-rest-server:v1 ./rest/
# docker push bhuv005/flask-rest-server:v1

# Apply Redis deployment and service
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

# Apply the Ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml

# Wait for the Ingress controller pods to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Apply the Flask REST server deployment and service
kubectl apply -f rest/rest-server.yaml
kubectl apply -f rest/rest-service.yaml

# Apply the REST ingress
kubectl apply -f rest/rest-ingress.yaml

# Add the Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install MinIO with Helm
helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio

# Wait for the MinIO pods to be ready
kubectl wait --namespace minio-ns \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=minio \
  --timeout=90s

# Apply the external MinIO service
kubectl apply -f minio/minio-external-service.yaml

# Apply the Demucs worker deployment
kubectl apply -f worker/demucs-worker-deployment.yaml

# Wait for the Demucs worker deployment to be ready
kubectl wait --for=condition=available --timeout=60s deployment/demucs-worker

# Optional: Port-forward Redis and MinIO services (commented if not required)
# kubectl port-forward service/redis-master 6379:6379 &
# kubectl port-forward -n minio-ns service/minio-proj 9000:9000 &
# kubectl port-forward -n minio-ns service/minio-proj 9001:9001 &
