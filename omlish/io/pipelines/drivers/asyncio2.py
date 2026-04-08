#
#
# ##
#
#
# class PollAsyncioStreamIoPipelineDriver(AsyncioStreamIoPipelineDriver):
#     async def _poll(self) -> ta.Union[
#         ta.Tuple[ta.Literal['unhandled'], ta.Any],
#         ta.Literal['read', 'stop'],
#         None,
#     ]:
#         check.state(self._pipeline.is_ready)
#
#         while True:
#             if (out_msg := self._pipeline.output.poll()) is not None:
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
#     async def next(
#             self,
#             *,
#             read: bool = True,
#             raise_on_stall: bool = True,
#     ) -> ta.Optional[ta.Any]:
#         if not self._has_init:
#             try:
#                 self._shutdown_task  # noqa
#             except AttributeError:
#                 pass
#             else:
#                 raise RuntimeError('Already running')
#
#             await self._init()
#
#             self._shutdown_task = asyncio.create_task(self._shutdown_task_main())
#
#             self._command_queue.put_nowait(AsyncioStreamIoPipelineDriver._FeedInCommand([
#                 IoPipelineMessages.InitialInput(),
#             ]))
#
#         pipeline = self._ensure_pipeline()  # noqa
#         check.state(pipeline.is_ready)
#
#         while True:
#             out = self._poll()
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
#     async def loop_until_done(self) -> None:
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
