import logging
from datetime import datetime
from pytz import timezone as tz

from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3_list import S3ListOperator
from airflow.utils import timezone

import google
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


TIMEZONE_LONDON: tz = tz("Europe/London")
S3_CONN = "minio"
S3_BUCKET = "networkrail"
VARIABLE_BIGQUERY_CREDENTIAL_SECRET = "bigquery_credential_secret"
VARIABLE_BIGQUERY_PROJECT_ID = "bigquery_project_id"
BIGQUERY_TABLE_ID = "networkrail.movements"


def _download_files(**context) -> str:
    ds = context["ds"]
    files = context["ti"].xcom_pull(task_ids="list_files", key="return_value")

    s3_hook = S3Hook(aws_conn_id=S3_CONN)

    events = []
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


def remove_old_data(bq_client: bigquery.Client, table: str, ds: str) -> None:
    try:
        query = bq_client.query(
            f"""
            DELETE FROM `{table}` WHERE DATE(actual_timestamp) = "{ds}"
            """
        )
        query.result()
    except google.api_core.exceptions.NotFound:
        logging.info("No table found")


def _load_data_to_bigquery(**context) -> None:
    ds = context["ds"]
    file_name = context["ti"].xcom_pull(task_ids="download_files", key="return_value")
    df = pd.read_json(file_name, dtype=str, lines=True)

    df["actual_timestamp"] = df["actual_timestamp"].astype(int) / 1000
    df["actual_timestamp"] = df["actual_timestamp"] \
        .map(datetime.utcfromtimestamp) \
        .map(TIMEZONE_LONDON.fromutc)

    bigquery_schema = [
        bigquery.SchemaField("event_type", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("gbtt_timestamp", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("original_loc_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_timestamp", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("timetable_variation", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("original_loc_timestamp", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("current_train_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("delay_monitoring_point", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("next_report_run_time", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("reporting_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("actual_timestamp", bigquery.enums.SqlTypeNames.TIMESTAMP),
        bigquery.SchemaField("correction_ind", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("event_source", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_file_address", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("platform", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("division_code", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_terminated", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("offroute_ind", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("variation_status", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("train_service_code", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("toc_id", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("loc_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("auto_expected", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("direction_ind", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("route", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("planned_event_type", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("next_report_stanox", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("line_ind", bigquery.enums.SqlTypeNames.STRING),
    ]
    job_config = bigquery.LoadJobConfig(schema=bigquery_schema)

    bq_credential_secret = Variable.get(VARIABLE_BIGQUERY_CREDENTIAL_SECRET, deserialize_json=True)
    bq_client = bigquery.Client(
        credentials=service_account.Credentials.from_service_account_info(bq_credential_secret),
        project=Variable.get(VARIABLE_BIGQUERY_PROJECT_ID),
    )

    remove_old_data(bq_client, BIGQUERY_TABLE_ID, ds)

    job = bq_client.load_table_from_dataframe(df, BIGQUERY_TABLE_ID, job_config=job_config)
    job.result()


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

    load_data_to_bigquery = PythonOperator(
        task_id="load_data_to_bigquery",
        python_callable=_load_data_to_bigquery,
    )

    end = EmptyOperator(task_id="end")

    start >> list_files >> download_files >> load_data_to_bigquery >> end
