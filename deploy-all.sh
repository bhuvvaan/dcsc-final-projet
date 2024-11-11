#!/bin/sh
#docker build -t bhuv005/flask-rest-server:v1 ./rest/
#docker push bhuv005/flask-rest-server:v1

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

#kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
#kubectl delete --force namespace/ingress-nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml

kubectl apply -f rest/rest-server.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-ingress.yaml

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
#kubectl apply -f logs/logs-deployment.yaml


kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f worker/demucs-worker-deployment.yaml

#kubectl apply -f redis-reader/redis-reader-deployment.yaml 

#kubectl port-forward service/redis-master 6379:6379 &

# # If you're using minio from the kubernetes tutorial this will forward those
# kubectl port-forward -n minio-ns service/minio-proj 9000:9000 &
# kubectl port-forward -n minio-ns service/minio-proj 9001:9001 &
