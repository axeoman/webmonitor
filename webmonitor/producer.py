"""
Check desired website and log metrics into Kafka topic. 
"""
import logging
from time import sleep
from typing import List, Union

from concurrent.futures import ThreadPoolExecutor, as_completed

import kafka
from webchecker import WebChecker


class CheckProducer:
    """Gathering metrics from website list asynchronicaly and send it into kafka topic"""
    _logger = logging.getLogger("producer")

    def __init__(
        self,
        producer: kafka.KafkaProducer,
        websites: List[str],
        topic: str,
        interval: int
    ):
        self._producer = producer
        self._websites = websites
        self._topic = topic
        self._interval = interval

    def gather_and_send(self, url: str):
        """Gather metrics and send into kafka topic"""
        while True:
            try:
                self._logger.info("Checking availability of %s", url)
                result = WebChecker.check_url(url, timeout=2)
                metadata = self._producer.send(
                    self._topic,
                    result.json().encode()
                )
                self._logger.info("Got Kafka metadata: %s", metadata)
            except Exception as exc:  # Make exception not such broad
                self._logger.error(
                    'Checking %s generated an exception: %s',
                    url,
                    exc
                )
            finally:
                sleep(self._interval)

    def monitor(self):
        """Runs infinite monitoring loop with configured parameters"""
        self._logger.info(
            "Starting to monitor %s websites.",
            len(self._websites)
        )

        with ThreadPoolExecutor() as executor:
            future_to_url = {
                executor.submit(self.gather_and_send, url): url
                for url in self._websites
            } #yapf: disable

        for future in as_completed(future_to_url):
            future.result()
