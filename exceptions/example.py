from typing import Any, Dict

from sanic.exceptions import SanicException


class ExampleException(SanicException):
    def __init__(
        self,
        message: str,
        status_code: int = 418,
        quiet: bool | None = None,
        context: Dict[str, Any] | None = None,
        extra: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, quiet, context, extra)
