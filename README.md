# DataTalks.Club's Data Engineering Zoomcamp Project

## Getting Started

### Services

* Confluent Control Center: http://localhost:9021
* Airflow UI: http://localhost:8080
* MinIO Console: http://localhost:9001

To start all services:

```sh
make setup
make up
```

To shutdown all services:

```sh
make down
```

Before we get the networkrail data feed, we'll need to register on [the NetworkRail website](https://datafeeds.networkrail.co.uk/) first.

To start the project:

```sh
python -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

We'll need to install the Apache Kafka C/C++ Library named [librdkafka](https://github.com/edenhill/librdkafka) too.

To get the NetworkRail data and produce messages to Kafka:

```sh
python get_networkrail_movements.py
```

To consume the messages from Kafka:

```sh
cp env.example .env
```

Save your AWS access key ID and AWS secret access key from MinIO to the file `.env`.

```sh
export $(cat .env)
python consume_networkrail_movements_to_data_lake.py
```

## Airflow S3 Connection to MinIO

- Connection Name: `minio` or any name you like
- Connection Type: S3
- Login: `<replace_here_with_your_minio_access_key>`
- Password: `<replace_here_with_your_minio_secret_key>`
- Extra: a JSON object with the following properties:
  ```json
  {
    "host": "http://minio:9000"
  }
  ```

**Note:** If we were using AWS S3, we don't need to specify the host in the extra.

## References

* [Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)