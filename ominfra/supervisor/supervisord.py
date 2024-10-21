#!/usr/bin/env python3
# !@omlish-amalg _amalg.py
"""
TODO:
 - amalg or not? only use om.logs and dc's
"""
import logging
import signal
import time

from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging

from .compat import ExitNow
from .compat import as_string
from .compat import decode_wait_status
from .compat import signame
from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .configs import ServerConfig
from .context import ServerContext
from .events import TICK_EVENTS
from .events import ProcessGroupAddedEvent
from .events import ProcessGroupRemovedEvent
from .events import SupervisorRunningEvent
from .events import SupervisorStoppingEvent
from .events import clear_events
from .events import notify_event
from .process import ProcessGroup
from .states import SupervisorStates
from .states import get_process_state_description


log = logging.getLogger(__name__)


class Supervisor:
    stopping = False  # set after we detect that we are handling a stop request
    last_shutdown_report = 0.  # throttle for delayed process error reports at stop
    process_groups: dict  # map of process group name to process group object
    stop_groups = None  # list used for priority ordered shutdown

    def __init__(self, context: ServerContext) -> None:
        super().__init__()

        self.context = context
        self.process_groups = {}
        self.ticks: dict = {}

    def main(self):
        if not self.context.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self.context.cleanup_fds()

        self.context.set_uid_or_exit()

        if self.context.first:
            self.context.set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self.context.config.nocleanup:
            # clean up old automatic logs
            self.context.clear_auto_child_logdir()

        self.run()

    def run(self):
        self.process_groups = {}  # clear
        self.stop_groups = None  # clear
        clear_events()
        try:
            for config in self.context.config.groups or []:
                self.add_process_group(config)
            self.context.set_signals()
            if not self.context.config.nodaemon and self.context.first:
                self.context.daemonize()
            # writing pid file needs to come *after* daemonizing or pid will be wrong
            self.context.write_pidfile()
            self.runforever()
        finally:
            self.context.cleanup()

    def diff_to_active(self):
        new = self.context.config.groups or []
        cur = [group.config for group in self.process_groups.values()]

        curdict = dict(zip([cfg.name for cfg in cur], cur))
        newdict = dict(zip([cfg.name for cfg in new], new))

        added = [cand for cand in new if cand.name not in curdict]
        removed = [cand for cand in cur if cand.name not in newdict]

        changed = [cand for cand in new if cand != curdict.get(cand.name, cand)]

        return added, changed, removed

    def add_process_group(self, config):
        name = config.name
        if name not in self.process_groups:
            group = self.process_groups[name] = ProcessGroup(config, self.context)
            group.after_setuid()
            notify_event(ProcessGroupAddedEvent(name))
            return True
        return False

    def remove_process_group(self, name):
        if self.process_groups[name].get_unstopped_processes():
            return False
        self.process_groups[name].before_remove()
        del self.process_groups[name]
        notify_event(ProcessGroupRemovedEvent(name))
        return True

    def get_process_map(self):
        process_map = {}
        for group in self.process_groups.values():
            process_map.update(group.get_dispatchers())
        return process_map

    def shutdown_report(self):
        unstopped = []

        for group in self.process_groups.values():
            unstopped.extend(group.get_unstopped_processes())

        if unstopped:
            # throttle 'waiting for x to die' reports
            now = time.time()
            if now > (self.last_shutdown_report + 3):  # every 3 secs
                names = [as_string(p.config.name) for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die', namestr)
                self.last_shutdown_report = now
                for proc in unstopped:
                    state = get_process_state_description(proc.get_state())
                    log.debug('%s state: %s', proc.config.name, state)
        return unstopped

    def ordered_stop_groups_phase_1(self):
        if self.stop_groups:
            # stop the last group (the one with the "highest" priority)
            self.stop_groups[-1].stop_all()  # type: ignore

    def ordered_stop_groups_phase_2(self):
        # after phase 1 we've transitioned and reaped, let's see if we can remove the group we stopped from the
        # stop_groups queue.
        if self.stop_groups:
            # pop the last group (the one with the "highest" priority)
            group = self.stop_groups.pop()  # type: ignore
            if group.get_unstopped_processes():
                # if any processes in the group aren't yet in a stopped state, we're not yet done shutting this group
                # down, so push it back on to the end of the stop group queue
                self.stop_groups.append(group)

    def runforever(self):
        notify_event(SupervisorRunningEvent())
        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)

        while 1:
            combined_map = {}
            combined_map.update(self.get_process_map())

            pgroups = list(self.process_groups.values())
            pgroups.sort()

            if self.context.state < SupervisorStates.RUNNING:
                if not self.stopping:
                    # first time, set the stopping flag, do a notification and set stop_groups
                    self.stopping = True
                    self.stop_groups = pgroups[:]
                    notify_event(SupervisorStoppingEvent())

                self.ordered_stop_groups_phase_1()

                if not self.shutdown_report():
                    # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                    raise ExitNow

            for fd, dispatcher in combined_map.items():
                if dispatcher.readable():
                    self.context.poller.register_readable(fd)
                if dispatcher.writable():
                    self.context.poller.register_writable(fd)

            r, w = self.context.poller.poll(timeout)

            for fd in r:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('read event caused by %r', dispatcher)
                        dispatcher.handle_read_event()
                        if not dispatcher.readable():
                            self.context.poller.unregister_readable(fd)
                    except ExitNow:
                        raise
                    except Exception:  # noqa
                        combined_map[fd].handle_error()
                else:
                    # if the fd is not in combined_map, we should unregister it. otherwise, it will be polled every
                    # time, which may cause 100% cpu usage
                    log.debug('unexpected read event from fd %r', fd)
                    try:
                        self.context.poller.unregister_readable(fd)
                    except Exception:  # noqa
                        pass

            for fd in w:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('write event caused by %r', dispatcher)
                        dispatcher.handle_write_event()
                        if not dispatcher.writable():
                            self.context.poller.unregister_writable(fd)
                    except ExitNow:
                        raise
                    except Exception:  # noqa
                        combined_map[fd].handle_error()
                else:
                    log.debug('unexpected write event from fd %r', fd)
                    try:
                        self.context.poller.unregister_writable(fd)
                    except Exception:  # noqa
                        pass

            for group in pgroups:
                group.transition()

            self.reap()
            self.handle_signal()
            self.tick()

            if self.context.state < SupervisorStates.RUNNING:
                self.ordered_stop_groups_phase_2()

            if self.context.test:
                break

    def tick(self, now=None):
        """Send one or more 'tick' events when the timeslice related to the period for the event type rolls over"""
        if now is None:
            # now won't be None in unit tests
            now = time.time()
        for event in TICK_EVENTS:
            period = event.period  # type: ignore
            last_tick = self.ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self.ticks[period] = timeslice(period, now)
            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self.ticks[period] = this_tick
                notify_event(event(this_tick, self))

    def reap(self, once=False, recursionguard=0):
        if recursionguard == 100:
            return
        pid, sts = self.context.waitpid()
        if pid:
            process = self.context.pid_history.get(pid, None)
            if process is None:
                _, msg = decode_wait_status(check_not_none(sts))
                log.info('reaped unknown pid %s (%s)', pid, msg)
            else:
                process.finish(check_not_none(sts))
                del self.context.pid_history[pid]
            if not once:
                # keep reaping until no more kids to reap, but don't recurse infinitely
                self.reap(once=False, recursionguard=recursionguard + 1)

    def handle_signal(self):
        sig = self.context.get_signal()
        if sig:
            if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
                log.warning('received %s indicating exit request', signame(sig))
                self.context.state = SupervisorStates.SHUTDOWN

            elif sig == signal.SIGHUP:
                if self.context.state == SupervisorStates.SHUTDOWN:
                    log.warning('ignored %s indicating restart request (shutdown in progress)', signame(sig))  # noqa
                else:
                    log.warning('received %s indicating restart request', signame(sig))  # noqa
                    self.context.state = SupervisorStates.RESTARTING

            elif sig == signal.SIGCHLD:
                log.debug('received %s indicating a child quit', signame(sig))

            elif sig == signal.SIGUSR2:
                log.info('received %s indicating log reopen request', signame(sig))
                # self.context.reopen_logs()
                for group in self.process_groups.values():
                    group.reopen_logs()

            else:
                log.debug('received %s indicating nothing', signame(sig))

    def get_state(self):
        return self.context.state


def timeslice(period, when):
    return int(when - (when % period))


def main(args=None, test=False):
    configure_standard_logging('INFO')

    # if we hup, restart by making a new Supervisor()
    first = True
    while True:
        config = ServerConfig.new(
            nodaemon=True,
            groups=[
                ProcessGroupConfig(
                    name='default',
                    processes=[
                        ProcessConfig(
                            name='sleep',
                            command='sleep 600',
                            stdout=ProcessConfig.Log(
                                file='/dev/fd/1',
                                maxbytes=0,
                            ),
                            redirect_stderr=True,
                        ),
                        ProcessConfig(
                            name='ls',
                            command='ls -al',
                            stdout=ProcessConfig.Log(
                                file='/dev/fd/1',
                                maxbytes=0,
                            ),
                            redirect_stderr=True,
                        ),
                    ],
                ),
            ],
        )

        context = ServerContext(
            config,
        )

        context.first = first
        context.test = test
        go(context)
        # options.close_logger()
        first = False
        if test or (context.state < SupervisorStates.RESTARTING):
            break


def go(context):  # pragma: no cover
    d = Supervisor(context)
    try:
        d.main()
    except ExitNow:
        pass


if __name__ == '__main__':
    main()
