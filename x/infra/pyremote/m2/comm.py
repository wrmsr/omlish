# Copyright 2019, David Wilson
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import binascii
import collections
import encodings.latin_1
import encodings.utf_8
import errno
import fcntl
import itertools
import logging
import os
import pickle as py_pickle
import pstats
import signal
import socket
import struct
import syslog
import threading
import time
import traceback
import types
import warnings
import weakref
import zlib


context_id = None


class Message:
    """
    Messages are the fundamental unit of communication, comprising fields from
    the :ref:`stream-protocol` header, an optional reference to the receiving
    :class:`mitogen.core.Router` for ingress messages, and helper methods for
    deserialization and generating replies.
    """
    #: Integer target context ID. :class:`Router` delivers messages locally
    #: when their :attr:`dst_id` matches :data:`mitogen.context_id`, otherwise
    #: they are routed up or downstream.
    dst_id = None

    #: Integer source context ID. Used as the target of replies if any are
    #: generated.
    src_id = None

    #: Context ID under whose authority the message is acting. See
    #: :ref:`source-verification`.
    auth_id = None

    #: Integer target handle in the destination context. This is one of the
    #: :ref:`standard-handles`, or a dynamically generated handle used to
    #: receive a one-time reply, such as the return value of a function call.
    handle = None

    #: Integer target handle to direct any reply to this message. Used to
    #: receive a one-time reply, such as the return value of a function call.
    #: :data:`IS_DEAD` has a special meaning when it appears in this field.
    reply_to = None

    #: Raw message data bytes.
    data = b('')

    _unpickled = object()

    #: The :class:`Router` responsible for routing the message. This is
    #: :data:`None` for locally originated messages.
    router = None

    #: The :class:`Receiver` over which the message was last received. Part of
    #: the :class:`mitogen.select.Select` interface. Defaults to :data:`None`.
    receiver = None

    HEADER_FMT = '>hLLLLLL'
    HEADER_LEN = struct.calcsize(HEADER_FMT)
    HEADER_MAGIC = 0x4d49  # 'MI'

    def __init__(self, **kwargs):
        """
        Construct a message from from the supplied `kwargs`. :attr:`src_id` and
        :attr:`auth_id` are always set to :data:`mitogen.context_id`.
        """
        self.src_id = mitogen.context_id
        self.auth_id = mitogen.context_id
        vars(self).update(kwargs)
        assert isinstance(self.data, BytesType), 'Message data is not Bytes'

    def pack(self):
        return (
                struct.pack(self.HEADER_FMT, self.HEADER_MAGIC, self.dst_id,
                            self.src_id, self.auth_id, self.handle,
                            self.reply_to or 0, len(self.data))
                + self.data
        )

    def _unpickle_context(self, context_id, name):
        return _unpickle_context(context_id, name, router=self.router)

    def _unpickle_sender(self, context_id, dst_handle):
        return _unpickle_sender(self.router, context_id, dst_handle)

    def _unpickle_bytes(self, s, encoding):
        s, n = LATIN1_CODEC.encode(s)
        return s

    def _find_global(self, module, func):
        """
        Return the class implementing `module_name.class_name` or raise
        `StreamError` if the module is not whitelisted.
        """
        if module == __name__:
            if func == '_unpickle_call_error' or func == 'CallError':
                return _unpickle_call_error
            elif func == '_unpickle_sender':
                return self._unpickle_sender
            elif func == '_unpickle_context':
                return self._unpickle_context
            elif func == 'Blob':
                return Blob
            elif func == 'Secret':
                return Secret
            elif func == 'Kwargs':
                return Kwargs
        elif module == '_codecs' and func == 'encode':
            return self._unpickle_bytes
        elif module == '__builtin__' and func == 'bytes':
            return BytesType
        raise StreamError('cannot unpickle %r/%r', module, func)

    @property
    def is_dead(self):
        """
        :data:`True` if :attr:`reply_to` is set to the magic value
        :data:`IS_DEAD`, indicating the sender considers the channel dead. Dead
        messages can be raised in a variety of circumstances, see
        :data:`IS_DEAD` for more information.
        """
        return self.reply_to == IS_DEAD

    @classmethod
    def dead(cls, reason=None, **kwargs):
        """
        Syntax helper to construct a dead message.
        """
        kwargs['data'], _ = encodings.utf_8.encode(reason or u'')
        return cls(reply_to=IS_DEAD, **kwargs)

    @classmethod
    def pickled(cls, obj, **kwargs):
        """
        Construct a pickled message, setting :attr:`data` to the serialization
        of `obj`, and setting remaining fields using `kwargs`.

        :returns:
            The new message.
        """
        self = cls(**kwargs)
        try:
            self.data = pickle__dumps(obj, protocol=2)
        except pickle.PicklingError:
            e = sys.exc_info()[1]
            self.data = pickle__dumps(CallError(e), protocol=2)
        return self

    def reply(self, msg, router=None, **kwargs):
        """
        Compose a reply to this message and send it using :attr:`router`, or
        `router` is :attr:`router` is :data:`None`.

        :param obj:
            Either a :class:`Message`, or an object to be serialized in order
            to construct a new message.
        :param router:
            Optional router to use if :attr:`router` is :data:`None`.
        :param kwargs:
            Optional keyword parameters overriding message fields in the reply.
        """
        if not isinstance(msg, Message):
            msg = Message.pickled(msg)
        msg.dst_id = self.src_id
        msg.handle = self.reply_to
        vars(msg).update(kwargs)
        if msg.handle:
            (self.router or router).route(msg)
        else:
            LOG.debug('dropping reply to message with no return address: %r',
                      msg)

    UNPICKLER_KWARGS = {'encoding': 'bytes'}

    def _throw_dead(self):
        if len(self.data):
            raise ChannelError(self.data.decode('utf-8', 'replace'))
        elif self.src_id == mitogen.context_id:
            raise ChannelError(ChannelError.local_msg)
        else:
            raise ChannelError(ChannelError.remote_msg)

    def unpickle(self, throw=True, throw_dead=True):
        """
        Unpickle :attr:`data`, optionally raising any exceptions present.

        :param bool throw_dead:
            If :data:`True`, raise exceptions, otherwise it is the caller's
            responsibility.

        :raises CallError:
            The serialized data contained CallError exception.
        :raises ChannelError:
            The `is_dead` field was set.
        """
        _vv and IOLOG.debug('%r.unpickle()', self)
        if throw_dead and self.is_dead:
            self._throw_dead()

        obj = self._unpickled
        if obj is Message._unpickled:
            fp = BytesIO(self.data)
            unpickler = _Unpickler(fp, **self.UNPICKLER_KWARGS)
            unpickler.find_global = self._find_global
            try:
                # Must occur off the broker thread.
                try:
                    obj = unpickler.load()
                except:
                    LOG.error('raw pickle was: %r', self.data)
                    raise
                self._unpickled = obj
            except (TypeError, ValueError):
                e = sys.exc_info()[1]
                raise StreamError('invalid message: %s', e)

        if throw:
            if isinstance(obj, CallError):
                raise obj

        return obj

    def __repr__(self):
        return 'Message(%r, %r, %r, %r, %r, %r..%d)' % (
            self.dst_id, self.src_id, self.auth_id, self.handle,
            self.reply_to, (self.data or '')[:50], len(self.data)
        )


