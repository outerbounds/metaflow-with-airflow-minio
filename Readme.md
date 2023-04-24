## Base Setup 

To set up MinIO on Minikube and use it with Boto3, follow these steps:

1. Install prerequisites

First, make sure you have the following software installed on your system:

- Minikube: Download and install Minikube from https://minikube.sigs.k8s.io/docs/start/
- kubectl: Download and install kubectl from https://kubernetes.io/docs/tasks/tools/
- Helm: Download and install Helm from https://helm.sh/docs/intro/install/
- ngrok: Download and install ngrok from https://ngrok.com/downloads
- An ngrok key created from the ngrok dashboard. 

2. Start Minikube

Start Minikube by running:

```bash
minikube start --cpus 6 --memory 10240
```

3. Add MinIO Helm repository

Add the MinIO Helm repository by running:

```bash
helm repo add minio https://charts.min.io/
helm repo update
```

4. Install MinIO

Install MinIO using Helm:

```bash
helm install --set resources.requests.memory=512Mi --set replicas=1 --set persistence.enabled=false --set mode=standalone --set rootUser=rootuser,rootPassword=rootpass123 minio-s3 minio/minio
```

5. Set up port forwarding for the MinIO service:

```bash
kubectl port-forward svc/minio-s3 9000 --namespace default
```

Now, the MinIO service will be accessible at http://localhost:9000.

6. Install metaflow, and kubernetes

```bash
pip install metaflow kubernetes
```

7. Use the [create-bucket.py](./create-bucket.py) python script to create metaflow's bucket named `metaflow-test` in MiniO. 

9. Create a Ngrok tunnel to the Port-forwarded minio service in a separate terminal window
```
ngrok http 9000
```

8. Create a Kubernetes secret in MiniO
```sh
kubectl create secret generic aws-secret --from-literal=AWS_ACCESS_KEY_ID=rootuser --from-literal=AWS_SECRET_ACCESS_KEY=rootpass123
```

9. Install Metaflow in the `default` namespace
```sh
git clone git@github.com:outerbounds/metaflow-tools.git .mf-tools
helm upgrade --install metaflow .mf-tools/k8s/helm/metaflow \
	--timeout 15m0s \
	--namespace default \
    --set metaflow-ui.METAFLOW_DATASTORE_SYSROOT_S3=s3://metaflow-test/metaflow \
    --set metaflow-ui.METAFLOW_S3_ENDPOINT_URL="<NGROK-TUNNEL-URL-COMES-HERE>" \
    --set "metaflow-ui.envFrom[0].secretRef.name=aws-secret" \
    --set metaflow-ui.ingress.className=nginx \
    --set metaflow-ui.ingress.enabled=true
```

10. Create the following metaflow configuration file under `~/.metaflowconfig/config.json`. **Ensure you name it `config_airflow_minio.json`**
```json
{
    "METAFLOW_S3_ENDPOINT_URL": "<NGROK TUNNEL URL COMES HERE>",
    "METAFLOW_DEFAULT_DATASTORE": "s3",
    "METAFLOW_DATASTORE_SYSROOT_S3":"s3://metaflow-test/metaflow",
    "METAFLOW_DATATOOLS_S3ROOT": "s3://metaflow-test/data",
    "METAFLOW_DEFAULT_METADATA" : "service",
    "METAFLOW_KUBERNETES_SECRETS": "aws-secret",
    "METAFLOW_SERVICE_INTERNAL_URL": "http://metaflow-metaflow-service.default.svc.cluster.local:8080",
    "METAFLOW_AIRFLOW_KUBERNETES_KUBECONFIG_CONTEXT": "minikube"
}
```
11. In a separate terminal window start the Airflow installation: 

```sh
pip install apache-airflow apache-airflow-providers-cncf-kubernetes
mkdir ~/airflow && mkdir ~/airflow/dags && airflow standalone
```

12. Create the Airflow Dag file for the [helloflow.py](./helloflow.py): 
```sh 
export METAFLOW_PROFILE=airflow_minio
python helloflow.py airflow create minio-test-dag.py
cp minio-test-dag.py ~/airflow/dags/minio-test-dag.py
```

13. Ensure dags get loaded with `airflow dags reserialize`

14. Trigger Dag from Airflow UI. The dag named `HelloFlow` will appear on the Airflow UI.

