from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "mariana",
    "retry_delay": timedelta(minutes=5),
}

spark_dag = DAG(
    dag_id="final_project",
    default_args=default_args,
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60),
    description="Final Project",
    start_date=days_ago(1),
)

Extract = SparkSubmitOperator(
    application="/spark-scripts/project.py",
    conn_id="spark_main",
    task_id="spark_submit_task",
    dag=spark_dag,
    packages = 'org.postgresql:postgresql:42.2.18'
)

Extract
