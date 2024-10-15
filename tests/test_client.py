import unittest
from unittest.mock import MagicMock, patch

import pytest

from tap_zendesk.client import ZendeskStream
from singer_sdk import typing as th
import logging


@pytest.fixture(autouse=True)
def mock_sleep():
    with patch('tap_zendesk.client.sleep', return_value=None) as mock_sleep:
        yield mock_sleep


class TestZendeskStream(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies."""
        self.tap_mock = MagicMock()
        self.tap_mock.config = {"min_remain_rate_limit": 10}
        dummy_schema = th.PropertiesList(th.Property("id", th.StringType)).to_dict()

        self.zendesk_stream = ZendeskStream(
            self.tap_mock, name="dummy_stream", schema=dummy_schema
        )
        self.zendesk_stream.logger = logging.getLogger("ZendeskStreamLogger")
        self.zendesk_stream.logger.setLevel(logging.DEBUG)
        self.log_stream = logging.StreamHandler()
        self.log_stream.setLevel(logging.DEBUG)
        self.zendesk_stream.logger.addHandler(self.log_stream)

    def test_check_rate_throttling_no_throttle(self):
        """Test when rate limit is not exceeded."""
        response = MagicMock()
        response.headers = {
            'x-rate-limit-remaining': '20',
            'x-rate-limit': '700',
        }

        with self.assertLogs(self.zendesk_stream.logger, level='DEBUG') as log:
            self.zendesk_stream.check_rate_throttling(response)
            self.assertIn('Remaining rate limit: 20/700', log.output[0])
            self.assertNotIn('API rate limit exceeded', log.output)

    def test_check_rate_throttling_with_throttle(self):
        """Test when rate limit is exceeded and there's a reset time."""
        response = MagicMock()
        response.headers = {
            'x-rate-limit-remaining': '5',
            'x-rate-limit': '700',
            'rate-limit-reset': '30',
        }

        with self.assertLogs(self.zendesk_stream.logger, level='DEBUG') as log:
            self.zendesk_stream.check_rate_throttling(response)
            self.assertIn('Remaining rate limit: 5/700 (reset in 30s)', log.output[0])
            self.assertIn('API rate limit exceeded', log.output[1])

    def test_check_rate_throttling_with_throttle_no_reset(self):
        """Test when rate limit is exceeded but no reset time is provided."""
        response = MagicMock()
        response.headers = {
            'x-rate-limit-remaining': '5',
            'x-rate-limit': '700',
        }

        with self.assertLogs(self.zendesk_stream.logger, level='DEBUG') as log:
            self.zendesk_stream.check_rate_throttling(response)
            self.assertIn('Remaining rate limit: 5/700 (no reset time)', log.output[0])
            self.assertIn('API rate limit exceeded', log.output[1])


if __name__ == "__main__":
    unittest.main()
