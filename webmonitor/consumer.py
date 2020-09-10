"""Container for CheckConsumer class"""
import logging
import psycopg2

import kafka

from webchecker import WebCheckResult
from sql import (
    INSERT_METRICS_RESULT,
    INSERT_REGEXP_RESULT,
    INIT_METRICS_TABLE,
    INIT_REGEXP_TABLE,
    SELECT_REGEXP
)
from datetime import datetime


class CheckConsumer:
    """Collect data from kafka topic and save into PostgreSQL database"""
    _logger = logging.getLogger("check_consumer")

    def __init__(
        self,
        db_connection,
        consumer: kafka.KafkaConsumer,
        table_prefix: str = "webmonitor",
        create_table: bool = True
    ):
        self._db_connection = db_connection
        self._consumer = consumer
        self._table_prefix = table_prefix

        if create_table:
            self._create_table()

    def _handle_message(self, message):
        """Deserialize recieved message and save to database"""
        check_result = WebCheckResult.loads(message.value)
        self._save_to_database(
            check_result,
            datetime.fromtimestamp(message.timestamp / 1000)
        )

    def _create_table(self):
        """Create table for metrics data if not exists"""
        self._logger.info("Creating database table if not exists...")
        cursor = self._db_connection.cursor()
        cursor.execute(INIT_REGEXP_TABLE.format(prefix=self._table_prefix))
        cursor.execute(INIT_METRICS_TABLE.format(prefix=self._table_prefix))

        self._db_connection.commit()
        cursor.close()

    def _save_to_database(self, check_result: WebCheckResult, time: datetime):
        """Save result to database"""
        cursor = self._db_connection.cursor()

        if check_result.regexp:
            # Have to do this because ON `CONFLICT DO NOTHING RETURNING id`
            # returns NULL when no entry was updated
            cursor.execute(
                SELECT_REGEXP.format(prefix=self._table_prefix),
                (check_result.regexp,
                 )
            )

            if result := cursor.fetchone():
                regexp_id = result[0]
            else:
                regexp_id = cursor.execute(
                    INSERT_REGEXP_RESULT.format(prefix=self._table_prefix),
                    (check_result.regexp,
                     )
                )

        else:
            regexp_id = None

        cursor.execute(
            INSERT_METRICS_RESULT.format(prefix=self._table_prefix),
            (
                check_result.status_code,
                check_result.response_time,
                regexp_id,
                check_result.regexp_matched,
                time
            )
        )
        self._db_connection.commit()
        cursor.close()

    def start(self):
        """Save serialized WebCheckResult into database"""
        for message in self._consumer:
            self._logger.info(message)
            self._handle_message(message)