class Sender:
    """
    Senders are used to send pickled messages to a handle in another context,
    it is the inverse of :class:`mitogen.core.Receiver`.

    Senders may be serialized, making them convenient to wire up data flows.
    See :meth:`mitogen.core.Receiver.to_sender` for more information.

    :param mitogen.core.Context context:
        Context to send messages to.
    :param int dst_handle:
        Destination handle to send messages to.
    """
    def __init__(self, context, dst_handle):
        self.context = context
        self.dst_handle = dst_handle

    def send(self, data):
        """
        Send `data` to the remote end.
        """
        _vv and IOLOG.debug('%r.send(%r..)', self, repr(data)[:100])
        self.context.send(Message.pickled(data, handle=self.dst_handle))

    explicit_close_msg = 'Sender was explicitly closed'

    def close(self):
        """
        Send a dead message to the remote, causing :meth:`ChannelError` to be
        raised in any waiting thread.
        """
        _vv and IOLOG.debug('%r.close()', self)
        self.context.send(
            Message.dead(
                reason=self.explicit_close_msg,
                handle=self.dst_handle
            )
        )

    def __repr__(self):
        return 'Sender(%r, %r)' % (self.context, self.dst_handle)

    def __reduce__(self):
        return _unpickle_sender, (self.context.context_id, self.dst_handle)


def _unpickle_sender(router, context_id, dst_handle):
    if not (isinstance(router, Router) and
            isinstance(context_id, int) and context_id >= 0 and
            isinstance(dst_handle, int) and dst_handle > 0):
        raise TypeError('cannot unpickle Sender: bad input or missing router')
    return Sender(Context(router, context_id), dst_handle)


