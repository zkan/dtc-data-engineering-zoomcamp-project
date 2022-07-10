#!/usr/bin/env python3

# Standard
from datetime import datetime
from time import sleep
import json

# Third party
import stomp

from pytz import timezone


TIMEZONE_LONDON: timezone = timezone("Europe/London")

# TD message types

C_BERTH_STEP = "CA"       # Berth step      - description moves from "from" berth into "to", "from" berth is erased
C_BERTH_CANCEL = "CB"     # Berth cancel    - description is erased from "from" berth
C_BERTH_INTERPOSE = "CC"  # Berth interpose - description is inserted into the "to" berth, previous contents erased
C_HEARTBEAT = "CT"        # Heartbeat       - sent periodically by a train describer

S_SIGNALLING_UDPATE = "SF"            # Signalling update
S_SIGNALLING_REFRESH = "SG"           # Signalling refresh
S_SIGNALLING_REFRESH_FINISHED = "SH"  # Signalling refresh finished


class Listener(stomp.ConnectionListener):
    _mq: stomp.Connection

    def __init__(self, mq: stomp.Connection):
        self._mq = mq

    def on_message(self, frame):
        headers, message_raw = frame.headers, frame.body
        parsed_body = json.loads(message_raw)
        # Acknowledging messages is important, it's part of the basis for our durable subscription.
        self._mq.ack(id=headers["message-id"], subscription=headers["subscription"])

        # Each message in the queue is a JSON array
        for outer_message in parsed_body:
            # Each list element consists of a dict with a single entry - our real target - e.g. {"CA_MSG": {...}}
            message = list(outer_message.values())[0]

            message_type = message["msg_type"]

            # For the sake of demonstration, we're only displaying C-class messages
            if message_type in [C_BERTH_STEP, C_BERTH_CANCEL, C_BERTH_INTERPOSE]:
                # The feed time is in milliseconds, but python takes timestamps in seconds
                timestamp = int(message["time"])/1000

                area_id = message["area_id"]
                description = message.get("descr", "")
                from_berth = message.get("from", "")
                to_berth = message.get("to", "")

                utc_datetime = datetime.utcfromtimestamp(timestamp)
                uk_datetime = TIMEZONE_LONDON.fromutc(utc_datetime)

                print("{} [{:2}] {:2} {:4} {:>5}->{:5}".format(
                    uk_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    message_type, area_id, description, from_berth, to_berth,
                    ))

    def on_error(self, frame):
        print('received an error {}'.format(frame.message))


if __name__ == "__main__":
    with open("secrets.json") as f:
        feed_username, feed_password = json.load(f)

    # https://stomp.github.io/stomp-specification-1.2.html#Heart-beating
    # We're committing to sending and accepting heartbeats every 5000ms
    connection = stomp.Connection([('datafeeds.networkrail.co.uk', 61618)], keepalive=True, heartbeats=(5000, 5000))
    connection.set_listener('', Listener(connection))

    # The client-id header is part of the durable subscription - it should be unique to your account
    connection.connect(**{
        "username": feed_username,
        "passcode": feed_password,
        "wait": True,
        "client-id": feed_username,
    })
    # The activemq.subscriptionName header is also part of the durable subscription, it should be subscription-unique
    # For example,
    connection.subscribe(**{
        "destination": "/topic/TD_ALL_SIG_AREA",
        "id": 1,
        "ack": "client-individual",
        "activemq.subscriptionName": "TD_ALL_SIG_AREA",
    })

    while connection.is_connected():
        sleep(1)

