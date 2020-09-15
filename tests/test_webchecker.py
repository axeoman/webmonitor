"""Tests for WebChecker class"""
import pytest

import responses

from webmonitor.webchecker import WebCheckResult, WebChecker

testdata = [
    (200, "Test Text", ".*", True, False),
    (200, "Test Text", "^Test.*$", True, False),
    (404, "Test Text", "^NEVERMATCH$", False, False),
] #yapf: disable


@pytest.mark.parametrize(
    "status_code, body, regexp, regexp_matched, connection_error",
    testdata
)
@responses.activate
def test_check_url(
    status_code: int,
    body: str,
    regexp: str,
    regexp_matched: bool,
    connection_error: bool
):
    """Parametrized test for WebChecker.check_url function"""
    website_url = "https://aiven.com"

    responses.add(responses.GET, website_url, status=status_code, body=body)
    result: WebCheckResult = WebChecker.check_url(website_url, regexp=regexp)

    assert result.url == website_url
    assert result.status_code == status_code
    assert result.regexp == regexp
    assert result.regexp_matched == regexp_matched
    assert result.connection_error == connection_error


def test_loads_dumps():
    """Check that loads and dumps methods are compatible"""

    result = WebCheckResult(
        url="https://aiven.com",
        status_code=200,
        regexp=".*",
        regexp_matched=True,
        connection_error=False
    )

    assert result == result.loads(result.dumps())
