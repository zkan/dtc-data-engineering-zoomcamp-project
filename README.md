# DataTalks.Club's Data Engineering Zoomcamp Project

**Table of Contents**

* [Project Overview](#project-overview)
* [Dataset](#dataset)
* [Technologies](#technologies)
* [Files and What They Do](#files-and-what-they-do)
* [Instruction on Running the Project](#instruction-on-running-the-project)

## Project Overview

![Project Overview](./img/dtc-data-engineering-zoomcamp-project-overview.png)

This project builds an automated end-to-end data pipeline that aims to get the
livestream of train movement data and analyze the train operating company's
performance.  The source of streaming data comes from the [UK's Network Rail
company](https://datafeeds.networkrail.co.uk) provided through an ActiveMQ
interface. A train movement message is sent whenever a train arrives, passes or
departs a location. It records the time at which the event happens.

We first extract the live stream of train movement messages from the ActiveMQ
endpoint and stream the messages into Kafka. We then consume and put them into
a data lake (MinIO). After that we schedule a data pipeline (Airflow) to run
daily to load the data to a data warehouse (Google BigQuery). Later on, we
transform the data in the warehouse using dbt. Finally, once the data is
cleaned and transformed, we can monitor and analyze the data on a dashboard
(Google Data Studio).

## Dataset

[Network Rail](https://datafeeds.networkrail.co.uk)

![Network Rail feed](./img/networkrail-feed.png)

## Technologies

* [Apache Airflow](https://airflow.apache.org/) for orchestrating workflow
* [Apache Kafka](https://kafka.apache.org/) for stream processing
* [MinIO](https://min.io/) for data lake storage
* [dbt](https://www.getdbt.com/) for data transformation
* [Google BigQuery](https://cloud.google.com/bigquery) for data warehousing and analysis
* [Google Data Studio](https://datastudio.google.com/overview) for dashboard
* [Terraform](https://www.terraform.io/) for provisioning BigQuery dataset
* [Docker](https://www.docker.com/) for running services on local machine

## Files and What They Do

| Name | Description |
| - | - |
| `mnt/dags/load_networkrail_movement_data_to_bigquery.py` | An Airflow DAG file that runs the ETL data pipeline on Network Rail train movement data and load them to BigQuery |
| `networkrail/` | A dbt project used to clean and transform the train movement data |
| `playground/` | A folder that contains code for testing ideas |
| `terraform/` | A Terraform project used to provision the Google BigQuery dataset |
| `.env.example` | A environment example file that contains the environment variables we use in this project |
| `docker-compose.yaml` | A Docker Compose file that runs the Confluent platform (Kafka and friends), an Airflow instance, and MinIO |
| `Makefile` | A Makefile file for running commands |
| `get_networkrail_movements.py` | A Python script that get the live stream data through the Network Rail's ActiveMQ interface |
| `consume_networkrail_movements_to_data_lake.py` | A Python script that consumes the messages from Kafka and puts them into a data lake storage |
| `README.md` | README file that provides the discussion on this project |
| `requirements.txt` | A file that contains Python package dependencies used in this project |
| `secrets.json.example` | A secret file that contains the Network Rail's username and password |

## Instruction on Running the Project

### Services

* Confluent Control Center: http://localhost:9021
* Airflow UI: http://localhost:8080
* MinIO Console: http://localhost:9001

### Starting the Project

Before we can get the NetworkRail data feed, we'll need to register a new
account on [the NetworkRail website](https://datafeeds.networkrail.co.uk/)
first.

To start all services:

```sh
make setup
make up
```

To set up a virtual environment and install package dependencies:

```sh
python -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

Note that we'll need to install the Apache Kafka C/C++ Library named
[librdkafka](https://github.com/edenhill/librdkafka) too.

To get the NetworkRail data and produce messages to the Kafka:

```sh
python get_networkrail_movements.py
```

Before we can consume the messages from Kafka, we'll need to set up a service
account first, so we can put the data into a data lake.

```sh
cp env.example .env
```

We then save the AWS access key ID and AWS secret access key from MinIO to the
file `.env`.

To consume the messages from Kafka:

```sh
export $(cat .env)
python consume_networkrail_movements_to_data_lake.py
```

After that we can go to the Airflow UI to run the data pipeline and wait for
the data to show up on the dashboard.

To shutdown all services:

```sh
make down
```

### Data Pipeline on Airflow

The screenshots below show the data pipeline on Airflow.

![Data Pipeline on Airflow 1](./img/airflow-data-pipeline-01.png)

![Data Pipeline on Airflow 2](./img/airflow-data-pipeline-02.png)

### Data Models on Google BigQuery

The screenshot below shows the data models on Google BigQuery.

![Data Models on Google BigQuery](./img/data-models-on-bigquery.png)

### TOC Performance Dashboard

The screenshot below shows the dashboard to monitor the train operating
company's performance.

![TOC Performance Dashboard](./img/toc-performance-dashboard.png)

### Steps to Set Up a Service Account on MinIO

The screenshots below show how to set up a service account on MinIO. Airflow
needs it in order to get data from the MinIO storage.

![Set up a Service Account on MinIO 1](./img/minio-set-up-service-account-01.png)

![Set up a Service Account on MinIO 2](./img/minio-set-up-service-account-02.png)

![Set up a Service Account on MinIO 3](./img/minio-set-up-service-account-03.png)

![Set up a Service Account on MinIO 4](./img/minio-set-up-service-account-04.png)

### Airflow S3 Connection to MinIO

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

### Steps to Set Up a Service Account on Google Cloud Platform (GCP)

The screenshots belwo show how to set up a service account on GCP. This service
account is required for Airflow to load data to the BigQuery as well as dbt to
transform data in the BigQuery.

![Set up a Service Account on GCP 1](./img/gcp-set-up-service-account-01.png)

![Set up a Service Account on GCP 2](./img/gcp-set-up-service-account-02.png)

![Set up a Service Account on GCP 3](./img/gcp-set-up-service-account-03.png)

![Set up a Service Account on GCP 4](./img/gcp-set-up-service-account-04.png)
