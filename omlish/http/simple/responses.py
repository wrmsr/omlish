# ruff: noqa: UP007 UP045
# @omlish-lite
import typing as ta

from ...lite.json import JsonStyle
from ...lite.json import json_dumps
from ...lite.namespaces import NamespaceClass
from ..statuses import HttpStatus
from .types import SimpleHttpHandlerResponse


##


class SimpleHttpHandlerResponses(NamespaceClass):
    @classmethod
    def of_json(
            cls,
            obj: ta.Any,
            *,
            style: JsonStyle = None,
            status: ta.Union[HttpStatus, int] = 200,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> SimpleHttpHandlerResponse:
        return SimpleHttpHandlerResponse(
            status=status,
            data=json_dumps(obj, style=style).encode('utf-8') + b'\n',
            headers={
                'Content-Type': 'application/json',
                **(headers or {}),
            },
            **kwargs,
        )
