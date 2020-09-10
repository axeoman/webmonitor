"""Container for WebChecker class and its models"""
from dataclasses import dataclass, asdict
from typing import Optional
import logging
import re

import json

import requests


@dataclass
class WebCheckResult:
    """Data class for web monitor metrics"""
    status_code: int
    response_time: int
    regexp: Optional[str] = None
    regexp_matched: Optional[bool] = None

    def dumps(self) -> str:
        """Serialize WebCheckResult into json"""
        return json.dumps(asdict(self))

    @classmethod
    def loads(cls, message: str) -> "WebCheckResult":
        """Deserialize json into WebCheckResult objects"""
        return WebCheckResult(**json.loads(message))


class WebChecker:
    """Class provides public methods that checks availability of the website"""
    _logger = logging.getLogger("webchecker")

    @classmethod
    def check_url(
        cls,
        url: str,
        regexp: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> WebCheckResult:
        """Check url for availablity."""

        resp = requests.get(url, timeout=timeout)

        result = WebCheckResult(
            status_code=resp.status_code,
            response_time=resp.elapsed.microseconds,
        )

        if regexp:
            result.regexp = regexp
            result.regexp_matched = cls._match_regexp(regexp, resp.text)

        return result

    @classmethod
    def _match_regexp(cls, regexp: str, body: str) -> bool:
        """Function check if provided contents matches regexp pattern"""
        return bool(re.match(regexp, body))