class Receiver:
    """
    Receivers maintain a thread-safe queue of messages sent to a handle of this
    context from another context.

    :param mitogen.core.Router router:
        Router to register the handler on.

    :param int handle:
        If not :data:`None`, an explicit handle to register, otherwise an
        unused handle is chosen.

    :param bool persist:
        If :data:`False`, unregister the handler after one message is received.
        Single-message receivers are intended for RPC-like transactions, such
        as in the case of :meth:`mitogen.parent.Context.call_async`.

    :param mitogen.core.Context respondent:
        Context this receiver is receiving from. If not :data:`None`, arranges
        for the receiver to receive a dead message if messages can no longer be
        routed to the context due to disconnection, and ignores messages that
        did not originate from the respondent context.
    """
    #: If not :data:`None`, a function invoked as `notify(receiver)` after a
    #: message has been received. The function is invoked on :class:`Broker`
    #: thread, therefore it must not block. Used by
    #: :class:`mitogen.select.Select` to efficiently implement waiting on
    #: multiple event sources.
    notify = None

    raise_channelerror = True

    def __init__(self, router, handle=None, persist=True,
                 respondent=None, policy=None, overwrite=False):
        self.router = router
        #: The handle.
        self.handle = handle  # Avoid __repr__ crash in add_handler()
        self._latch = Latch()  # Must exist prior to .add_handler()
        self.handle = router.add_handler(
            fn=self._on_receive,
            handle=handle,
            policy=policy,
            persist=persist,
            respondent=respondent,
            overwrite=overwrite,
        )

    def __repr__(self):
        return 'Receiver(%r, %r)' % (self.router, self.handle)

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        self.close()

    def to_sender(self):
        """
        Return a :class:`Sender` configured to deliver messages to this
        receiver. As senders are serializable, this makes it convenient to pass
        `(context_id, handle)` pairs around::

            def deliver_monthly_report(sender):
                for line in open('monthly_report.txt'):
                    sender.send(line)
                sender.close()

            @mitogen.main()
            def main(router):
                remote = router.ssh(hostname='mainframe')
                recv = mitogen.core.Receiver(router)
                remote.call(deliver_monthly_report, recv.to_sender())
                for msg in recv:
                    print(msg)
        """
        return Sender(self.router.myself(), self.handle)

    def _on_receive(self, msg):
        """
        Callback registered for the handle with :class:`Router`; appends data
        to the internal queue.
        """
        _vv and IOLOG.debug('%r._on_receive(%r)', self, msg)
        self._latch.put(msg)
        if self.notify:
            self.notify(self)

    closed_msg = 'the Receiver has been closed'

    def close(self):
        """
        Unregister the receiver's handle from its associated router, and cause
        :class:`ChannelError` to be raised in any thread waiting in :meth:`get`
        on this receiver.
        """
        if self.handle:
            self.router.del_handler(self.handle)
            self.handle = None
        self._latch.close()

    def size(self):
        """
        Return the number of items currently buffered.

        As with :class:`Queue.Queue`, `0` may be returned even though a
        subsequent call to :meth:`get` will succeed, since a message may be
        posted at any moment between :meth:`size` and :meth:`get`.

        As with :class:`Queue.Queue`, `>0` may be returned even though a
        subsequent call to :meth:`get` will block, since another waiting thread
        may be woken at any moment between :meth:`size` and :meth:`get`.

        :raises LatchError:
            The underlying latch has already been marked closed.
        """
        return self._latch.size()

    def empty(self):
        """
        Return `size() == 0`.

        .. deprecated:: 0.2.8
           Use :meth:`size` instead.

        :raises LatchError:
            The latch has already been marked closed.
        """
        return self._latch.empty()

    def get(self, timeout=None, block=True, throw_dead=True):
        """
        Sleep waiting for a message to arrive on this receiver.

        :param float timeout:
            If not :data:`None`, specifies a timeout in seconds.

        :raises mitogen.core.ChannelError:
            The remote end indicated the channel should be closed,
            communication with it was lost, or :meth:`close` was called in the
            local process.

        :raises mitogen.core.TimeoutError:
            Timeout was reached.

        :returns:
            :class:`Message` that was received.
        """
        _vv and IOLOG.debug('%r.get(timeout=%r, block=%r)', self, timeout, block)
        try:
            msg = self._latch.get(timeout=timeout, block=block)
        except LatchError:
            raise ChannelError(self.closed_msg)
        if msg.is_dead and throw_dead:
            msg._throw_dead()
        return msg

    def __iter__(self):
        """
        Yield consecutive :class:`Message` instances delivered to this receiver
        until :class:`ChannelError` is raised.
        """
        while True:
            try:
                msg = self.get()
            except ChannelError:
                return
            yield msg


class Channel(Sender, Receiver):
    """
    A channel inherits from :class:`mitogen.core.Sender` and
    `mitogen.core.Receiver` to provide bidirectional functionality.

    .. deprecated:: 0.2.0
        This class is incomplete and obsolete, it will be removed in Mitogen
        0.3.

    Channels were an early attempt at syntax sugar. It is always easier to pass
    around unidirectional pairs of senders/receivers, even though the syntax is
    baroque:

    .. literalinclude:: ../examples/ping_pong.py

    Since all handles aren't known until after both ends are constructed, for
    both ends to communicate through a channel, it is necessary for one end to
    retrieve the handle allocated to the other and reconfigure its own channel
    to match. Currently this is a manual task.
    """
    def __init__(self, router, context, dst_handle, handle=None):
        Sender.__init__(self, context, dst_handle)
        Receiver.__init__(self, router, handle)

    def close(self):
        Receiver.close(self)
        Sender.close(self)

    def __repr__(self):
        return 'Channel(%s, %s)' % (
            Sender.__repr__(self),
            Receiver.__repr__(self)
        )


