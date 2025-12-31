# import typing as ta
#
# from omlish import check
# from omlish import dataclasses as dc
# from omlish import lang
#
# from ..services.requests import Request
# from ..services.responses import Response
# from ..services.services import Service
# from ..types import Option
# from ..types import Output
#
#
# RequestV = ta.TypeVar('RequestV')
# OptionT = ta.TypeVar('OptionT', bound=Option)
#
# ResponseV = ta.TypeVar('ResponseV')
# OutputT = ta.TypeVar('OutputT', bound=Output)
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class FirstInWinsServiceCancelledError(Exception):
#     e: BaseException
#
#
# class FirstInWinsServiceExceptionGroup(ExceptionGroup):
#     pass
#
#
# @dc.dataclass(frozen=True)
# class FirstInWinsServiceOutput(Output):
#     first_in_wins_service: 'FirstInWinsService'
#     response_service: Service
#     service_exceptions: ta.Mapping[Service, Exception] | None = None
#
#
# class FirstInWinsService(
#     lang.Abstract,
#     ta.Generic[
#         RequestV,
#         OptionT,
#         ResponseV,
#         OutputT,
#     ],
# ):
#     def __init__(
#             self,
#             *services: Service[
#                 Request[
#                     RequestV,
#                     OptionT,
#                 ],
#                 Response[
#                     ResponseV,
#                     OutputT,
#                 ],
#             ],
#     ) -> None:
#         super().__init__()
#
#         self._services = check.not_empty(services)
