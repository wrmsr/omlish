#!/usr/bin/env python -u
# Supervisor is licensed under the following license:
#
#  A copyright notice accompanies this license document that identifies the copyright holders.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions in source code must retain the accompanying copyright notice, this list of conditions, and the
#     following disclaimer.
#
#  2. Redistributions in binary form must reproduce the accompanying copyright notice, this list of conditions, and the
#     following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Names of the copyright holders must not be used to endorse or promote products derived from this software without
#     prior written permission from the copyright holders.
#
#  4. If any files are modified, you must cause the modified files to carry prominent notices stating that you changed
#     the files and the date of any change.
#
#  Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
#   NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
pidproxy -- run command and proxy signals to it via its pidfile.

This executable runs a command and then monitors a pidfile.  When this
executable receives a signal, it sends the same signal to the pid
in the pidfile.

Usage: %s <pidfile name> <command> [<cmdarg1> ...]
"""
import os
import sys
import signal
import time


class PidProxy:
    pid = None

    def __init__(self, args):
        super().__init__()
        try:
            self.pidfile, cmdargs = args[1], args[2:]
            self.abscmd = os.path.abspath(cmdargs[0])
            self.cmdargs = cmdargs
        except (ValueError, IndexError):
            self.usage()
            sys.exit(1)

    def go(self):
        self.set_signals()
        self.pid = os.spawnv(os.P_NOWAIT, self.abscmd, self.cmdargs)
        while 1:
            time.sleep(5)
            try:
                pid = os.waitpid(-1, os.WNOHANG)[0]
            except OSError:
                pid = None
            if pid:
                break

    def usage(self):
        print(__doc__ % sys.argv[0])

    def set_signals(self):
        signal.signal(signal.SIGTERM, self.pass_to_child)
        signal.signal(signal.SIGHUP, self.pass_to_child)
        signal.signal(signal.SIGINT, self.pass_to_child)
        signal.signal(signal.SIGUSR1, self.pass_to_child)
        signal.signal(signal.SIGUSR2, self.pass_to_child)
        signal.signal(signal.SIGQUIT, self.pass_to_child)
        signal.signal(signal.SIGCHLD, self.reap)

    def reap(self, sig, frame):
        # do nothing, we reap our child synchronously
        pass

    def pass_to_child(self, sig, frame):
        try:
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
        except:
            print("Can't read child pidfile %s!" % self.pidfile)
            return
        os.kill(pid, sig)
        if sig in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT]:
            sys.exit(0)


def main():
    pp = PidProxy(sys.argv)
    pp.go()


if __name__ == '__main__':
    main()