class Stream:
    """
    A :class:`Stream` is one readable and optionally one writeable file
    descriptor (represented by :class:`Side`) aggregated alongside an
    associated :class:`Protocol` that knows how to respond to IO readiness
    events for those descriptors.

    Streams are registered with :class:`Broker`, and callbacks are invoked on
    the broker thread in response to IO activity. When registered using
    :meth:`Broker.start_receive` or :meth:`Broker._start_transmit`, the broker
    may call any of :meth:`on_receive`, :meth:`on_transmit`,
    :meth:`on_shutdown` or :meth:`on_disconnect`.

    It is expected that the :class:`Protocol` associated with a stream will
    change over its life. For example during connection setup, the initial
    protocol may be :class:`mitogen.parent.BootstrapProtocol` that knows how to
    enter SSH and sudo passwords and transmit the :mod:`mitogen.core` source to
    the target, before handing off to :class:`MitogenProtocol` when the target
    process is initialized.

    Streams connecting to children are in turn aggregated by
    :class:`mitogen.parent.Connection`, which contains additional logic for
    managing any child process, and a reference to any separate ``stderr``
    :class:`Stream` connected to that process.
    """
    #: A :class:`Side` representing the stream's receive file descriptor.
    receive_side = None

    #: A :class:`Side` representing the stream's transmit file descriptor.
    transmit_side = None

    #: A :class:`Protocol` representing the protocol active on the stream.
    protocol = None

    #: In parents, the :class:`mitogen.parent.Connection` instance.
    conn = None

    #: The stream name. This is used in the :meth:`__repr__` output in any log
    #: messages, it may be any descriptive string.
    name = u'default'

    def set_protocol(self, protocol):
        """
        Bind a :class:`Protocol` to this stream, by updating
        :attr:`Protocol.stream` to refer to this stream, and updating this
        stream's :attr:`Stream.protocol` to the refer to the protocol. Any
        prior protocol's :attr:`Protocol.stream` is set to :data:`None`.
        """
        if self.protocol:
            self.protocol.stream = None
        self.protocol = protocol
        self.protocol.stream = self

    def accept(self, rfp, wfp):
        """
        Attach a pair of file objects to :attr:`receive_side` and
        :attr:`transmit_side`, after wrapping them in :class:`Side` instances.
        :class:`Side` will call :func:`set_nonblock` and :func:`set_cloexec`
        on the underlying file descriptors during construction.

        The same file object may be used for both sides. The default
        :meth:`on_disconnect` is handles the possibility that only one
        descriptor may need to be closed.

        :param file rfp:
            The file object to receive from.
        :param file wfp:
            The file object to transmit to.
        """
        self.receive_side = Side(self, rfp)
        self.transmit_side = Side(self, wfp)

    def __repr__(self):
        return "<Stream %s #%04x>" % (self.name, id(self) & 0xffff,)

    def on_receive(self, broker):
        """
        Invoked by :class:`Broker` when the stream's :attr:`receive_side` has
        been marked readable using :meth:`Broker.start_receive` and the broker
        has detected the associated file descriptor is ready for reading.

        Subclasses must implement this if they are registered using
        :meth:`Broker.start_receive`, and the method must invoke
        :meth:`on_disconnect` if reading produces an empty string.

        The default implementation reads :attr:`Protocol.read_size` bytes and
        passes the resulting bytestring to :meth:`Protocol.on_receive`. If the
        bytestring is 0 bytes, invokes :meth:`on_disconnect` instead.
        """
        buf = self.receive_side.read(self.protocol.read_size)
        if not buf:
            LOG.debug('%r: empty read, disconnecting', self.receive_side)
            return self.on_disconnect(broker)

        self.protocol.on_receive(broker, buf)

    def on_transmit(self, broker):
        """
        Invoked by :class:`Broker` when the stream's :attr:`transmit_side` has
        been marked writeable using :meth:`Broker._start_transmit` and the
        broker has detected the associated file descriptor is ready for
        writing.

        Subclasses must implement they are ever registerd with
        :meth:`Broker._start_transmit`.

        The default implementation invokes :meth:`Protocol.on_transmit`.
        """
        self.protocol.on_transmit(broker)

    def on_shutdown(self, broker):
        """
        Invoked by :meth:`Broker.shutdown` to allow the stream time to
        gracefully shutdown.

        The default implementation emits a ``shutdown`` signal before
        invoking :meth:`on_disconnect`.
        """
        fire(self, 'shutdown')
        self.protocol.on_shutdown(broker)

    def on_disconnect(self, broker):
        """
        Invoked by :class:`Broker` to force disconnect the stream during
        shutdown, invoked by the default :meth:`on_shutdown` implementation,
        and usually invoked by any subclass :meth:`on_receive` implementation
        in response to a 0-byte read.

        The base implementation fires a ``disconnect`` event, then closes
        :attr:`receive_side` and :attr:`transmit_side` after unregistering the
        stream from the broker.
        """
        fire(self, 'disconnect')
        self.protocol.on_disconnect(broker)


