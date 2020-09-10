"""Collect data from kafka topic and save into PostgreSQL database"""
import logging

import psycopg2
import kafka


class CheckConsumer:
    _logger = logging.getLogger("consumer")

    def __init__(self, db_connection, consumer: kafka.KafkaConsumer):
        self._db_connection = db_connection
        self._consumer = consumer

    def consume(self):
        for message in self._consumer:
            self._logger.info(message)
