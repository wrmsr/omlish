import queue
import threading
import typing as ta

from .. import check


class Firehose:

    def __init__(self, shutdown_event: ta.Optional[threading.Event] = None) -> None:
        super().__init__()

        if shutdown_event is None:
            shutdown_event = threading.Event()
        self._shutdown_event = check.isinstance(shutdown_event, threading.Event)

        self._lock = threading.Lock()
        self._lock_queue_pairs: ta.List[threading.Lock, queue.Queue] = []
        self._num_rejections = 0

    def publish(self, obj):
        for _, q in list(self._lock_queue_pairs):
            try:
                q.put(obj, block=False)
            except queue.Full:
                self._num_rejections += 1

    def stream(self):
        lock = threading.Lock()
        q = queue.Queue(100)
        lock.acquire()

        with self._lock:
            self._lock_queue_pairs.append((lock, q))

        try:
            while not self._shutdown_event.is_set():
                try:
                    payload = q.get(block=True, timeout=1)
                except queue.Empty:
                    yield b'{}\n'
                else:
                    yield payload

        finally:
            with self._lock:
                self._lock_queue_pairs = [(l, q) for l, q in self._lock_queue_pairs if l is not lock]