class Protocol:
    """
    Implement the program behaviour associated with activity on a
    :class:`Stream`. The protocol in use may vary over a stream's life, for
    example to allow :class:`mitogen.parent.BootstrapProtocol` to initialize
    the connected child before handing it off to :class:`MitogenProtocol`. A
    stream's active protocol is tracked in the :attr:`Stream.protocol`
    attribute, and modified via :meth:`Stream.set_protocol`.

    Protocols do not handle IO, they are entirely reliant on the interface
    provided by :class:`Stream` and :class:`Side`, allowing the underlying IO
    implementation to be replaced without modifying behavioural logic.
    """
    stream_class = Stream

    #: The :class:`Stream` this protocol is currently bound to, or
    #: :data:`None`.
    stream = None

    #: The size of the read buffer used by :class:`Stream` when this is the
    #: active protocol for the stream.
    read_size = CHUNK_SIZE

    @classmethod
    def build_stream(cls, *args, **kwargs):
        stream = cls.stream_class()
        stream.set_protocol(cls(*args, **kwargs))
        return stream

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            self.stream and self.stream.name,
        )

    def on_shutdown(self, broker):
        _v and LOG.debug('%r: shutting down', self)
        self.stream.on_disconnect(broker)

    def on_disconnect(self, broker):
        # Normally both sides an FD, so it is important that tranmit_side is
        # deregistered from Poller before closing the receive side, as pollers
        # like epoll and kqueue unregister all events on FD close, causing
        # subsequent attempt to unregister the transmit side to fail.
        LOG.debug('%r: disconnecting', self)
        broker.stop_receive(self.stream)
        if self.stream.transmit_side:
            broker._stop_transmit(self.stream)

        self.stream.receive_side.close()
        if self.stream.transmit_side:
            self.stream.transmit_side.close()


class DelimitedProtocol(Protocol):
    """
    Provide a :meth:`Protocol.on_receive` implementation for protocols that are
    delimited by a fixed string, like text based protocols. Each message is
    passed to :meth:`on_line_received` as it arrives, with incomplete messages
    passed to :meth:`on_partial_line_received`.

    When emulating user input it is often necessary to respond to incomplete
    lines, such as when a "Password: " prompt is sent.
    :meth:`on_partial_line_received` may be called repeatedly with an
    increasingly complete message. When a complete message is finally received,
    :meth:`on_line_received` will be called once for it before the buffer is
    discarded.

    If :func:`on_line_received` returns :data:`False`, remaining data is passed
    unprocessed to the stream's current protocol's :meth:`on_receive`. This
    allows switching from line-oriented to binary while the input buffer
    contains both kinds of data.
    """
    #: The delimiter. Defaults to newline.
    delimiter = b('\n')
    _trailer = b('')

    def on_receive(self, broker, buf):
        _vv and IOLOG.debug('%r.on_receive()', self)
        stream = self.stream
        self._trailer, cont = mitogen.core.iter_split(
            buf=self._trailer + buf,
            delim=self.delimiter,
            func=self.on_line_received,
        )

        if self._trailer:
            if cont:
                self.on_partial_line_received(self._trailer)
            else:
                assert stream.protocol is not self, \
                    'stream protocol is no longer %r' % (self,)
                stream.protocol.on_receive(broker, self._trailer)

    def on_line_received(self, line):
        """
        Receive a line from the stream.

        :param bytes line:
            The encoded line, excluding the delimiter.
        :returns:
            :data:`False` to indicate this invocation modified the stream's
            active protocol, and any remaining buffered data should be passed
            to the new protocol's :meth:`on_receive` method.

            Any other return value is ignored.
        """
        pass

    def on_partial_line_received(self, line):
        """
        Receive a trailing unterminated partial line from the stream.

        :param bytes line:
            The encoded partial line.
        """
        pass


class BufferedWriter:
    """
    Implement buffered output while avoiding quadratic string operations. This
    is currently constructed by each protocol, in future it may become fixed
    for each stream instead.
    """
    def __init__(self, broker, protocol):
        self._broker = broker
        self._protocol = protocol
        self._buf = collections.deque()
        self._len = 0

    def write(self, s):
        """
        Transmit `s` immediately, falling back to enqueuing it and marking the
        stream writeable if no OS buffer space is available.
        """
        if not self._len:
            # Modifying epoll/Kqueue state is expensive, as are needless broker
            # loops. Rather than wait for writeability, just write immediately,
            # and fall back to the broker loop on error or full buffer.
            try:
                n = self._protocol.stream.transmit_side.write(s)
                if n:
                    if n == len(s):
                        return
                    s = s[n:]
            except OSError:
                pass

            self._broker._start_transmit(self._protocol.stream)
        self._buf.append(s)
        self._len += len(s)

    def on_transmit(self, broker):
        """
        Respond to stream writeability by retrying previously buffered
        :meth:`write` calls.
        """
        if self._buf:
            buf = self._buf.popleft()
            written = self._protocol.stream.transmit_side.write(buf)
            if not written:
                _v and LOG.debug('disconnected during write to %r', self)
                self._protocol.stream.on_disconnect(broker)
                return
            elif written != len(buf):
                self._buf.appendleft(BufferType(buf, written))

            _vv and IOLOG.debug('transmitted %d bytes to %r', written, self)
            self._len -= written

        if not self._buf:
            broker._stop_transmit(self._protocol.stream)


