"""
https://github.com/python-hyper/h11/blob/cc87dfcc5a4693eb49b0453e6677ca004ffb035b/examples/trio-server.py
"""
import datetime
import email.utils
import itertools
import json
import logging
import typing as ta

from omlish import check
from omlish import logs
from omlish.asyncs import anyio as aiou
import anyio.abc
import h11


log = logging.getLogger(__name__)


MAX_RECV = 2**16
TIMEOUT = 10


def format_date_time(dt=None):
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    return email.utils.format_datetime(dt, usegmt=True)


class AnyioHTTPWrapper:
    _next_id = itertools.count()

    def __init__(self, stream: anyio.abc.SocketStream) -> None:
        super().__init__()
        self.stream = stream
        self.conn = h11.Connection(h11.SERVER)
        # Our Server: header
        self.ident = ' '.join(
            [f'h11-example-anyio-server/{h11.__version__}', h11.PRODUCT_ID]
        ).encode('ascii')
        self._obj_id = next(AnyioHTTPWrapper._next_id)

    async def send(self, event: h11.Event) -> None:
        # The code below doesn't send ConnectionClosed, so we don't bother handling it here either -- it would require
        # that we do something appropriate when 'data' is None.
        check.not_isinstance(event, h11.ConnectionClosed)
        data = self.conn.send(event)
        try:
            await self.stream.send(data)
        except BaseException:
            # If send_all raises an exception (especially trio.Cancelled), we have no choice but to give it up.
            self.conn.send_failed()
            raise

    async def _read_from_peer(self) -> None:
        if self.conn.they_are_waiting_for_100_continue:
            self.debug('Sending 100 Continue')
            go_ahead = h11.InformationalResponse(
                status_code=100,
                headers=self.basic_headers(),
            )
            await self.send(go_ahead)

        try:
            data = await aiou.anyio_eof_to_empty(self.stream.receive, MAX_RECV)
        except ConnectionError:
            data = b''

        self.conn.receive_data(data)

    async def next_event(self) -> h11.Event:
        while True:
            event = self.conn.next_event()
            if event is h11.NEED_DATA:
                await self._read_from_peer()
                continue
            return event

    async def shutdown_and_clean_up(self) -> None:
        # When this method is called, it's because we definitely want to kill # this connection, either as a clean
        # shutdown or because of some kind # of error or loss-of-sync bug, and we no longer care if that violates # the
        # protocol or not. So we ignore the state of self.conn, and just # go ahead and do the shutdown on the socket
        # directly. (If you're # implementing a client you might prefer to send ConnectionClosed() # and let it raise an
        # exception if that violates the protocol.)
        try:
            await self.stream.send_eof()
        except anyio.BrokenResourceError:
            # They're already gone, nothing to do
            return

        # Wait and read for a bit to give them a chance to see that we closed things, but eventually give up and just
        # close the socket.
        # XX FIXME: possibly we should set SO_LINGER to 0 here, so that in the case where the client has ignored our
        #  shutdown and declined to initiate the close themselves, we do a violent shutdown (RST) and avoid the
        #  TIME_WAIT?
        # it looks like nginx never does this for keepalive timeouts, and only does it for regular timeouts (slow
        # clients I guess?) if explicitly enabled ('Default: reset_timedout_connection off')
        with anyio.move_on_after(TIMEOUT):
            try:
                while True:
                    # Attempt to read until EOF
                    got = await aiou.anyio_eof_to_empty(self.stream.receive, MAX_RECV)
                    if not got:
                        break
            except anyio.BrokenResourceError:
                pass
            finally:
                await self.stream.aclose()

    def basic_headers(self) -> list[tuple[str, bytes | str]]:
        return [
            ('Date', format_date_time().encode('ascii')),
            ('Server', self.ident),
        ]

    def debug(self, *args: ta.Any) -> None:
        log.debug(' '.join(map(str, [f'{self._obj_id}:', *args])))


