## Running Metaflow with Airflow and MinIO on Minikube

This guide provides instructions on how to set up Metaflow with Airflow and MinIO on Minikube

### Prerequisites

Ensure the following software is installed on your system:

- Minikube: Download and install from [Minikube's official website](https://minikube.sigs.k8s.io/docs/start/)
- kubectl: Download and install from [Kubernetes' official website](https://kubernetes.io/docs/tasks/tools/)
- Helm: Download and install from [Helm's official website](https://helm.sh/docs/intro/install/)
- ngrok: Download and install from [ngrok's official website](https://ngrok.com/downloads)
- An ngrok key created from the ngrok dashboard

### Step-by-step Instructions

1. **Start Minikube** by executing the following command:

   ```bash
   minikube start --cpus 6 --memory 10240
   ```

2. **Add the MinIO Helm repository** and update it:

   ```bash
   helm repo add minio https://charts.min.io/
   helm repo update
   ```

3. **Install MinIO using Helm**:

   ```bash
   helm install --set resources.requests.memory=512Mi --set replicas=1 --set persistence.enabled=false --set mode=standalone --set rootUser=rootuser,rootPassword=rootpass123 minio-s3 minio/minio
   ```

4. **Set up port forwarding for the MinIO service**:

   ```bash
   kubectl port-forward svc/minio-s3 9000 --namespace default
   ```

   The MinIO service will now be accessible at http://localhost:9000.

5. **Install metaflow and kubernetes**:

   ```bash
   pip install metaflow kubernetes
   ```

6. **Create a metaflow bucket** named `metaflow-test` in MinIO using the [create-bucket.py](./create-bucket.py) Python script. The `--access-key`/`--secret-key` correspond to the `rootUser` / `rootPassword` set in Step 4. 
   ```bash
   python create_bucket.py --access-key rootuser --secret-key rootpass123 --bucket-name metaflow-test
   ```

7. **Create an ngrok tunnel** to the port-forwarded MinIO service in a separate terminal window:

   ```
   ngrok http 9000
   ```

8. **Create a Kubernetes secret for MinIO.** This secret will be used by Metaflow Tasks and Metaflow UI running on Kubernetes to access data stored in MinIO:

   ```sh
   kubectl create secret generic minio-secret --from-literal=AWS_ACCESS_KEY_ID=rootuser --from-literal=AWS_SECRET_ACCESS_KEY=rootpass123
   ```

9. **Install Metaflow in the `default` namespace and enable ingress on minikube**:

   ```sh
   minikube addons enable ingress
   git clone git@github.com:outerbounds/metaflow-tools.git .mf-tools
   helm upgrade --install metaflow .mf-tools/k8s/helm/metaflow \
   	--timeout 15m0s \
   	--namespace default \
       --set metaflow-ui.uiBackend.metaflowDatastoreSysRootS3=s3://metaflow-test/metaflow \
       --set metaflow-ui.uiBackend.metaflowS3EndpointURL="<NGROK-TUNNEL-URL-COMES-HERE>" \
       --set "metaflow-ui.envFrom[0].secretRef.name=minio-secret" \
       --set metaflow-ui.ingress.className=nginx \
       --set metaflow-ui.ingress.enabled=true
   ```

10. **Create a metaflow configuration file** under `~/.metaflowconfig/config.json`. Ensure you name it `config_airflow_minio.json`:
    ```json
    {
        "METAFLOW_S3_ENDPOINT_URL": "<NGROK TUNNEL URL COMES HERE>",
        "METAFLOW_DEFAULT_DATASTORE": "s3",
        "METAFLOW_DATASTORE_SYSROOT_S3":"s3://metaflow-test/metaflow",
        "METAFLOW_DATATOOLS_S3ROOT": "s3://metaflow-test/data",
        "METAFLOW_DEFAULT_METADATA" : "service",
        "METAFLOW_KUBERNETES_SECRETS": "minio-secret",
        "METAFLOW_SERVICE_URL": "http://metaflow-metaflow-service.default.svc.cluster.local:8080",
        "METAFLOW_AIRFLOW_KUBERNETES_KUBECONFIG_CONTEXT": "minikube"
    }
    ```

11. **Start the Airflow installation** in a separate terminal window:

    ```sh
    pip install apache-airflow apache-airflow-providers-cncf-kubernetes
    mkdir ~/airflow && mkdir ~/airflow/dags && airflow standalone
    ```

12. **Create the Airflow DAG file** for the [helloflow.py](./helloflow.py):

    ```sh 
    export METAFLOW_PROFILE=airflow_minio
    python helloflow.py airflow create minio-test-dag.py
    cp minio-test-dag.py ~/airflow/dags/minio-test-dag.py
    ```

13. **Ensure DAGs get loaded** with `airflow dags reserialize`.

14. **Trigger the DAG** from the Airflow UI. The DAG named `HelloFlow` will appear on the Airflow UI.