class Side:
    """
    Represent one side of a :class:`Stream`. This allows unidirectional (e.g.
    pipe) and bidirectional (e.g. socket) streams to operate identically.

    Sides are also responsible for tracking the open/closed state of the
    underlying FD, preventing erroneous duplicate calls to :func:`os.close` due
    to duplicate :meth:`Stream.on_disconnect` calls, which would otherwise risk
    silently succeeding by closing an unrelated descriptor. For this reason, it
    is crucial only one file object exists per unique descriptor.

    :param mitogen.core.Stream stream:
        The stream this side is associated with.
    :param object fp:
        The file or socket object managing the underlying file descriptor. Any
        object may be used that supports `fileno()` and `close()` methods.
    :param bool cloexec:
        If :data:`True`, the descriptor has its :data:`fcntl.FD_CLOEXEC` flag
        enabled using :func:`fcntl.fcntl`.
    :param bool keep_alive:
        If :data:`True`, the continued existence of this side will extend the
        shutdown grace period until it has been unregistered from the broker.
    :param bool blocking:
        If :data:`False`, the descriptor has its :data:`os.O_NONBLOCK` flag
        enabled using :func:`fcntl.fcntl`.
    """
    _fork_refs = weakref.WeakValueDictionary()
    closed = False

    def __init__(self, stream, fp, cloexec=True, keep_alive=True, blocking=False):
        #: The :class:`Stream` for which this is a read or write side.
        self.stream = stream
        # File or socket object responsible for the lifetime of its underlying
        # file descriptor.
        self.fp = fp
        #: Integer file descriptor to perform IO on, or :data:`None` if
        #: :meth:`close` has been called. This is saved separately from the
        #: file object, since :meth:`file.fileno` cannot be called on it after
        #: it has been closed.
        self.fd = fp.fileno()
        #: If :data:`True`, causes presence of this side in
        #: :class:`Broker`'s active reader set to defer shutdown until the
        #: side is disconnected.
        self.keep_alive = keep_alive
        self._fork_refs[id(self)] = self
        if cloexec:
            set_cloexec(self.fd)
        if not blocking:
            set_nonblock(self.fd)

    def __repr__(self):
        return '<Side of %s fd %s>' % (
            self.stream.name or repr(self.stream),
            self.fd
        )

    @classmethod
    def _on_fork(cls):
        while cls._fork_refs:
            _, side = cls._fork_refs.popitem()
            _vv and IOLOG.debug('Side._on_fork() closing %r', side)
            side.close()

    def close(self):
        """
        Call :meth:`file.close` on :attr:`fp` if it is not :data:`None`,
        then set it to :data:`None`.
        """
        _vv and IOLOG.debug('%r.close()', self)
        if not self.closed:
            self.closed = True
            self.fp.close()

    def read(self, n=CHUNK_SIZE):
        """
        Read up to `n` bytes from the file descriptor, wrapping the underlying
        :func:`os.read` call with :func:`io_op` to trap common disconnection
        conditions.

        :meth:`read` always behaves as if it is reading from a regular UNIX
        file; socket, pipe, and TTY disconnection errors are masked and result
        in a 0-sized read like a regular file.

        :returns:
            Bytes read, or the empty string to indicate disconnection was
            detected.
        """
        if self.closed:
            # Refuse to touch the handle after closed, it may have been reused
            # by another thread. TODO: synchronize read()/write()/close().
            return b('')
        s, disconnected = io_op(os.read, self.fd, n)
        if disconnected:
            LOG.debug('%r: disconnected during read: %s', self, disconnected)
            return b('')
        return s

    def write(self, s):
        """
        Write as much of the bytes from `s` as possible to the file descriptor,
        wrapping the underlying :func:`os.write` call with :func:`io_op` to
        trap common disconnection conditions.

        :returns:
            Number of bytes written, or :data:`None` if disconnection was
            detected.
        """
        if self.closed:
            # Don't touch the handle after close, it may be reused elsewhere.
            return None

        written, disconnected = io_op(os.write, self.fd, s)
        if disconnected:
            LOG.debug('%r: disconnected during write: %s', self, disconnected)
            return None
        return written


