import errno
import functools
import os
import shlex
import signal
import sys
import time
import traceback

from . import events
from .compat import as_bytes
from .compat import as_string
from .compat import compact_traceback
from .compat import decode_wait_status
from .compat import signame
from .datatypes import RestartUnconditionally
from .dispatchers import EventListenerStates
from .options import BadCommand
from .options import ProcessException
from .states import ProcessStates
from .states import STOPPED_STATES
from .states import SupervisorStates
from .states import get_process_state_description


@functools.total_ordering
class Subprocess:
    """A class to manage a subprocess."""

    # Initial state; overridden by instance variables

    pid = 0  # Subprocess pid; 0 when not running
    config = None  # ProcessConfig instance
    state = None  # process state code
    listener_state = None  # listener state code (if we're an event listener)
    event = None  # event currently being processed (if we're an event listener)
    laststart = 0  # Last time the subprocess was started; 0 if never
    laststop = 0  # Last time the subprocess was stopped; 0 if never
    last_stop_report = 0  # Last time "waiting for x to stop" logged, to throttle
    delay = 0  # If nonzero, delay starting or killing until this time
    administrative_stop = False  # true if process has been stopped by an admin
    system_stop = False  # true if process has been stopped by the system
    killing = False  # true if we are trying to kill this process
    backoff = 0  # backoff counter (to startretries)
    dispatchers = None  # asyncore output dispatchers (keyed by fd)
    pipes = None  # map of channel name to file descriptor #
    exitstatus = None  # status attached to dead process by finish()
    spawn_err = None  # error message attached by spawn() if any
    group = None  # ProcessGroup instance if process is in the group

    def __init__(self, config):
        """Constructor.

        Argument is a ProcessConfig instance.
        """
        self.config = config
        self.dispatchers = {}
        self.pipes = {}
        self.state = ProcessStates.STOPPED

    def remove_logs(self):
        for dispatcher in self.dispatchers.values():
            if hasattr(dispatcher, 'remove_logs'):
                dispatcher.remove_logs()

    def reopen_logs(self):
        for dispatcher in self.dispatchers.values():
            if hasattr(dispatcher, 'reopen_logs'):
                dispatcher.reopen_logs()

    def drain(self):
        for dispatcher in self.dispatchers.values():
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if dispatcher.readable():
                dispatcher.handle_read_event()
            if dispatcher.writable():
                dispatcher.handle_write_event()

    def write(self, chars):
        if not self.pid or self.killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self.pipes['stdin']
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = self.dispatchers[stdin_fd]
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.input_buffer += chars
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    def get_execv_args(self):
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessException if not
        """
        try:
            commandargs = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommand("can't parse command %r: %s" % (self.config.command, str(e)))

        if commandargs:
            program = commandargs[0]
        else:
            raise BadCommand('command is empty')

        if '/' in program:
            filename = program
            try:
                st = os.stat(filename)
            except OSError:
                st = None

        else:
            path = self.config.get_path()
            found = None
            st = None
            for dir in path:
                found = os.path.join(dir, program)
                try:
                    st = os.stat(found)
                except OSError:
                    pass
                else:
                    break
            if st is None:
                filename = program
            else:
                filename = found

        # check_execv_args will raise a ProcessException if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        self.config.options.check_execv_args(filename, commandargs, st)

        return filename, commandargs

    event_map = {
        ProcessStates.BACKOFF: events.ProcessStateBackoffEvent,
        ProcessStates.FATAL: events.ProcessStateFatalEvent,
        ProcessStates.UNKNOWN: events.ProcessStateUnknownEvent,
        ProcessStates.STOPPED: events.ProcessStateStoppedEvent,
        ProcessStates.EXITED: events.ProcessStateExitedEvent,
        ProcessStates.RUNNING: events.ProcessStateRunningEvent,
        ProcessStates.STARTING: events.ProcessStateStartingEvent,
        ProcessStates.STOPPING: events.ProcessStateStoppingEvent,
    }

    def change_state(self, new_state, expected=True):
        old_state = self.state
        if new_state is old_state:
            # exists for unit tests
            return False

        self.state = new_state
        if new_state == ProcessStates.BACKOFF:
            now = time.time()
            self.backoff += 1
            self.delay = now + self.backoff

        event_class = self.event_map.get(new_state)
        if event_class is not None:
            event = event_class(self, old_state, expected)
            events.notify(event)

    def _check_in_state(self, *states):
        if self.state not in states:
            current_state = get_process_state_description(self.state)
            allowable_states = ' '.join(map(get_process_state_description, states))
            processname = as_string(self.config.name)
            raise AssertionError('Assertion failed for %s: %s not in %s' % (processname, current_state, allowable_states))  # noqa

    def record_spawn_err(self, msg):
        self.spawn_err = msg
        self.config.options.logger.info('spawn_err: %s' % msg)

    def spawn(self):
        """
        Start the subprocess.  It must not be running already.

        Return the process id.  If the fork() call fails, return None.
        """
        options = self.config.options
        processname = as_string(self.config.name)

        if self.pid:
            msg = 'process \'%s\' already running' % processname
            options.logger.warn(msg)
            return None

        self.killing = False
        self.spawn_err = None
        self.exitstatus = None
        self.system_stop = False
        self.administrative_stop = False

        self.laststart = time.time()

        self._check_in_state(
            ProcessStates.EXITED,
            ProcessStates.FATAL,
            ProcessStates.BACKOFF,
            ProcessStates.STOPPED,
        )

        self.change_state(ProcessStates.STARTING)

        try:
            filename, argv = self.get_execv_args()
        except ProcessException as what:
            self.record_spawn_err(what.args[0])
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            return None

        try:
            self.dispatchers, self.pipes = self.config.make_dispatchers(self)
        except OSError as why:
            code = why.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = 'too many open files to spawn \'%s\'' % processname
            else:
                msg = 'unknown error making dispatchers for \'%s\': %s' % (processname, errno.errorcode.get(code, code))
            self.record_spawn_err(msg)
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            return None

        try:
            pid = os.fork()
        except OSError as why:
            code = why.args[0]
            if code == errno.EAGAIN:
                # process table full
                msg = ('Too many processes in process table to spawn \'%s\'' % processname)
            else:
                msg = 'unknown error during fork for \'%s\': %s' % (processname, errno.errorcode.get(code, code))
            self.record_spawn_err(msg)
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            options.close_parent_pipes(self.pipes)
            options.close_child_pipes(self.pipes)
            return None

        if pid != 0:
            return self._spawn_as_parent(pid)

        else:
            return self._spawn_as_child(filename, argv)

    def _spawn_as_parent(self, pid):
        # Parent
        self.pid = pid
        options = self.config.options
        options.close_child_pipes(self.pipes)
        options.logger.info('spawned: \'%s\' with pid %s' % (as_string(self.config.name), pid))
        self.spawn_err = None
        self.delay = time.time() + self.config.startsecs
        options.pid_history[pid] = self
        return pid

    def _prepare_child_fds(self):
        options = self.config.options
        os.dup2(self.pipes['child_stdin'], 0)
        os.dup2(self.pipes['child_stdout'], 1)
        if self.config.redirect_stderr:
            os.dup2(self.pipes['child_stdout'], 2)
        else:
            os.dup2(self.pipes['child_stderr'], 2)
        for i in range(3, options.minfds):
            options.close_fd(i)

    def _spawn_as_child(self, filename, argv):
        options = self.config.options
        try:
            # prevent child from receiving signals sent to the parent by calling os.setpgrp to create a new process
            # group for the child; this prevents, for instance, the case of child processes being sent a SIGINT when
            # running supervisor in foreground mode and Ctrl-C in the terminal window running supervisord is pressed.
            # Presumably it also prevents HUP, etc received by supervisord from being sent to children.
            os.setpgrp()

            self._prepare_child_fds()
            # sending to fd 2 will put this output in the stderr log

            # set user
            setuid_msg = self.set_uid()
            if setuid_msg:
                uid = self.config.uid
                msg = "couldn't setuid to %s: %s\n" % (uid, setuid_msg)
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set environment
            env = os.environ.copy()
            env['SUPERVISOR_ENABLED'] = '1'
            env['SUPERVISOR_PROCESS_NAME'] = self.config.name
            if self.group:
                env['SUPERVISOR_GROUP_NAME'] = self.group.config.name
            if self.config.environment is not None:
                env.update(self.config.environment)

            # change directory
            cwd = self.config.directory
            try:
                if cwd is not None:
                    os.chdir(cwd)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = "couldn't chdir to %s: %s\n" % (cwd, code)
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set umask, then execve
            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(filename, argv, env)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = "couldn't exec %s: %s\n" % (argv[0], code)
                os.write(2, as_bytes('supervisor: ' + msg))
            except:
                (file, fun, line), t, v, tbinfo = compact_traceback()
                error = '%s, %s: file: %s line: %s' % (t, v, file, line)
                msg = "couldn't exec %s: %s\n" % (filename, error)
                os.write(2, as_bytes('supervisor: ' + msg))

            # this point should only be reached if execve failed. the finally clause will exit the child process.

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            options._exit(127)  # exit process with code for spawn failure

    def _check_and_adjust_for_system_clock_rollback(self, test_time):
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """
        if self.state == ProcessStates.STARTING:
            if test_time < self.laststart:
                self.laststart = test_time
            if self.delay > 0 and test_time < (self.delay - self.config.startsecs):
                self.delay = test_time + self.config.startsecs
        elif self.state == ProcessStates.RUNNING:
            if test_time > self.laststart and test_time < (self.laststart + self.config.startsecs):
                self.laststart = test_time - self.config.startsecs
        elif self.state == ProcessStates.STOPPING:
            if test_time < self.last_stop_report:
                self.last_stop_report = test_time
            if self.delay > 0 and test_time < (self.delay - self.config.stopwaitsecs):
                self.delay = test_time + self.config.stopwaitsecs
        elif self.state == ProcessStates.BACKOFF:
            if self.delay > 0 and test_time < (self.delay - self.backoff):
                self.delay = test_time + self.backoff

    def stop(self):
        """ Administrative stop """
        self.administrative_stop = True
        self.last_stop_report = 0
        return self.kill(self.config.stopsignal)

    def stop_report(self):
        """ Log a 'waiting for x to stop' message with throttling. """
        if self.state == ProcessStates.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self.last_stop_report + 2):  # every 2 seconds
                self.config.options.logger.info('waiting for %s to stop' % as_string(self.config.name))
                self.last_stop_report = now

    def give_up(self):
        self.delay = 0
        self.backoff = 0
        self.system_stop = True
        self._check_in_state(ProcessStates.BACKOFF)
        self.change_state(ProcessStates.FATAL)

    def kill(self, sig):
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit).  This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        now = time.time()
        options = self.config.options

        processname = as_string(self.config.name)
        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED.  This is needed because
        # if startretries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self.state == ProcessStates.BACKOFF:
            msg = ('Attempted to kill %s, which is in BACKOFF state.' % processname)
            options.logger.debug(msg)
            self.change_state(ProcessStates.STOPPED)
            return None

        if not self.pid:
            msg = ("attempted to kill %s with sig %s but it wasn't running" % (processname, signame(sig)))
            options.logger.debug(msg)
            return msg

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self.state == ProcessStates.STOPPING:
            killasgroup = self.config.killasgroup
        else:
            killasgroup = self.config.stopasgroup

        as_group = ''
        if killasgroup:
            as_group = 'process group '

        options.logger.debug('killing %s (pid %s) %swith signal %s' % (processname, self.pid, as_group, signame(sig)))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self.killing = True
        self.delay = now + self.config.stopwaitsecs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stopwaitsecs
        self._check_in_state(ProcessStates.RUNNING, ProcessStates.STARTING, ProcessStates.STOPPING)
        self.change_state(ProcessStates.STOPPING)

        pid = self.pid
        if killasgroup:
            # send to the whole process group instead
            pid = -self.pid

        try:
            try:
                os.kill(pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    msg = ('unable to signal %s (pid %s), it probably just exited '
                           'on its own: %s' % (processname, self.pid, str(exc)))
                    options.logger.debug(msg)
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except:
            tb = traceback.format_exc()
            msg = 'unknown problem killing %s (%s):%s' % (processname, self.pid, tb)
            options.logger.critical(msg)
            self.change_state(ProcessStates.UNKNOWN)
            self.killing = False
            self.delay = 0
            return msg

        return None

    def signal(self, sig):
        """
        Send a signal to the subprocess, without intending to kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        options = self.config.options
        processname = as_string(self.config.name)
        if not self.pid:
            msg = ("attempted to send %s sig %s but it wasn't running" % (processname, signame(sig)))
            options.logger.debug(msg)
            return msg

        options.logger.debug('sending %s (pid %s) sig %s' % (processname, self.pid, signame(sig)))

        self._check_in_state(ProcessStates.RUNNING, ProcessStates.STARTING, ProcessStates.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    msg = ('unable to signal %s (pid %s), it probably just now exited '
                           'on its own: %s' % (processname, self.pid, str(exc)))
                    options.logger.debug(msg)
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except:
            tb = traceback.format_exc()
            msg = 'unknown problem sending sig %s (%s):%s' % (processname, self.pid, tb)
            options.logger.critical(msg)
            self.change_state(ProcessStates.UNKNOWN)
            return msg

        return None

    def finish(self, pid, sts):
        """ The process was reaped and we need to report and manage its state """
        self.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self.laststop = now
        processname = as_string(self.config.name)

        if now > self.laststart:
            too_quickly = now - self.laststart < self.config.startsecs
        else:
            too_quickly = False
            self.config.options.logger.warn(
                "process '%s' (%s) laststart time is in the future, don't "
                "know how long process was running so assuming it did "
                "not exit too quickly" % (processname, self.pid))

        exit_expected = es in self.config.exitcodes

        if self.killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self.killing = False
            self.delay = 0
            self.exitstatus = es

            msg = 'stopped: %s (%s)' % (processname, msg)
            self._check_in_state(ProcessStates.STOPPING)
            self.change_state(ProcessStates.STOPPED)
            if exit_expected:
                self.config.options.logger.info(msg)
            else:
                self.config.options.logger.warn(msg)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self.exitstatus = None
            self.spawn_err = 'Exited too quickly (process log may have details)'
            msg = 'exited: %s (%s)' % (processname, msg + '; not expected')
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            self.config.options.logger.warn(msg)

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self.delay = 0
            self.backoff = 0
            self.exitstatus = es

            # if the process was STARTING but a system time change causes self.laststart to be in the future, the normal
            # STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self.state == ProcessStates.STARTING:
                self.change_state(ProcessStates.RUNNING)

            self._check_in_state(ProcessStates.RUNNING)

            if exit_expected:
                # expected exit code
                msg = 'exited: %s (%s)' % (processname, msg + '; expected')
                self.change_state(ProcessStates.EXITED, expected=True)
                self.config.options.logger.info(msg)
            else:
                # unexpected exit code
                self.spawn_err = 'Bad exit code %s' % es
                msg = 'exited: %s (%s)' % (processname, msg + '; not expected')
                self.change_state(ProcessStates.EXITED, expected=False)
                self.config.options.logger.warn(msg)

        self.pid = 0
        self.config.options.close_parent_pipes(self.pipes)
        self.pipes = {}
        self.dispatchers = {}

        # if we died before we processed the current event (only happens if we're an event listener), notify the event
        # system that this event was rejected so it can be processed again.
        if self.event is not None:
            # Note: this should only be true if we were in the BUSY state when finish() was called.
            events.notify(events.EventRejectedEvent(self, self.event))
            self.event = None

    def set_uid(self):
        if self.config.uid is None:
            return None
        msg = self.config.options.drop_privileges(self.config.uid)
        return msg

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        # sort by priority
        return self.config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self.config.name
        return '<Subprocess at %s with name %s in state %s>' % (
            id(self), name, get_process_state_description(self.get_state()))

    def get_state(self):
        return self.state

    def transition(self):
        now = time.time()
        state = self.state

        self._check_and_adjust_for_system_clock_rollback(now)

        logger = self.config.options.logger

        if self.config.options.mood > SupervisorStates.RESTARTING:
            # dont start any processes if supervisor is shutting down
            if state == ProcessStates.EXITED:
                if self.config.autorestart:
                    if self.config.autorestart is RestartUnconditionally:
                        # EXITED -> STARTING
                        self.spawn()
                    elif self.exitstatus not in self.config.exitcodes:
                        # EXITED -> STARTING
                        self.spawn()
            elif state == ProcessStates.STOPPED and not self.laststart:
                if self.config.autostart:
                    # STOPPED -> STARTING
                    self.spawn()
            elif state == ProcessStates.BACKOFF:
                if self.backoff <= self.config.startretries:
                    if now > self.delay:
                        # BACKOFF -> STARTING
                        self.spawn()

        processname = as_string(self.config.name)
        if state == ProcessStates.STARTING:
            if now - self.laststart > self.config.startsecs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.startsecs,
                self.delay = 0
                self.backoff = 0
                self._check_in_state(ProcessStates.STARTING)
                self.change_state(ProcessStates.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for '
                       '> than %s seconds (startsecs)' % self.config.startsecs)
                logger.info('success: %s %s' % (processname, msg))

        if state == ProcessStates.BACKOFF:
            if self.backoff > self.config.startretries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                logger.info('gave up: %s %s' % (processname, msg))

        elif state == ProcessStates.STOPPING:
            time_left = self.delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill.  if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                self.config.options.logger.warn('killing \'%s\' (%s) with SIGKILL' % (processname, self.pid))
                self.kill(signal.SIGKILL)


@functools.total_ordering
class ProcessGroupBase:
    def __init__(self, config):
        self.config = config
        self.processes = {}
        for pconfig in self.config.process_configs:
            self.processes[pconfig.name] = pconfig.make_process(self)

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self.config.name
        return '<%s instance at %s named %s>' % (self.__class__, id(self), name)

    def remove_logs(self):
        for process in self.processes.values():
            process.remove_logs()

    def reopen_logs(self):
        for process in self.processes.values():
            process.reopen_logs()

    def stop_all(self):
        processes = list(self.processes.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.get_state()
            if state == ProcessStates.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()
            elif state == ProcessStates.STARTING:
                # STARTING -> STOPPING
                proc.stop()
            elif state == ProcessStates.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def get_unstopped_processes(self):
        """ Processes which aren't in a state that is considered 'stopped' """
        return [x for x in self.processes.values() if x.get_state() not in STOPPED_STATES]

    def get_dispatchers(self):
        dispatchers = {}
        for process in self.processes.values():
            dispatchers.update(process.dispatchers)
        return dispatchers

    def before_remove(self):
        pass


class ProcessGroup(ProcessGroupBase):
    def transition(self):
        for proc in self.processes.values():
            proc.transition()


class EventListenerPool(ProcessGroupBase):
    def __init__(self, config):
        ProcessGroupBase.__init__(self, config)
        self.event_buffer = []
        self.serial = -1
        self.last_dispatch = 0
        self.dispatch_throttle = 0  # in seconds: .00195 is an interesting one
        self._subscribe()

    def handle_rejected(self, event):
        process = event.process
        procs = self.processes.values()
        if process in procs:  # this is one of our processes
            # rebuffer the event
            self._accept_event(event.event, head=True)

    def transition(self):
        processes = self.processes.values()
        dispatch_capable = False
        for process in processes:
            process.transition()
            # this is redundant, we do it in _dispatch_event too, but we want to reduce function call overhead
            if process.state == ProcessStates.RUNNING:
                if process.listener_state == EventListenerStates.READY:
                    dispatch_capable = True
        if dispatch_capable:
            if self.dispatch_throttle:
                now = time.time()

                if now < self.last_dispatch:
                    # The system clock appears to have moved backward Reset self.last_dispatch accordingly
                    self.last_dispatch = now

                if now - self.last_dispatch < self.dispatch_throttle:
                    return
            self.dispatch()

    def before_remove(self):
        self._unsubscribe()

    def dispatch(self):
        while self.event_buffer:
            # dispatch the oldest event
            event = self.event_buffer.pop(0)
            ok = self._dispatch_event(event)
            if not ok:
                # if we can't dispatch an event, rebuffer it and stop trying to process any further events in the buffer
                self._accept_event(event, head=True)
                break
        self.last_dispatch = time.time()

    def _accept_event(self, event, head=False):
        # events are required to be instances this has a side effect to fail with an attribute error on 'old style'
        # classes
        processname = as_string(self.config.name)
        if not hasattr(event, 'serial'):
            event.serial = new_serial(GlobalSerial)
        if not hasattr(event, 'pool_serials'):
            event.pool_serials = {}
        if self.config.name not in event.pool_serials:
            event.pool_serials[self.config.name] = new_serial(self)
        else:
            self.config.options.logger.debug(
                'rebuffering event %s for pool %s (buf size=%d, max=%d)' % (
                    (event.serial, processname, len(self.event_buffer), self.config.buffer_size)))

        if len(self.event_buffer) >= self.config.buffer_size:
            if self.event_buffer:
                # discard the oldest event
                discarded_event = self.event_buffer.pop(0)
                self.config.options.logger.error(
                    'pool %s event buffer overflowed, discarding event %s' % ((processname, discarded_event.serial)))
        if head:
            self.event_buffer.insert(0, event)
        else:
            self.event_buffer.append(event)

    def _dispatch_event(self, event):
        pool_serial = event.pool_serials[self.config.name]

        for process in self.processes.values():
            if process.state != ProcessStates.RUNNING:
                continue
            if process.listener_state == EventListenerStates.READY:
                processname = as_string(process.config.name)
                payload = event.payload()
                try:
                    event_type = event.__class__
                    serial = event.serial
                    envelope = self._event_envelope(event_type, serial, pool_serial, payload)
                    process.write(as_bytes(envelope))
                except OSError as why:
                    if why.args[0] != errno.EPIPE:
                        raise

                    self.config.options.logger.debug(
                        'epipe occurred while sending event %s '
                        'to listener %s, listener state unchanged' % (event.serial, processname))
                    continue

                process.listener_state = EventListenerStates.BUSY
                process.event = event
                self.config.options.logger.debug('event %s sent to listener %s' % (event.serial, processname))
                return True

        return False

    def _event_envelope(self, event_type, serial, pool_serial, payload):
        event_name = events.get_event_name_by_type(event_type)
        payload_len = len(payload)
        D = {
            'ver': '3.0',
            'sid': self.config.options.identifier,
            'serial': serial,
            'pool_name': self.config.name,
            'pool_serial': pool_serial,
            'event_name': event_name,
            'len': payload_len,
            'payload': payload,
        }
        return (
                'ver:%(ver)s '
                'server:%(sid)s '
                'serial:%(serial)s '
                'pool:%(pool_name)s '
                'poolserial:%(pool_serial)s '
                'eventname:%(event_name)s '
                'len:%(len)s\n%(payload)s'
                % D
        )

    def _subscribe(self):
        for event_type in self.config.pool_events:
            events.subscribe(event_type, self._accept_event)
        events.subscribe(events.EventRejectedEvent, self.handle_rejected)

    def _unsubscribe(self):
        for event_type in self.config.pool_events:
            events.unsubscribe(event_type, self._accept_event)
        events.unsubscribe(events.EventRejectedEvent, self.handle_rejected)


class GlobalSerial:
    def __init__(self):
        self.serial = -1


GlobalSerial = GlobalSerial()  # singleton


def new_serial(inst):
    if inst.serial == sys.maxsize:
        inst.serial = -1
    inst.serial += 1
    return inst.serial
