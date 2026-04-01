# # ruff: noqa: UP006 UP007 UP045
# # @omlish-lite
# """
# TODO:
#  - can implement sched w/ settimeout
#  - sanity / upper bound read/write timeouts
# """
# import collections
# import dataclasses as dc
# import typing as ta
#
# from ....lite.check import check
# from ....logs.modules import get_module_logger
# from ...fdio.handlers import SocketFdioHandler
# from ...streams.utils import ByteStreamBuffers
# from ..core import IoPipeline
# from ..core import IoPipelineMessages
# from ..flow.types import IoPipelineFlow
# from ..flow.types import IoPipelineFlowMessages
# from .metadata import DriverIoPipelineMetadata
#
#
# log = get_module_logger(globals())  # noqa
#
#
# ##
#
#
# class IoPipelineDriverSocketFdioHandler(SocketFdioHandler):
#     @dc.dataclass(frozen=True)
#     class Config:
#         DEFAULT: ta.ClassVar['IoPipelineDriverSocketFdioHandler.Config']
#
#         read_chunk_size: int = 64 * 1024
#         write_chunk_max: ta.Optional[int] = None
#
#         strict_input_flow: bool = False
#
#     Config.DEFAULT = Config()
#
#     #
#
#     def __init__(
#             self,
#             spec: IoPipeline.Spec,
#             sock: ta.Any,
#             config: ta.Optional[Config] = None,
#     ) -> None:
#         super().__init__()
#
#         self._spec = spec
#         self._sock = sock
#         if config is None:
#             config = self.Config.DEFAULT
#         self._config = config
#
#         self._input_q: collections.deque[ta.Any] = collections.deque()
#         self._input_q.append(IoPipelineMessages.InitialInput())
#
#     def __repr__(self) -> str:
#         return f'{type(self).__name__}@{id(self):x}'
#
#     @property
#     def config(self) -> Config:
#         return self._config
#
#     @property
#     def pipeline(self) -> IoPipeline:
#         return self._pipeline
#
#     #
#
#     _pipeline: IoPipeline
#
#     _flow: ta.Optional[IoPipelineFlow]
#
#     def _opt_pipeline(self) -> ta.Optional[IoPipeline]:
#         try:
#             return self._pipeline
#         except AttributeError:
#             return None
#
#     def _ensure_pipeline(self) -> IoPipeline:
#         try:
#             return self._pipeline
#         except AttributeError:
#             pass
#
#         self._pipeline = pipeline = self._make_pipeline()
#
#         self._flow = flow = pipeline.services.find(IoPipelineFlow)
#         if flow is None:
#             self._want_read = True
#
#         return pipeline
#
#     def _make_pipeline(self) -> IoPipeline:
#         return IoPipeline(dc.replace(
#             self._spec,
#
#             metadata=[
#                 *self._spec.metadata,
#                 DriverIoPipelineMetadata(self),
#             ],
#         ))
#
#     @property
#     def is_running(self) -> bool:
#         if (pipeline := self._opt_pipeline()) is None:
#             return False
#         return pipeline.is_ready
#
#     #
#
#     def close(self) -> None:
#         try:
#             if (pipeline := self._opt_pipeline()) is not None:
#                 pipeline.destroy()
#         finally:
#             super().close()
#
#     #
#
#     _want_read: bool = False
#
#     def _do_read(self) -> ta.List[ta.Any]:
#         out: ta.List[ta.Any] = []
#
#         b = self._sock.recv(self._config.read_chunk_size)
#
#         if not b:
#             out.append(IoPipelineMessages.FinalInput())
#         else:
#             out.append(b)
#             if self._flow is not None:
#                 out.append(IoPipelineFlowMessages.FlushInput())
#
#         if self._flow is not None:
#             self._want_read = False
#
#         return out
#
#     #
#
#     def _handle_output(self, msg: ta.Any) -> ta.Literal['handled', 'unhandled', 'stop']:
#         if ByteStreamBuffers.can_bytes(msg):
#             for mv in ByteStreamBuffers.iter_segments(msg):
#                 # self._sock.settimeout(None)
#                 self._sock.send(mv)
#             return 'handled'
#
#         elif isinstance(msg, IoPipelineFlowMessages.FlushOutput):
#             # self._sock.flush()
#             return 'handled'
#
#         elif isinstance(msg, IoPipelineMessages.FinalOutput):
#             return 'stop'
#
#         elif isinstance(msg, IoPipelineMessages.Defer):
#             self._pipeline.run_deferred(msg)
#             return 'handled'
#
#         elif isinstance(msg, IoPipelineFlowMessages.ReadyForInput):
#             check.state(self._flow is not None)
#             if self._config.strict_input_flow:
#                 check.state(not self._want_read)
#             self._want_read = True
#             return 'handled'
#
#         else:
#             return 'unhandled'
#
#     #
#
#     def enqueue(self, *in_msgs: ta.Any) -> None:
#         self._input_q.extend(in_msgs)
#
#     def poll(self) -> ta.Union[
#         ta.Tuple[ta.Literal['unhandled'], ta.Any],
#         ta.Literal['read', 'stop'],
#         None,
#     ]:
#         pipeline = self._ensure_pipeline()  # noqa
#         check.state(pipeline.is_ready)
#
#         while True:
#             if (out_msg := pipeline.output.poll()) is not None:
#                 handled = self._handle_output(out_msg)
#
#                 if handled == 'handled':
#                     continue
#
#                 elif handled == 'unhandled':
#                     return ('unhandled', out_msg)
#
#                 elif handled == 'stop':
#                     return 'stop'
#
#                 else:
#                     raise RuntimeError(f'Unknown handled value: {handled!r}')
#
#             if self._input_q:
#                 pipeline.feed_in(self._input_q.popleft())
#                 continue
#
#             if not pipeline.saw_final_input and self._want_read:
#                 return 'read'
#
#             return None
#
#     def next(
#             self,
#             *,
#             read: bool = True,
#             raise_on_stall: bool = True,
#     ) -> ta.Optional[ta.Any]:
#         pipeline = self._ensure_pipeline()  # noqa
#         check.state(pipeline.is_ready)
#
#         while True:
#             out = self.poll()
#
#             if isinstance(out, tuple):
#                 ok, ov = out
#                 if ok == 'unhandled':
#                     return ov
#
#                 else:
#                     raise RuntimeError(f'Unknown output: {ok!r}')
#
#             elif out == 'read':
#                 if read:
#                     self._input_q.extend(self._do_read())
#
#                 else:
#                     return None
#
#             elif out == 'stop':
#                 break
#
#             elif out is None:
#                 if raise_on_stall:
#                     raise RuntimeError('Pipeline stalled')
#
#                 else:
#                     return None
#
#             else:
#                 raise RuntimeError(f'Unknown output: {out!r}')
#
#         pipeline.destroy()
#         return None
#
#     def loop_until_done(self) -> None:
#         try:
#             while True:
#                 if (out := self.next()) is not None:
#                     raise TypeError(out)
#
#                 if not self._pipeline.is_ready:
#                     break
#
#         finally:
#             self.close()
#
#     ##
#
#     def readable(self) -> bool:
#         return True
#
#     def writable(self) -> bool:
#         return self._write_buf is not None
#
#     #
#
#     def on_readable(self) -> None:
#         try:
#             buf = check.not_none(self._sock).recv(self._read_size)
#         except BlockingIOError:
#             return
#         except ConnectionResetError:
#             self.close()
#             return
#         if not buf:
#             self.close()
#             return
#
#         self._read_buf.feed(buf)
#
#         if isinstance(self._cur_io, CoroHttpIo.AnyReadIo):
#             self._next_io()
#
#     def on_writable(self) -> None:
#         check.isinstance(self._cur_io, CoroHttpIo.WriteIo)
#         wb = check.not_none(self._write_buf)
#         while wb.rem > 0:
#             def send(d: bytes) -> int:
#                 try:
#                     return check.not_none(self._sock).send(d)
#                 except ConnectionResetError:
#                     self.close()
#                     return 0
#                 except BlockingIOError:
#                     return 0
#             if not wb.write(send):
#                 break
#
#         if wb.rem < 1:
#             self._write_buf = None
#             self._cur_io = None
#             self._next_io()
