
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "cryptoflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="cryptoflow_ml_anomaly_detection",
    default_args=default_args,
    description="Run CryptoFlow ML anomaly detection",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["cryptoflow", "machine-learning"],
) as dag:

    detect_anomalies = BashOperator(
        task_id="detect_anomalies",
        bash_command=(
            "cd /opt/airflow/project && "
            "python ml/anomaly_detection.py"
        ),
    )
