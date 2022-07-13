import json
import logging
import os
from datetime import datetime
from pytz import timezone

import boto3
from botocore.client import Config
from confluent_kafka import Consumer


TIMEZONE_LONDON: timezone = timezone("Europe/London")

topics = ["public.networkrail.movement",]
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "mygroup",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(conf)
consumer.subscribe(topics)

S3_BUCKET = "networkrail"
s3 = boto3.resource(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    config=Config(signature_version="s3v4"),
    region_name=os.environ.get("AWS_REGION", "ap-southeast-1"),
)

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    message = json.loads(msg.value().decode('utf-8'))

    header = message["header"]
    msg_type = header["msg_type"]
    body = message["body"]

    if msg_type == "0003":
        timestamp = int(body["actual_timestamp"]) / 1000
        utc_datetime = datetime.utcfromtimestamp(timestamp)
        uk_datetime = TIMEZONE_LONDON.fromutc(utc_datetime)
        uk_date = uk_datetime.date()
        uk_year = uk_date.year
        uk_month = uk_date.month
        uk_day = uk_date.day
        toc_id = body["toc_id"]

        uk_datetime_str = uk_datetime.strftime("%Y%m%d-%H%M%S")
        filename = f"{uk_datetime_str}-{toc_id}.json"
        with open(f"tmp/{filename}", "w") as f:
            f.write(json.dumps(body))

        key = f"year={uk_year}/month={uk_month:02}/day={uk_day:02}/{filename}"
        s3.Bucket(S3_BUCKET).upload_file(
            f"tmp/{filename}",
            key,
        )
        print(header["msg_type"], body["event_type"], body["toc_id"], body["variation_status"], uk_datetime)