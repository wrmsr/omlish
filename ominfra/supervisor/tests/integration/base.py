# ruff: noqa: PT009 SLF001 UP006 UP007 UP045
"""Base test harness for supervisor integration tests."""
import contextlib
import os
import os.path
import shutil
import signal
import tempfile
import threading
import time
import typing as ta
import unittest

from omlish.lite.inject import inj
from omlish.lite.marshal import unmarshal_obj

from ...configs import ServerConfig
from ...configs import prepare_server_config
from ...events import Event
from ...events import EventCallbacks
from ...groups import ProcessGroupManager
from ...inject import bind_server
from ...states import ProcessState
from ...supervisor import Supervisor
from ...types import ExitNow
from ...types import Process
from ...utils.ostypes import Pid


##


PROGRAMS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'programs')


def get_program_path(name: str) -> str:
    """Get absolute path to a test program."""
    return os.path.join(PROGRAMS_DIR, name)


##


class SupervisorTestBase(unittest.TestCase):
    """Base class for supervisor integration tests with no mocks."""

    def setUp(self) -> None:
        super().setUp()

        self._events: ta.List[Event] = []
        self._temp_dirs: ta.List[str] = []

    def tearDown(self) -> None:
        super().tearDown()

        # Clean up temp directories
        for d in self._temp_dirs:
            if os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)

    #

    def make_temp_dir(self) -> str:
        """Create a temporary directory that will be cleaned up."""
        d = tempfile.mkdtemp(prefix='supervisor_test_')
        self._temp_dirs.append(d)
        return d

    #

    def make_config(
            self,
            config_dict: ta.Mapping[str, ta.Any],
            *,
            nodaemon: bool = True,
            **kwargs: ta.Any,
    ) -> ServerConfig:
        """
        Build ServerConfig from dict with sensible test defaults.

        Example:
            config = self.make_config({
                'groups': {
                    'test': {
                        'processes': {
                            'sleep': {'command': 'sleep 10'}
                        }
                    }
                }
            })
        """

        merged = {
            'nodaemon': nodaemon,
            'silent': True,
            'nocleanup': True,
            **config_dict,
            **kwargs,
        }

        prepared = prepare_server_config(merged)

        # return ServerConfig(**prepared)

        return unmarshal_obj(prepared, ServerConfig)

    #

    def _event_callback(self, event: Event) -> None:
        """Internal event callback that captures all events."""
        self._events.append(event)

    @contextlib.contextmanager
    def run_supervisor(
            self,
            config: ServerConfig,
            *,
            max_iterations: ta.Optional[int] = None,
            timeout: ta.Optional[float] = None,
    ) -> ta.Iterator[Supervisor]:
        """
        Run supervisor in a controlled environment.

        The supervisor runs in the main thread but with iteration control.
        Yields supervisor instance for inspection and control.

        Args:
            config: Server configuration
            max_iterations: Maximum number of event loop iterations (None = infinite)
            timeout: Maximum wall-clock time to run (None = infinite)

        Yields:
            Supervisor instance
        """
        self._events.clear()

        with contextlib.ExitStack() as es:
            injector = inj.create_injector(bind_server(es, config))

            # Register our event callback
            event_callbacks = injector[EventCallbacks]
            event_callbacks.subscribe(Event, self._event_callback)

            supervisor = injector[Supervisor]

            # Track iteration and timing
            iteration = [0]
            start_time = [time.time()]
            should_stop = [False]

            def callback(sup: Supervisor) -> bool:
                iteration[0] += 1

                # Check iteration limit
                if max_iterations is not None and iteration[0] >= max_iterations:
                    should_stop[0] = True
                    return False

                # Check timeout
                if timeout is not None and (time.time() - start_time[0]) >= timeout:
                    should_stop[0] = True
                    return False

                # Check external stop
                if should_stop[0]:
                    return False

                return True

            # Expose stop mechanism
            supervisor._test_should_stop = should_stop  # type: ignore

            # Run in background thread so we can yield control

            exc_holder: ta.List[ta.Optional[BaseException]] = [None]

            def run_thread():
                try:
                    supervisor.run(callback=callback)
                except ExitNow:
                    pass
                except BaseException as e:  # noqa
                    exc_holder[0] = e

            thread = threading.Thread(target=run_thread, daemon=True)
            thread.start()

            # Give supervisor a moment to start
            time.sleep(0.1)

            try:
                yield supervisor

            finally:
                # Signal stop
                should_stop[0] = True

                # Wait for supervisor to stop
                thread.join(timeout=5.0)

                if thread.is_alive():
                    # Force cleanup - kill all child processes
                    self._cleanup_processes(supervisor)

                # Re-raise any exception from supervisor thread
                if exc_holder[0] is not None:
                    raise exc_holder[0]

    def _cleanup_processes(self, supervisor: Supervisor) -> None:
        """Force cleanup of all supervisor child processes."""

        try:
            groups = supervisor._process_groups
            if isinstance(groups, ProcessGroupManager):
                for proc in groups.all_processes():
                    if proc.pid:
                        try:
                            os.kill(proc.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
        except Exception:  # noqa
            pass

    #

    def get_process(self, supervisor: Supervisor, name: str) -> ta.Optional[Process]:
        """Get a process by name (format: 'group:process' or 'process')."""

        groups = supervisor._process_groups

        if ':' in name:
            group_name, proc_name = name.split(':', 1)
            group = groups.get(group_name)
            if group is None:
                return None
            return group.get(proc_name)

        else:
            # Search all groups
            for group in groups:
                proc = group.get(name)
                if proc is not None:
                    return proc
            return None

    def wait_for_process_state(
            self,
            supervisor: Supervisor,
            name: str,
            state: ProcessState,
            timeout: float = 5.0,
    ) -> Process:
        """
        Wait for named process to reach state or raise timeout.

        Args:
            supervisor: Supervisor instance
            name: Process name (group:name or just name)
            state: Expected state
            timeout: Maximum time to wait

        Returns:
            Process instance

        Raises:
            AssertionError: If timeout or process not found
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            proc = self.get_process(supervisor, name)

            if proc is None:
                time.sleep(0.1)
                continue

            if proc.state == state:
                return proc

            time.sleep(0.1)

        # Timeout
        proc = self.get_process(supervisor, name)
        if proc is None:
            self.fail(f'Process {name} not found after {timeout}s')
        else:
            self.fail(
                f'Process {name} did not reach state {state.name} within {timeout}s '
                f'(current state: {proc.state.name})',
            )
        raise RuntimeError  # noqa

    def wait_for_event_type(
            self,
            event_type: ta.Type[Event],
            timeout: float = 5.0,
            since_index: int = 0,
    ) -> Event:
        """
        Wait for an event of specific type to occur.

        Args:
            event_type: Event class to wait for
            timeout: Maximum time to wait
            since_index: Only check events after this index

        Returns:
            The event instance

        Raises:
            AssertionError: If timeout
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            for _i, event in enumerate(self._events[since_index:], start=since_index):
                if isinstance(event, event_type):
                    return event

            time.sleep(0.05)

        self.fail(f'Event {event_type.__name__} did not occur within {timeout}s')
        raise RuntimeError  # noqa

    def wait_for_event_sequence(
            self,
            expected_types: ta.Sequence[ta.Type[Event]],
            timeout: float = 5.0,
    ) -> ta.List[Event]:
        """
        Wait for a sequence of event types to occur in order.

        Args:
            expected_types: Sequence of event types
            timeout: Maximum time to wait

        Returns:
            List of matching events

        Raises:
            AssertionError: If timeout or sequence doesn't match
        """
        deadline = time.time() + timeout
        matches: ta.List[Event] = []
        search_idx = 0

        while time.time() < deadline and len(matches) < len(expected_types):
            expected_type = expected_types[len(matches)]

            for event in self._events[search_idx:]:
                search_idx += 1
                if isinstance(event, expected_type):
                    matches.append(event)
                    break

            if len(matches) < len(expected_types):
                time.sleep(0.05)

        if len(matches) != len(expected_types):
            found_types = [type(e).__name__ for e in matches]
            expected_names = [t.__name__ for t in expected_types]
            self.fail(
                f'Event sequence incomplete after {timeout}s: '
                f'expected {expected_names}, got {found_types}',
            )

        return matches

    #

    def assert_process_alive(self, pid: Pid) -> None:
        """Assert process with PID is alive."""
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            self.fail(f'Process {pid} is not alive')
        except PermissionError:
            # Process exists but we don't own it
            pass

    def assert_process_dead(self, pid: Pid, timeout: float = 1.0) -> None:
        """Assert process with PID is dead (with optional wait)."""
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                os.kill(pid, 0)
                time.sleep(0.1)
            except ProcessLookupError:
                return  # Dead!

        self.fail(f'Process {pid} is still alive after {timeout}s')

    def wait_until(
            self,
            condition: ta.Callable[[], bool],
            timeout: float = 5.0,
            interval: float = 0.1,
            message: ta.Optional[str] = None,
    ) -> None:
        """
        Poll until condition is true or timeout.

        Args:
            condition: Callable that returns bool
            timeout: Maximum time to wait
            interval: Polling interval
            message: Custom failure message
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            if condition():
                return

            time.sleep(interval)

        self.fail(message or f'Condition not met within {timeout}s')
