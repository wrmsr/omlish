"""
abc:
  _eventloop:
   - AsyncBackend

  _resources:
   - AsyncResource

  _sockets:
   - ConnectedUDPSocket
   - ConnectedUNIXDatagramSocket
   - IPAddressType
   - IPSockAddrType
   - SocketAttribute
   - SocketListener
   - SocketStream
   - UDPPacketType
   - UDPSocket
   - UNIXDatagramPacketType
   - UNIXDatagramSocket
   - UNIXSocketStream
   - AnyByteReceiveStream
   - AnyByteSendStream
   - AnyByteStream
   - AnyUnreliableByteReceiveStream
   - AnyUnreliableByteSendStream
   - AnyUnreliableByteStream
   - ByteReceiveStream
   - ByteSendStream
   - ByteStream
   - Listener
   - ObjectReceiveStream
   - ObjectSendStream
   - ObjectStream
   - UnreliableObjectReceiveStream
   - UnreliableObjectSendStream
   - UnreliableObjectStream

  _subprocesses:
   - Process

  _tasks:
   - TaskGroup
   - TaskStatus

  _testing:
   - TestRunner

  eventloop:
   - current_time
   - get_all_backends
   - get_cancelled_exc_class
   - run
   - sleep
   - sleep_forever
   - sleep_until

exceptions:
 - BrokenResourceError
 - BrokenWorkerInterpreter
 - BrokenWorkerProcess
 - BusyResourceError
 - ClosedResourceError
 - DelimiterNotFound
 - EndOfStream
 - IncompleteRead
 - TypedAttributeLookupError
 - WouldBlock

fileio:
 - AsyncFile
 - Path
 - open_file
 - wrap_file

resources:
 - aclose_forcefully

signals:
 - open_signal_receiver

sockets:
 - connect_tcp
 - connect_unix
 - create_connected_udp_socket
 - create_connected_unix_datagram_socket
 - create_tcp_listener
 - create_udp_socket
 - create_unix_datagram_socket
 - create_unix_listener
 - getaddrinfo
 - getnameinfo
 - wait_readable
 - wait_socket_readable
 - wait_socket_writable
 - wait_writable

streams:
 - create_memory_object_stream

subprocesses:
 - open_process
 - run_process

synchronization:
 - CapacityLimiter
 - CapacityLimiterStatistics
 - Condition
 - ConditionStatistics
 - Event
 - EventStatistics
 - Lock
 - LockStatistics
 - ResourceGuard
 - Semaphore
 - SemaphoreStatistics

tasks:
 - TASK_STATUS_IGNORED
 - CancelScope
 - create_task_group
 - current_effective_deadline
 - fail_after
 - move_on_after

tempfile:
 - NamedTemporaryFile
 - SpooledTemporaryFile
 - TemporaryDirectory
 - TemporaryFile
 - gettempdir
 - gettempdirb
 - mkdtemp
 - mkstemp

testing:
 - TaskInfo
 - get_current_task
 - get_running_tasks
 - wait_all_tasks_blocked

typedattr:
 - TypedAttributeProvider
 - TypedAttributeSet
 - typed_attribute
"""