class Poller:
    """
    A poller manages OS file descriptors the user is waiting to become
    available for IO. The :meth:`poll` method blocks the calling thread
    until one or more become ready.

    Each descriptor has an associated `data` element, which is unique for each
    readiness type, and defaults to being the same as the file descriptor. The
    :meth:`poll` method yields the data associated with a descriptor, rather
    than the descriptor itself, allowing concise loops like::

        p = Poller()
        p.start_receive(conn.fd, data=conn.on_read)
        p.start_transmit(conn.fd, data=conn.on_write)

        for callback in p.poll():
            callback()  # invoke appropriate bound instance method

    Pollers may be modified while :meth:`poll` is yielding results. Removals
    are processed immediately, causing pending events for the descriptor to be
    discarded.

    The :meth:`close` method must be called when a poller is discarded to avoid
    a resource leak.

    Pollers may only be used by one thread at a time.

    This implementation uses :func:`select.select` for wider platform support.
    That is considered an implementation detail. Previous versions have used
    :func:`select.poll`. Future versions may decide at runtime.
    """
    SUPPORTED = True

    #: Increments on every poll(). Used to version _rfds and _wfds.
    _generation = 1

    def __init__(self):
        self._rfds = {}
        self._wfds = {}

    def __repr__(self):
        return '%s' % (type(self).__name__,)

    def _update(self, fd):
        """
        Required by PollPoller subclass.
        """
        pass

    @property
    def readers(self):
        """
        Return a list of `(fd, data)` tuples for every FD registered for
        receive readiness.
        """
        return list((fd, data) for fd, (data, gen) in self._rfds.items())

    @property
    def writers(self):
        """
        Return a list of `(fd, data)` tuples for every FD registered for
        transmit readiness.
        """
        return list((fd, data) for fd, (data, gen) in self._wfds.items())

    def close(self):
        """
        Close any underlying OS resource used by the poller.
        """
        pass

    def start_receive(self, fd, data=None):
        """
        Cause :meth:`poll` to yield `data` when `fd` is readable.
        """
        self._rfds[fd] = (data or fd, self._generation)
        self._update(fd)

    def stop_receive(self, fd):
        """
        Stop yielding readability events for `fd`.

        Redundant calls to :meth:`stop_receive` are silently ignored, this may
        change in future.
        """
        self._rfds.pop(fd, None)
        self._update(fd)

    def start_transmit(self, fd, data=None):
        """
        Cause :meth:`poll` to yield `data` when `fd` is writeable.
        """
        self._wfds[fd] = (data or fd, self._generation)
        self._update(fd)

    def stop_transmit(self, fd):
        """
        Stop yielding writeability events for `fd`.

        Redundant calls to :meth:`stop_transmit` are silently ignored, this may
        change in future.
        """
        self._wfds.pop(fd, None)
        self._update(fd)

    def _poll(self, timeout):
        (rfds, wfds, _), _ = io_op(select.select,
                                   self._rfds,
                                   self._wfds,
                                   (), timeout
                                   )

        for fd in rfds:
            _vv and IOLOG.debug('%r: POLLIN for %r', self, fd)
            data, gen = self._rfds.get(fd, (None, None))
            if gen and gen < self._generation:
                yield data

        for fd in wfds:
            _vv and IOLOG.debug('%r: POLLOUT for %r', self, fd)
            data, gen = self._wfds.get(fd, (None, None))
            if gen and gen < self._generation:
                yield data

    def poll(self, timeout=None):
        """
        Block the calling thread until one or more FDs are ready for IO.

        :param float timeout:
            If not :data:`None`, seconds to wait without an event before
            returning an empty iterable.
        :returns:
            Iterable of `data` elements associated with ready FDs.
        """
        _vv and IOLOG.debug('%r.poll(%r)', self, timeout)
        self._generation += 1
        return self._poll(timeout)


