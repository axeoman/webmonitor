"""
Check desired website and log metrics into Kafka topic. 
"""
import logging
from time import sleep
from typing import Optional, List

from concurrent.futures import ThreadPoolExecutor, as_completed
from configuration import WebSiteRules

import kafka
from webchecker import WebChecker


class CheckProducer:
    """Gathering metrics from website list asynchronicaly and send it into kafka topic"""
    _logger = logging.getLogger("check_producer")

    def __init__(
        self,
        producer: kafka.KafkaProducer,
        websites: List[WebSiteRules],
        topic: str,
    ):
        self._producer = producer
        self._websites = websites
        self._topic = topic

    def gather_and_send(self, url: str, regexp: Optional[str], interval: int):
        """Gather metrics and send into kafka topic"""
        while True:

            self._logger.info("Checking availability of %s", url)
            result = WebChecker.check_url(url, regexp=regexp)
            metadata = self._producer.send(
                self._topic,
                result.dumps().encode()
            )
            self._logger.info("Got Kafka metadata: %s", metadata)
            sleep(interval)

    def start(self):
        """Runs infinite monitoring loop with configured parameters"""
        self._logger.info(
            "Starting to monitor %s websites.",
            len(self._websites)
        )

        with ThreadPoolExecutor() as executor:
            futures = list()
            for website in self._websites:
                future = executor.submit(
                    self.gather_and_send,
                    website.url,
                    website.regexp,
                    website.interval
                )
                futures.append(future)

        for future in as_completed(futures):
            future.result()
