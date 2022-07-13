from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils import timezone


default_args = {
    "owner": "Kan Ouivirach",
}
with DAG(
    "load_networkrail_movement_data_to_bigquery",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=timezone.datetime(2022, 7, 13),
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="end")

    start >> end