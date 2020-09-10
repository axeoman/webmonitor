import argparse
import logging

import kafka
from consumer import CheckConsumer
from producer import CheckProducer

SERVER = "kafka-3603f4b2-axeoman-a287.aivencloud.com:29940"


def run_producer():
    """Run WebMonitor consumer"""
    producer = kafka.KafkaProducer(
        bootstrap_servers=SERVER,
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )
    check_producer = CheckProducer(
        producer,
        ["https://google.com",
         "https://yandex.ru",
         "https://goooogle.com"],
        "webmonitor",
        1
    )
    check_producer.monitor()


def run_consumer():
    """Run WebMonitor consumer"""
    consumer = kafka.KafkaConsumer(
        "webmonitor",
        group_id="group1",
        bootstrap_servers=SERVER,
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )
    check_consumer = CheckConsumer("", consumer)
    check_consumer.consume()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description=(
            "Tool that monitors website availability over the network, "
            "produces metrics about this and passes these events through "
            "Kafka instance into Postgresql database"
        )
    )
    parser.add_argument(
        'component',
        nargs='?',
        type=str,
        choices=['checker',
                 'saver'],
    )
    args = parser.parse_args()

    if args.component == 'checker':
        run_producer()
    elif args.component == 'saver':
        run_consumer()
