"""Container for CheckConsumer class"""
import logging
from datetime import datetime

import kafka

from .webchecker import WebCheckResult
from .sql import (
    INSERT_METRICS_RESULT,
    INSERT_REGEXP,
    INSERT_URL,
    INIT_METRICS_TABLE,
    INIT_REGEXPS_TABLE,
    INIT_URLS_TABLE,
    SELECT_REGEXPS,
    SELECT_URLS
)


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
            self._create_tables()

    def _handle_message(self, message):
        """Deserialize recieved message and save to database"""
        check_result = WebCheckResult.loads(message.value)
        self._save_to_database(
            check_result,
            datetime.fromtimestamp(message.timestamp / 1000)
        )

    def _create_tables(self):
        """Create table for metrics data if not exists"""
        self._logger.info("Creating database table if not exists...")
        cursor = self._db_connection.cursor()
        cursor.execute(INIT_REGEXPS_TABLE.format(prefix=self._table_prefix))
        cursor.execute(INIT_URLS_TABLE.format(prefix=self._table_prefix))
        cursor.execute(INIT_METRICS_TABLE.format(prefix=self._table_prefix))

        self._db_connection.commit()
        cursor.close()

    def _save_to_database(self, check_result: WebCheckResult, time: datetime):
        """Save result to database"""
        cursor = self._db_connection.cursor()
        regexp_id = self._get_regexp_id(check_result.regexp, cursor)
        url_id = self._get_url_id(check_result.url, cursor)
        cursor.execute(
            INSERT_METRICS_RESULT.format(prefix=self._table_prefix),
            (
                url_id,
                check_result.status_code,
                check_result.response_time,
                regexp_id,
                check_result.regexp_matched,
                check_result.connection_error,
                time
            )
        )
        self._db_connection.commit()
        cursor.close()

    def _get_regexp_id(self, pattern, cursor) -> int:
        """Get or create regexp entry and return its id"""
        if pattern:

            cursor.execute(
                SELECT_REGEXPS.format(prefix=self._table_prefix),
                (pattern,
                 )
            )
            if result := cursor.fetchone():
                regexp_id = result[0]
            else:
                cursor.execute(
                    INSERT_REGEXP.format(prefix=self._table_prefix),
                    (pattern,
                     )
                )
                regexp_id = cursor.fetchone()[0]

        else:
            regexp_id = None

        return regexp_id

    def _get_url_id(self, url, cursor) -> int:
        """Get or create url entry and return its id"""

        cursor.execute(SELECT_URLS.format(prefix=self._table_prefix), (url, ))
        if result := cursor.fetchone():
            url_id = result[0]
        else:
            cursor.execute(
                INSERT_URL.format(prefix=self._table_prefix),
                (url,
                 )
            )
            url_id = cursor.fetchone()[0]

        return url_id

    def start(self):
        """Save serialized WebCheckResult into database"""
        for message in self._consumer:
            self._logger.info(message)
            self._handle_message(message)
