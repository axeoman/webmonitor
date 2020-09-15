"""Test for CheckConsumer class"""
from unittest import mock

import kafka

from webmonitor.consumer import CheckConsumer


def test_consumer_calls():
    """Check that CheckConsumer is getting metrics from kafka"""

    mock_consumer = mock.MagicMock(kafka.KafkaConsumer)
    mock_dbconnection = mock.Mock()

    check_consumer = CheckConsumer(mock_dbconnection, mock_consumer)
    check_consumer.start()

    assert mock_consumer.mock_calls == [mock.call.__iter__()]
