"""Test for CheckProducer class"""
import kafka
from unittest import mock

from webmonitor.producer import CheckProducer
from webmonitor.webchecker import WebChecker, WebCheckResult
from webmonitor.configuration import WebSiteRules


def test_producer_calls():
    """Checks that CheckProducer is correctly sending gathered metrics from check_url method"""
    kafka_topic = "topic01"
    website_url = "https://aiven.com"

    mock_producer = mock.Mock(kafka.KafkaProducer)
    mock_checker = mock.Mock(WebChecker)

    webcheck_result = WebCheckResult(
        website_url,
        200,
        10000,
        False,
        '.*',
        True
    )
    mock_checker.check_url.return_value = webcheck_result

    websites = [WebSiteRules(website_url, interval=None)]
    producer = CheckProducer(
        mock_producer,
        websites,
        kafka_topic,
        webchecker=mock_checker
    )

    producer.start()

    mock_producer.send.assert_called_once()
    mock_producer.send.assert_called_with(
        kafka_topic,
        webcheck_result.dumps().encode()
    )
