import json
import socket
from datetime import datetime
from pytz import timezone
from time import sleep

import stomp
from confluent_kafka import Producer


TIMEZONE_LONDON: timezone = timezone("Europe/London")

topic = "public.networkrail.movement"
conf = {
    "bootstrap.servers": "localhost:9092",
    "client.id": socket.gethostname(),
}
producer = Producer(conf)


class Listener(stomp.ConnectionListener):
    _mq: stomp.Connection

    def __init__(self, mq: stomp.Connection):
        self._mq = mq

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)
        self._mq.ack(id=headers["message-id"], subscription=headers["subscription"])

        for message in parsed_body:
            header = message["header"]
            msg_type = header["msg_type"]
            msg_queue_timestamp = header["msg_queue_timestamp"]
            timestamp = int(msg_queue_timestamp) / 1000
            utc_datetime = datetime.utcfromtimestamp(timestamp)
            uk_datetime = TIMEZONE_LONDON.fromutc(utc_datetime)
            
            producer.produce(topic, json.dumps(message))
            producer.flush()

            print(f"{uk_datetime} - Produced a message type of {msg_type} successfully")


if __name__ == "__main__":
    with open("secrets.json") as f:
        feed_username, feed_password = json.load(f)

    connection = stomp.Connection(
        [
            ("datafeeds.networkrail.co.uk", 61618)
        ],
        keepalive=True,
        heartbeats=(10000, 10000),
    )
    connection.set_listener("", Listener(connection))

    connection.connect(**{
        "username": feed_username,
        "passcode": feed_password,
        "wait": True,
        "client-id": feed_username,
    })

    # Train Movements feed: https://wiki.openraildata.com/index.php?title=Train_Movements
    connection.subscribe(**{
        "destination": "/topic/TRAIN_MVT_ALL_TOC",
        "id": 1,
        "ack": "client-individual",
        "activemq.subscriptionName": "TRAIN_MVT_ALL_TOC",
    })

    while connection.is_connected():
        sleep(1)
