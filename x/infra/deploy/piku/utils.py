import collections
import os.path
import re
import shutil
import socket
import stat
import subprocess
import sys
import time

import click

from .env import APP_ROOT


def sanitize_app_name(app):
    """Sanitize the app name and build matching path"""

    app = "".join(c for c in app if c.isalnum() or c in ('.', '_', '-')).rstrip().lstrip('/')
    return app


def exit_if_invalid(app):
    """Utility function for error checking upon command startup."""

    app = sanitize_app_name(app)
    if not os.path.exists(os.path.join(APP_ROOT, app)):
        click.secho("Error: app '{}' not found.".format(app), fg='red')
        sys.exit(1)
    return app


def get_free_port(address=""):
    """Find a free TCP port (entirely at random)"""

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 0))  # lgtm [py/bind-socket-all-network-interfaces]
    port = s.getsockname()[1]
    s.close()
    return port


def get_boolean(value):
    """Convert a boolean-ish string to a boolean."""

    return value.lower() in ['1', 'on', 'true', 'enabled', 'yes', 'y']


def write_config(filename, bag, separator='='):
    """Helper for writing out config files"""

    with open(filename, 'w') as h:
        # pylint: disable=unused-variable
        for k, v in bag.items():
            h.write('{k:s}{separator:s}{v}\n'.format(**locals()))


def setup_authorized_keys(ssh_fingerprint, script_path, pubkey):
    """Sets up an authorized_keys file to redirect SSH commands"""

    authorized_keys = os.path.join(os.environ['HOME'], '.ssh', 'authorized_keys')
    if not os.path.exists(os.path.dirname(authorized_keys)):
        os.makedirs(os.path.dirname(authorized_keys))
    # Restrict features and force all SSH commands to go through our script
    with open(authorized_keys, 'a') as h:
        h.write(
            ''.join([
                """command="FINGERPRINT={ssh_fingerprint:s} NAME=default {script_path:s} $SSH_ORIGINAL_COMMAND",""",
                "no-agent-forwarding,no-user-rc,no-X11-forwarding,no-port-forwarding {pubkey:s}\n",
            ]).format(**locals()),
        )
    os.chmod(os.path.dirname(authorized_keys), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    os.chmod(authorized_keys, stat.S_IRUSR | stat.S_IWUSR)


CRON_REGEXP = r"^((?:(?:\*\/)?\d+)|\*) ((?:(?:\*\/)?\d+)|\*) ((?:(?:\*\/)?\d+)|\*) ((?:(?:\*\/)?\d+)|\*) ((?:(?:\*\/)?\d+)|\*) (.*)$"  # noqa


def parse_procfile(filename):
    """Parses a Procfile and returns the worker types. Only one worker of each type is allowed."""

    workers = {}
    if not os.path.exists(filename):
        return None

    with open(filename, 'r') as procfile:
        for line_number, line in enumerate(procfile):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            try:
                kind, command = map(lambda x: x.strip(), line.split(":", 1))
                # Check for cron patterns
                if kind == "cron":
                    limits = [59, 24, 31, 12, 7]
                    res = re.match(CRON_REGEXP, command)
                    if res:
                        matches = res.groups()
                        for i in range(len(limits)):
                            if int(matches[i].replace("*/", "").replace("*", "1")) > limits[i]:
                                raise ValueError
                workers[kind] = command
            except Exception:
                click.secho("Warning: misformatted Procfile entry '{}' at line {}".format(line, line_number), fg='yellow')
    if len(workers) == 0:
        return {}
    # WSGI trumps regular web workers
    if 'wsgi' in workers:
        if 'web' in workers:
            click.secho("Warning: found both 'wsgi' and 'web' workers, disabling 'web'", fg='yellow')
            del workers['web']
    return workers


def expandvars(buffer, env, default=None, skip_escaped=False):
    """expand shell-style environment variables in a buffer"""

    def replace_var(match):
        return env.get(match.group(2) or match.group(1), match.group(0) if default is None else default)

    pattern = (r'(?<!\\)' if skip_escaped else '') + r'\$(\w+|\{([^}]*)\})'
    return re.sub(pattern, replace_var, buffer)


def command_output(cmd):
    """executes a command and grabs its output, if any"""
    try:
        env = os.environ
        return str(subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env, shell=True))
    except Exception:
        return ""


def parse_settings(filename, env={}):
    """Parses a settings file and returns a dict with environment variables"""

    if not os.path.exists(filename):
        return {}

    with open(filename, 'r') as settings:
        for line in settings:
            if line[0] == '#' or len(line.strip()) == 0:  # ignore comments and newlines
                continue
            try:
                k, v = map(lambda x: x.strip(), line.split("=", 1))
                env[k] = expandvars(v, env)
            except Exception:
                click.secho("Error: malformed setting '{}', ignoring file.".format(line), fg='red')
                return {}
    return env


def check_requirements(binaries):
    """Checks if all the binaries exist and are executable"""

    click.secho("-----> Checking requirements: {}".format(binaries), fg='green')
    requirements = list(map(shutil.which, binaries))
    click.secho(str(requirements))

    if None in requirements:
        return False
    return True


def multi_tail(app, filenames, catch_up=20):
    """Tails multiple log files"""

    # Seek helper
    def peek(handle):
        where = handle.tell()
        line = handle.readline()
        if not line:
            handle.seek(where)
            return None
        return line

    inodes = {}
    files = {}
    prefixes = {}

    # Set up current state for each log file
    for f in filenames:
        prefixes[f] = os.path.splitext(os.path.basename(f))[0]
        files[f] = open(f, "rt", encoding="utf-8", errors="ignore")
        inodes[f] = os.stat(f).st_ino
        files[f].seek(0, 2)

    longest = max(map(len, prefixes.values()))

    # Grab a little history (if any)
    for f in filenames:
        for line in collections.deque(open(f, "rt", encoding="utf-8", errors="ignore"), catch_up):
            yield "{} | {}".format(prefixes[f].ljust(longest), line)

    while True:
        updated = False
        # Check for updates on every file
        for f in filenames:
            line = peek(files[f])
            if line:
                updated = True
                yield "{} | {}".format(prefixes[f].ljust(longest), line)

        if not updated:
            time.sleep(1)
            # Check if logs rotated
            for f in filenames:
                if os.path.exists(f):
                    if os.stat(f).st_ino != inodes[f]:
                        files[f] = open(f)
                        inodes[f] = os.stat(f).st_ino
                else:
                    filenames.remove(f)