async def http_serve(stream: anyio.abc.SocketStream) -> None:
    wrapper = AnyioHTTPWrapper(stream)
    wrapper.debug('Got new connection')
    while True:
        check.equal(wrapper.conn.states, {h11.CLIENT: h11.IDLE, h11.SERVER: h11.IDLE})

        try:
            with anyio.fail_after(TIMEOUT):
                wrapper.debug('Server main loop waiting for request')
                event = await wrapper.next_event()
                wrapper.debug('Server main loop got event:', event)
                if type(event) is h11.Request:
                    await send_echo_response(wrapper, check.isinstance(event, h11.Request))
        except Exception as exc:
            wrapper.debug(f'Error during response handler: {exc!r}')
            await maybe_send_error_response(wrapper, exc)

        if wrapper.conn.our_state is h11.MUST_CLOSE:
            wrapper.debug('connection is not reusable, so shutting down')
            await wrapper.shutdown_and_clean_up()
            return
        else:
            try:
                wrapper.debug('trying to re-use connection')
                wrapper.conn.start_next_cycle()
            except h11.ProtocolError:
                states = wrapper.conn.states
                wrapper.debug('unexpected state', states, '-- bailing out')
                await maybe_send_error_response(
                    wrapper, RuntimeError(f'unexpected state {states}')
                )
                await wrapper.shutdown_and_clean_up()
                return


async def send_simple_response(
        wrapper: AnyioHTTPWrapper,
        status_code: int,
        content_type: str,
        body: bytes,
) -> None:
    wrapper.debug('Sending', status_code, 'response with', len(body), 'bytes')

    headers = wrapper.basic_headers()
    headers.append(('Content-Type', content_type))
    headers.append(('Content-Length', str(len(body))))

    await wrapper.send(h11.Response(status_code=status_code, headers=headers))
    await wrapper.send(h11.Data(data=body))
    await wrapper.send(h11.EndOfMessage())


async def maybe_send_error_response(wrapper: AnyioHTTPWrapper, exc: BaseException) -> None:
    wrapper.debug('trying to send error response...')
    if wrapper.conn.our_state not in {h11.IDLE, h11.SEND_RESPONSE}:
        wrapper.debug("...but I can't, because our state is", wrapper.conn.our_state)
        return

    try:
        if isinstance(exc, h11.RemoteProtocolError):
            status_code = exc.error_status_hint
        # elif isinstance(exc, anyio.TooSlowError):  # FIXME:
        #     status_code = 408  # Request Timeout
        elif isinstance(exc, TimeoutError):
            status_code = 408  # Request Timeout
        else:
            status_code = 500
        body = str(exc).encode('utf-8')
        await send_simple_response(
            wrapper, status_code, 'text/plain; charset=utf-8', body
        )

    except Exception as exc:
        wrapper.debug('error while sending error response:', exc)


async def send_echo_response(wrapper: AnyioHTTPWrapper, request: h11.Request) -> None:
    wrapper.debug('Preparing echo response')
    if request.method not in {b'GET', b'POST'}:
        # Laziness: we should send a proper 405 Method Not Allowed with the appropriate Accept: header, but we don't.
        raise RuntimeError('unsupported method')

    response_json = {
        'method': request.method.decode('ascii'),
        'target': request.target.decode('ascii'),
        'headers': [
            (name.decode('ascii'), value.decode('ascii'))
            for (name, value) in request.headers
        ],
        'body': '',
    }

    while True:
        next_event = await wrapper.next_event()
        if type(next_event) is h11.EndOfMessage:
            break
        data_event = check.isinstance(next_event, h11.Data)
        response_json['body'] += data_event.data.decode('ascii')

    response_body_unicode = json.dumps(
        response_json,
        sort_keys=True,
        indent=4,
        separators=(',', ': '),
    )

    await send_simple_response(
        wrapper,
        200,
        'application/json; charset=utf-8',
        response_body_unicode.encode('utf-8'),
    )


async def serve(port: int) -> None:
    log.info(f'listening on http://localhost:{port}')
    try:
        listener = await anyio.create_tcp_listener(local_port=port)
        await listener.serve(http_serve)
    except KeyboardInterrupt:
        log.info('KeyboardInterrupt - shutting down')


if __name__ == '__main__':
    logs.configure_standard_logging('DEBUG')
    anyio.run(
        serve,
        8080,
        # backend='trio',
    )
