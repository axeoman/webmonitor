"""
Check desired website and log metrics into Kafka topic. 
"""
import logging
from time import sleep
from typing import List, Union, Optional, Tuple

from concurrent.futures import ThreadPoolExecutor, as_completed

import kafka
from webchecker import WebChecker


class CheckProducer:
    """Gathering metrics from website list asynchronicaly and send it into kafka topic"""
    _logger = logging.getLogger("check_producer")

    def __init__(
        self,
        producer: kafka.KafkaProducer,
        websites: Tuple[str,
                        Optional[str]],
        topic: str,
        interval: int
    ):
        self._producer = producer
        self._websites = websites
        self._topic = topic
        self._interval = interval

    def gather_and_send(self, url: str, regexp: Optional[str]):
        """Gather metrics and send into kafka topic"""
        while True:
            try:
                self._logger.info("Checking availability of %s", url)
                result = WebChecker.check_url(url, timeout=2, regexp=regexp)
                metadata = self._producer.send(
                    self._topic,
                    result.dumps().encode()
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

    def start(self):
        """Runs infinite monitoring loop with configured parameters"""
        self._logger.info(
            "Starting to monitor %s websites.",
            len(self._websites)
        )

        with ThreadPoolExecutor() as executor:
            futures = list()
            for website in self._websites:
                if len(website) > 1:
                    url, regexp = website
                else:
                    url = website
                    regexp = None

                future = executor.submit(self.gather_and_send, url, regexp)
                futures.append(future)

        for future in as_completed(futures):
            future.result()
