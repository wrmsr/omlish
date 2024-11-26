import os
import signal
import sys


MAXSIG = 31  # Signals we care about, 1 to 31 inclusive


class DumbInit:
    def __init__(self, command, debug=False, use_setsid=True):
        super().__init__()
        self.command = command
        self.debug = debug
        self.use_setsid = use_setsid
        self.child_pid = None
        self.signal_rewrite = {i: i for i in range(1, MAXSIG + 1)}
        self.signal_temporary_ignores = {i: 0 for i in range(1, MAXSIG + 1)}

    def log(self, message, *args):
        if self.debug:
            print(f'[dumb-init] {message}' % args, file=sys.stderr)

    def translate_signal(self, signum):
        return self.signal_rewrite.get(signum, signum)

    def forward_signal(self, signum):
        translated = self.translate_signal(signum)
        if translated > 0:
            target = -self.child_pid if self.use_setsid else self.child_pid
            os.kill(target, translated)
            self.log('Forwarded signal %d to children.', translated)

    def handle_signal(self, signum, frame):
        self.log('Received signal %d.', signum)

        if self.signal_temporary_ignores[signum] == 1:
            self.log('Ignoring temporary signal %d.', signum)
            self.signal_temporary_ignores[signum] = 0
        elif signum == signal.SIGCHLD:
            self.handle_child_exit()
        else:
            self.forward_signal(signum)
            if signum in {signal.SIGTSTP, signal.SIGTTIN, signal.SIGTTOU}:
                self.log('Suspending self due to TTY signal.')
                os.kill(os.getpid(), signal.SIGSTOP)

    def handle_child_exit(self):
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                elif pid == self.child_pid:
                    if os.WIFEXITED(status):
                        exit_status = os.WEXITSTATUS(status)
                        self.log('Child exited with status %d.', exit_status)
                    elif os.WIFSIGNALED(status):
                        exit_status = 128 + os.WTERMSIG(status)
                        self.log('Child terminated by signal %d.', exit_status - 128)
                    self.forward_signal(signal.SIGTERM)
                    sys.exit(exit_status)
            except ChildProcessError:
                break

    def run(self):
        for i in range(1, MAXSIG + 1):
            signal.signal(i, self.handle_signal)

        if self.use_setsid:
            try:
                os.setsid()
                self.log('Detached from controlling TTY.')
            except Exception as e:  # noqa
                self.log('Failed to detach from controlling TTY: %s', str(e))

        self.child_pid = os.fork()
        if self.child_pid == 0:  # Child process
            os.execvp(self.command[0], self.command)
        else:  # Parent process
            self.log('Spawned child process with PID %d.', self.child_pid)
            while True:
                signal.pause()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='dumb-init equivalent in Python.')
    parser.add_argument('command', nargs='+', help='Command to run.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug output.')
    parser.add_argument('-c', '--single-child', action='store_true', help='Do not use setsid.')
    args = parser.parse_args()

    dumb_init = DumbInit(
        command=args.command,
        debug=args.verbose,
        use_setsid=not args.single_child,
    )
    dumb_init.run()


if __name__ == '__main__':
    main()
