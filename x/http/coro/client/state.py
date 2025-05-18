import dataclasses as dc
import email.message

from omlish.lite.maybes import Maybe


##


@dc.dataclass()
class ResponseState:
    # If the response includes a content-length header, we need to make sure that the client doesn't read more than
    # the specified number of bytes. If it does, it will block until the server times out and closes the connection.
    # This will happen if a self.fp.read() is done (without a size) whether self.fp is buffered or not. So, no
    # self.fp.read() by clients unless they know what they are doing.
    method: Maybe[str] = Maybe.empty()

    # The HttpResponse object is returned via urllib. The clients of http and urllib expect different attributes for
    # the headers. headers is used here and supports urllib. msg is provided as a backwards compatibility layer for
    # http clients.
    headers: Maybe[email.message.Message] = Maybe.empty()

    # from the Status-Line of the response
    version: Maybe[int] = Maybe.empty()  # HTTP-Version
    status: Maybe[str] = Maybe.empty()  # Status-Code
    reason: Maybe[str] = Maybe.empty()  # Reason-Phrase

    chunked: Maybe[bool] = False  # is "chunked" being used?
    chunk_left: Maybe[int] = Maybe.empty()  # bytes left to read in current chunk

    length: Maybe[int] = Maybe.empty()  # number of bytes left in response

    will_close: Maybe[bool] = Maybe.empty()  # conn will close at end of response