class Broker:
    """
    Responsible for handling I/O multiplexing in a private thread.

    **Note:** This somewhat limited core version is used by children. The
    master subclass is documented below.
    """
    poller_class = Poller
    _waker = None
    _thread = None

    # :func:`mitogen.parent._upgrade_broker` replaces this with
    # :class:`mitogen.parent.TimerList` during upgrade.
    timers = NullTimerList()

    #: Seconds grace to allow :class:`streams <Stream>` to shutdown gracefully
    #: before force-disconnecting them during :meth:`shutdown`.
    shutdown_timeout = 3.0

    def __init__(self, poller_class=None, activate_compat=True):
        self._alive = True
        self._exitted = False
        self._waker = Waker.build_stream(self)
        #: Arrange for `func(\*args, \**kwargs)` to be executed on the broker
        #: thread, or immediately if the current thread is the broker thread.
        #: Safe to call from any thread.
        self.defer = self._waker.protocol.defer
        self.poller = self.poller_class()
        self.poller.start_receive(
            self._waker.receive_side.fd,
            (self._waker.receive_side, self._waker.on_receive)
        )
        self._thread = threading.Thread(
            target=self._broker_main,
            name='mitogen.broker'
        )
        self._thread.start()
        if activate_compat:
            self._py24_25_compat()

    def _py24_25_compat(self):
        """
        Python 2.4/2.5 have grave difficulties with threads/fork. We
        mandatorily quiesce all running threads during fork using a
        monkey-patch there.
        """
        if sys.version_info < (2, 6):
            # import_module() is used to avoid dep scanner.
            os_fork = import_module('mitogen.os_fork')
            os_fork._notice_broker_or_pool(self)

    def start_receive(self, stream):
        """
        Mark the :attr:`receive_side <Stream.receive_side>` on `stream` as
        ready for reading. Safe to call from any thread. When the associated
        file descriptor becomes ready for reading,
        :meth:`BasicStream.on_receive` will be called.
        """
        _vv and IOLOG.debug('%r.start_receive(%r)', self, stream)
        side = stream.receive_side
        assert side and not side.closed
        self.defer(self.poller.start_receive,
                   side.fd, (side, stream.on_receive))

    def stop_receive(self, stream):
        """
        Mark the :attr:`receive_side <Stream.receive_side>` on `stream` as not
        ready for reading. Safe to call from any thread.
        """
        _vv and IOLOG.debug('%r.stop_receive(%r)', self, stream)
        self.defer(self.poller.stop_receive, stream.receive_side.fd)

    def _start_transmit(self, stream):
        """
        Mark the :attr:`transmit_side <Stream.transmit_side>` on `stream` as
        ready for writing. Must only be called from the Broker thread. When the
        associated file descriptor becomes ready for writing,
        :meth:`BasicStream.on_transmit` will be called.
        """
        _vv and IOLOG.debug('%r._start_transmit(%r)', self, stream)
        side = stream.transmit_side
        assert side and not side.closed
        self.poller.start_transmit(side.fd, (side, stream.on_transmit))

    def _stop_transmit(self, stream):
        """
        Mark the :attr:`transmit_side <Stream.receive_side>` on `stream` as not
        ready for writing.
        """
        _vv and IOLOG.debug('%r._stop_transmit(%r)', self, stream)
        self.poller.stop_transmit(stream.transmit_side.fd)

    def keep_alive(self):
        """
        Return :data:`True` if any reader's :attr:`Side.keep_alive` attribute
        is :data:`True`, or any :class:`Context` is still registered that is
        not the master. Used to delay shutdown while some important work is in
        progress (e.g. log draining).
        """
        it = (side.keep_alive for (_, (side, _)) in self.poller.readers)
        return sum(it, 0) > 0 or self.timers.get_timeout() is not None

    def defer_sync(self, func):
        """
        Arrange for `func()` to execute on :class:`Broker` thread, blocking the
        current thread until a result or exception is available.

        :returns:
            Return value of `func()`.
        """
        latch = Latch()
        def wrapper():
            try:
                latch.put(func())
            except Exception:
                latch.put(sys.exc_info()[1])
        self.defer(wrapper)
        res = latch.get()
        if isinstance(res, Exception):
            raise res
        return res

    def _call(self, stream, func):
        """
        Call `func(self)`, catching any exception that might occur, logging it,
        and force-disconnecting the related `stream`.
        """
        try:
            func(self)
        except Exception:
            LOG.exception('%r crashed', stream)
            stream.on_disconnect(self)

    def _loop_once(self, timeout=None):
        """
        Execute a single :class:`Poller` wait, dispatching any IO events that
        caused the wait to complete.

        :param float timeout:
            If not :data:`None`, maximum time in seconds to wait for events.
        """
        _vv and IOLOG.debug('%r._loop_once(%r, %r)',
                            self, timeout, self.poller)

        timer_to = self.timers.get_timeout()
        if timeout is None:
            timeout = timer_to
        elif timer_to is not None and timer_to < timeout:
            timeout = timer_to

        #IOLOG.debug('readers =\n%s', pformat(self.poller.readers))
        #IOLOG.debug('writers =\n%s', pformat(self.poller.writers))
        for side, func in self.poller.poll(timeout):
            self._call(side.stream, func)
        if timer_to is not None:
            self.timers.expire()

    def _broker_exit(self):
        """
        Forcefully call :meth:`Stream.on_disconnect` on any streams that failed
        to shut down gracefully, then discard the :class:`Poller`.
        """
        for _, (side, _) in self.poller.readers + self.poller.writers:
            LOG.debug('%r: force disconnecting %r', self, side)
            side.stream.on_disconnect(self)

        self.poller.close()

    def _broker_shutdown(self):
        """
        Invoke :meth:`Stream.on_shutdown` for every active stream, then allow
        up to :attr:`shutdown_timeout` seconds for the streams to unregister
        themselves, logging an error if any did not unregister during the grace
        period.
        """
        for _, (side, _) in self.poller.readers + self.poller.writers:
            self._call(side.stream, side.stream.on_shutdown)

        deadline = now() + self.shutdown_timeout
        while self.keep_alive() and now() < deadline:
            self._loop_once(max(0, deadline - now()))

        if self.keep_alive():
            LOG.error('%r: pending work still existed %d seconds after '
                      'shutdown began. This may be due to a timer that is yet '
                      'to expire, or a child connection that did not fully '
                      'shut down.', self, self.shutdown_timeout)

    def _do_broker_main(self):
        """
        Broker thread main function. Dispatches IO events until
        :meth:`shutdown` is called.
        """
        # For Python 2.4, no way to retrieve ident except on thread.
        self._waker.protocol.broker_ident = thread.get_ident()
        try:
            while self._alive:
                self._loop_once()

            fire(self, 'before_shutdown')
            fire(self, 'shutdown')
            self._broker_shutdown()
        except Exception:
            e = sys.exc_info()[1]
            LOG.exception('broker crashed')
            syslog.syslog(syslog.LOG_ERR, 'broker crashed: %s' % (e,))
            syslog.closelog()  # prevent test 'fd leak'.

        self._alive = False  # Ensure _alive is consistent on crash.
        self._exitted = True
        self._broker_exit()

    def _broker_main(self):
        try:
            _profile_hook('mitogen.broker', self._do_broker_main)
        finally:
            # 'finally' to ensure _on_broker_exit() can always SIGTERM.
            fire(self, 'exit')

    def shutdown(self):
        """
        Request broker gracefully disconnect streams and stop. Safe to call
        from any thread.
        """
        _v and LOG.debug('%r: shutting down', self)
        def _shutdown():
            self._alive = False
        if self._alive and not self._exitted:
            self.defer(_shutdown)

    def join(self):
        """
        Wait for the broker to stop, expected to be called after
        :meth:`shutdown`.
        """
        self._thread.join()

    def __repr__(self):
        return 'Broker(%04x)' % (id(self) & 0xffff,)
