import os
import xdg
import argparse
import logging

import kafka
import psycopg2

from consumer import CheckConsumer
from producer import CheckProducer
from configuration import parse_config, WebMonitorConfig

SERVER = "kafka-3603f4b2-axeoman-a287.aivencloud.com:29940"


def run_producer(config: WebMonitorConfig):
    """Run WebMonitor consumer"""
    producer = kafka.KafkaProducer(
        bootstrap_servers=config.kafka.host_port,
        security_protocol="SSL",
        ssl_cafile=config.kafka.ssl_cafile,
        ssl_certfile=config.kafka.ssl_certfile,
        ssl_keyfile=config.kafka.ssl_keyfile,
    )
    check_producer = CheckProducer(
        producer,
        config.websites,
        config.kafka.topic,
    ) #yapf: disable
    check_producer.start()


def run_consumer(config: WebMonitorConfig):
    """Run WebMonitor consumer"""

    connection = psycopg2.connect(config.postgresql.dsn)

    consumer = kafka.KafkaConsumer(
        config.kafka.topic,
        group_id=config.kafka.consumer_group,
        bootstrap_servers=config.kafka.host_port,
        security_protocol="SSL",
        ssl_cafile=config.kafka.ssl_cafile,
        ssl_certfile=config.kafka.ssl_certfile,
        ssl_keyfile=config.kafka.ssl_keyfile,
    )
    check_consumer = CheckConsumer(
        connection,
        consumer,
        config.postgresql.table_prefix
    )
    check_consumer.start()


def create_argparser() -> argparse.ArgumentParser:
    """Construct all neccecery command-line arguments with argparse library"""
    parser = argparse.ArgumentParser(
        description=(
            "Tool that monitors website availability over the network, "
            "produces metrics about this and passes these events through "
            "Kafka instance into Postgresql database"
        )
    )
    parser.add_argument(
        "component",
        nargs="?",
        type=str,
        choices=["checker",
                 "saver"],
    )
    parser.add_argument(
        "-c",
        nargs="?",
        type=str,
        dest="config",
        default=os.path.join(xdg.XDG_CONFIG_HOME,
                             "webmonitor.yml"),
        help=(
            "config file for application. "
            "Default: ${XDG_CONFIG_HOME}/webmonitor.yml"
        )
    )

    return parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    args = create_argparser().parse_args()
    app_config = parse_config(args.config)

    if args.component == "checker":
        run_producer(app_config)
    elif args.component == "saver":
        run_consumer(app_config)
