# DataTalks.Club's Data Engineering Zoomcamp Project

## Getting Started

To start all services:

```sh
make setup
make up
```

To shutdown all services:

```sh
make down
```

To start the project:

```sh
python -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

We'll need to install the Apache Kafka C/C++ Library named [librdkafka](https://github.com/edenhill/librdkafka) too.

```sh
python get_network_rail_movements.py
```

### Services

* Airflow UI: http://localhost:8080
* MinIO Console: http://localhost:9001

## References

* [Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)