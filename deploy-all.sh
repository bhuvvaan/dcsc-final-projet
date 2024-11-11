#!/bin/sh
docker build -t bhuv005/flask-rest-server:v1 ./rest/
docker push bhuv005/flask-rest-server:v1

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
kubectl apply -f rest/rest-server.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-ingress.yaml

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
#kubectl apply -f logs/logs-deployment.yaml

#kubectl apply -f worker/worker-deployment.yaml

kubectl apply -f minio/minio-external-service.yaml
