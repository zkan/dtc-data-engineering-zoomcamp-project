from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3_list import S3ListOperator
from airflow.utils import timezone


S3_BUCKET = "networkrail"


def _download_files(**context):
    ds = context["ds"]
    # year, month, day = ds.split("-")

    s3_hook = S3Hook(aws_conn_id="minio")

    events = []
    files = context["ti"].xcom_pull(task_ids="list_files", key="return_value")
    for each in files:
        file_name = s3_hook.download_file(
            key=each,
            bucket_name=S3_BUCKET,
        )

        with open(file_name) as f:
            events.append(f.read())

    output_file_name = f"{ds}-events.json"
    with open(output_file_name, "w") as f:
        f.writelines(f"{e}\n" for e in events)

    return output_file_name


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

    list_files = S3ListOperator(
        task_id="list_files",
        bucket=S3_BUCKET,
        prefix='year={{ macros.ds_format(logical_date | ds, "%Y-%m-%d", "%Y")  }}/month={{ macros.ds_format(logical_date | ds, "%Y-%m-%d", "%m") }}/day={{ macros.ds_format(logical_date | ds, "%Y-%m-%d", "%d") }}/',
        aws_conn_id="minio",
    )

    download_files = PythonOperator(
        task_id="download_files",
        python_callable=_download_files,
    )

    end = EmptyOperator(task_id="end")

    start >> list_files >> download_files >> end