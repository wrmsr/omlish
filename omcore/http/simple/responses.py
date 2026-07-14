# ruff: noqa: UP007 UP045
# @om-lite
import io
import typing as ta

from ...lite.json import JsonStyle
from ...lite.json import json_dump_encode
from ...lite.namespaces import NamespaceClass
from ..statuses import HttpStatus
from .types import SimpleHttpHandlerResponse


##


class SimpleHttpHandlerResponses(NamespaceClass):
    @classmethod
    def not_found(
            cls,
            **kwargs: ta.Any,
    ) -> SimpleHttpHandlerResponse:
        return SimpleHttpHandlerResponse(
            status=HttpStatus.NOT_FOUND,
            **kwargs,
        )

    @classmethod
    def text(
            cls,
            msg: str,
            *,
            status: ta.Union[HttpStatus, int] = 200,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> SimpleHttpHandlerResponse:
        return SimpleHttpHandlerResponse(
            status=status,
            data=msg.encode('utf-8'),
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                **(headers or {}),
            },
            **kwargs,
        )

    @classmethod
    def json(
            cls,
            obj: ta.Any,
            *,
            style: JsonStyle = None,
            status: ta.Union[HttpStatus, int] = 200,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> SimpleHttpHandlerResponse:
        out = io.BytesIO()
        json_dump_encode(obj, out, style=style)
        out.write(b'\n')

        return SimpleHttpHandlerResponse(
            status=status,
            data=out.getvalue(),
            headers={
                'Content-Type': 'application/json',
                **(headers or {}),
            },
            **kwargs,
        )
