import json
from datetime import datetime
from time import sleep

import stomp
from pytz import timezone


TIMEZONE_LONDON: timezone = timezone("Europe/London")


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
            message_type = header["msg_type"]
            body = message["body"]
            if message_type == "0003":
                timestamp = int(body["actual_timestamp"])/1000
                utc_datetime = datetime.utcfromtimestamp(timestamp)
                uk_datetime = TIMEZONE_LONDON.fromutc(utc_datetime)

                print(header["msg_type"], body["event_type"], body["toc_id"], body["variation_status"], uk_datetime)


if __name__ == "__main__":
    with open("secrets.json") as f:
        feed_username, feed_password = json.load(f)

    connection = stomp.Connection(
        [
            ("datafeeds.networkrail.co.uk", 61618)
        ],
        keepalive=True,
        heartbeats=(5000, 5000),
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
