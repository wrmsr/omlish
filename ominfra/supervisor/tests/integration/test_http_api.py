# ruff: noqa: PT009 UP006 UP007 UP045
"""Integration tests for HTTP API."""
import http.client
import json
import sys
import time

from ...states import ProcessState
from .base import SupervisorTestBase


class TestHttpApi(SupervisorTestBase):
    """Test HTTP status and control API."""

    def test_http_server_starts(self):
        """HTTP server should start and be accessible."""

        config = self.make_config({
            'http_port': 19001,  # Use non-standard port to avoid conflicts
            'groups': {
                'test': {
                    'processes': {
                        'dummy': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process to start
            self.wait_for_process_state(sup, 'dummy', ProcessState.RUNNING, timeout=5.0)

            # Give HTTP server a moment to be ready
            time.sleep(0.5)

            # Try to connect to HTTP server
            conn = http.client.HTTPConnection('localhost', 19001, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()

                # Should get a response
                self.assertEqual(resp.status, 200)

                # Should be JSON
                content_type = resp.getheader('Content-Type')
                assert content_type is not None
                self.assertIn('json', content_type.lower())

                # Read and parse body
                body = resp.read()
                data = json.loads(body)

                # Should have structure
                self.assertIn('groups', data)
                self.assertIn('method', data)
                self.assertIn('path', data)

            finally:
                conn.close()

    def test_http_shows_process_state(self):
        """HTTP API should show current process states."""

        config = self.make_config({
            'http_port': 19002,
            'groups': {
                'workers': {
                    'processes': {
                        'worker1': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                        'worker2': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for processes to start
            proc1 = self.wait_for_process_state(sup, 'worker1', ProcessState.RUNNING, timeout=5.0)
            proc2 = self.wait_for_process_state(sup, 'worker2', ProcessState.RUNNING, timeout=5.0)

            time.sleep(0.5)

            # Query HTTP API
            conn = http.client.HTTPConnection('localhost', 19002, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()
                body = resp.read()
                data = json.loads(body)

                # Check structure
                self.assertIn('groups', data)
                self.assertIn('workers', data['groups'])

                workers_group = data['groups']['workers']
                self.assertIn('processes', workers_group)

                processes = workers_group['processes']
                self.assertIn('worker1', processes)
                self.assertIn('worker2', processes)

                # Check process details
                worker1_info = processes['worker1']
                self.assertEqual(worker1_info['state'], 'RUNNING')
                self.assertEqual(worker1_info['pid'], proc1.pid)

                worker2_info = processes['worker2']
                self.assertEqual(worker2_info['state'], 'RUNNING')
                self.assertEqual(worker2_info['pid'], proc2.pid)

            finally:
                conn.close()

    def test_http_shows_state_transitions(self):
        """HTTP API should reflect real-time state changes."""

        config = self.make_config({
            'http_port': 19003,
            'groups': {
                'test': {
                    'processes': {
                        'transient': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.immediate_exit 0 2',
                            'auto_start': True,
                            'start_secs': 1,
                            'auto_restart': False,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for RUNNING
            self.wait_for_process_state(sup, 'transient', ProcessState.RUNNING, timeout=5.0)

            # Query while running
            conn = http.client.HTTPConnection('localhost', 19003, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()
                data = json.loads(resp.read())

                proc_info = data['groups']['test']['processes']['transient']
                self.assertEqual(proc_info['state'], 'RUNNING')
                self.assertGreater(proc_info['pid'], 0)

            finally:
                conn.close()

            # Wait for process to exit
            self.wait_for_process_state(sup, 'transient', ProcessState.EXITED, timeout=5.0)

            # Query after exited
            conn = http.client.HTTPConnection('localhost', 19003, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()
                data = json.loads(resp.read())

                proc_info = data['groups']['test']['processes']['transient']
                self.assertEqual(proc_info['state'], 'EXITED')
                self.assertEqual(proc_info['pid'], 0)  # No PID when not running

            finally:
                conn.close()

    def test_http_concurrent_connections(self):
        """HTTP server should handle concurrent connections."""

        config = self.make_config({
            'http_port': 19004,
            'groups': {
                'test': {
                    'processes': {
                        'stable': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.long_runner 10',
                            'auto_start': True,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=10.0) as sup:
            # Wait for process
            self.wait_for_process_state(sup, 'stable', ProcessState.RUNNING, timeout=5.0)

            time.sleep(0.5)

            # Make multiple concurrent requests
            responses = []
            for _ in range(5):
                conn = http.client.HTTPConnection('localhost', 19004, timeout=5)
                try:
                    conn.request('GET', '/')
                    resp = conn.getresponse()
                    responses.append(resp.status)
                    resp.read()  # Consume body
                finally:
                    conn.close()

            # All should succeed
            self.assertEqual(responses, [200] * 5)

    def test_http_survives_process_crash(self):
        """HTTP server should continue working even if processes crash."""

        config = self.make_config({
            'http_port': 19005,
            'groups': {
                'test': {
                    'processes': {
                        'crasher': {
                            'command': f'{sys.executable} -m ominfra.supervisor.tests.programs.rapid_crasher 1 1',
                            'auto_start': True,
                            'start_retries': 2,
                        },
                    },
                },
            },
        })

        with self.run_supervisor(config, timeout=15.0) as sup:  # noqa
            # Wait for process to run and crash
            time.sleep(3.0)

            # HTTP should still work
            conn = http.client.HTTPConnection('localhost', 19005, timeout=5)
            try:
                conn.request('GET', '/')
                resp = conn.getresponse()

                # Should succeed
                self.assertEqual(resp.status, 200)

                data = json.loads(resp.read())
                self.assertIn('groups', data)

            finally:
                conn.close()
