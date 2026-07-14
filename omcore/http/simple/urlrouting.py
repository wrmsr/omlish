# ruff: noqa: UP006 UP007 UP045
# @om-lite
import dataclasses as dc
import typing as ta

from ..statuses import HttpStatus
from ..urlrouting.router import UrlRouter
from ..urlrouting.types import UrlRouteMatchError
from ..urlrouting.types import UrlRouteMethodNotAllowedError
from ..urlrouting.types import UrlRouteRedirectRequiredError
from .types import SimpleHttpHandler
from .types import SimpleHttpHandler_
from .types import SimpleHttpHandlerRequest
from .types import SimpleHttpHandlerResponse


##


@dc.dataclass(frozen=True)
class UrlRoutingSimpleHttpHandler(SimpleHttpHandler_):
    router: UrlRouter

    not_found_handler: ta.Optional[SimpleHttpHandler] = None
    method_not_allowed_handler: ta.Optional[SimpleHttpHandler] = None

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        try:
            match = self.router.match(req.path, method=req.method)

        except UrlRouteRedirectRequiredError as e:
            return SimpleHttpHandlerResponse(
                status=HttpStatus.PERMANENT_REDIRECT,
                headers={'Location': e.redirect_path},
            )

        except UrlRouteMethodNotAllowedError as e:
            if self.method_not_allowed_handler is not None:
                return self.method_not_allowed_handler(req)

            return SimpleHttpHandlerResponse(
                status=HttpStatus.METHOD_NOT_ALLOWED,
                headers={'Allow': ', '.join(sorted(e.allowed_methods))},
            )

        except UrlRouteMatchError:
            if self.not_found_handler is not None:
                return self.not_found_handler(req)

            return SimpleHttpHandlerResponse(status=HttpStatus.NOT_FOUND)

        endpoint = match.endpoint
        if not callable(endpoint):
            raise TypeError(endpoint)

        return endpoint(req.with_context(match))
