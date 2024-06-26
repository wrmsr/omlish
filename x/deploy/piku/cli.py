#!/usr/bin/env python3
"""Piku Micro-PaaS"""
from fcntl import F_GETFL
from fcntl import F_SETFL
from fcntl import fcntl
from glob import glob
from grp import getgrgid
from importlib import import_module
from multiprocessing import cpu_count
from os import O_NONBLOCK
from os import chmod
from os import environ
from os import getgid
from os import getuid
from os import listdir
from os import makedirs
from os import remove
from os import stat
from os import unlink
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import isdir
from os.path import join
from os.path import realpath
from pwd import getpwuid
from shutil import copyfile
from shutil import rmtree
from stat import S_IXUSR
from subprocess import Popen
from subprocess import STDOUT
from subprocess import call
from subprocess import check_output
from sys import argv
from sys import path as sys_path
from sys import stderr
from sys import stdin
from sys import stdout
from sys import version_info
from tempfile import NamedTemporaryFile
from traceback import format_exc

from click import CommandCollection
from click import argument
from click import group
from click import pass_context
from click import secho as echo

from .deploy import do_deploy
from .deploy import do_restart
from .deploy import do_stop
from .env import ACME_WWW
from .env import APP_ROOT
from .env import CACHE_ROOT
from .env import DATA_ROOT
from .env import ENV_ROOT
from .env import GIT_ROOT
from .env import LOG_ROOT
from .env import NGINX_ROOT
from .env import PIKU_PLUGIN_ROOT
from .env import PIKU_RAW_SOURCE_URL
from .env import PIKU_SCRIPT
from .env import UWSGI_AVAILABLE
from .env import UWSGI_ENABLED
from .env import UWSGI_LOG_MAXSIZE
from .env import UWSGI_ROOT
from .utils import exit_if_invalid
from .utils import multi_tail
from .utils import parse_procfile
from .utils import parse_settings
from .utils import sanitize_app_name
from .utils import setup_authorized_keys
from .utils import write_config


# === CLI commands ===


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@group(context_settings=CONTEXT_SETTINGS)
def piku():
    """The smallest PaaS you've ever seen"""
    pass


piku.rc = getattr(piku, "result_callback", None) or getattr(piku, "resultcallback", None)


@piku.rc()
def cleanup(ctx):
    """Callback from command execution -- add debugging to taste"""
    pass


# --- User commands ---


@piku.command("apps")
def cmd_apps():
    """List apps, e.g.: piku apps"""
    apps = listdir(APP_ROOT)
    if not apps:
        echo("There are no applications deployed.")
        return

    for a in apps:
        running = len(glob(join(UWSGI_ENABLED, '{}*.ini'.format(a)))) != 0
        echo(('*' if running else ' ') + a, fg='green')


@piku.command("config")
@argument('app')
def cmd_config(app):
    """Show config, e.g.: piku config <app>"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'ENV')
    if exists(config_file):
        echo(open(config_file).read().strip(), fg='white')
    else:
        echo("Warning: app '{}' not deployed, no config found.".format(app), fg='yellow')


@piku.command("config:get")
@argument('app')
@argument('setting')
def cmd_config_get(app, setting):
    """e.g.: piku config:get <app> FOO"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'ENV')
    if exists(config_file):
        env = parse_settings(config_file)
        if setting in env:
            echo("{}".format(env[setting]), fg='white')
    else:
        echo("Warning: no active configuration for '{}'".format(app))


@piku.command("config:set")
@argument('app')
@argument('settings', nargs=-1)
def cmd_config_set(app, settings):
    """e.g.: piku config:set <app> FOO=bar BAZ=quux"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'ENV')
    env = parse_settings(config_file)
    for s in settings:
        try:
            k, v = map(lambda x: x.strip(), s.split("=", 1))
            env[k] = v
            echo("Setting {k:s}={v} for '{app:s}'".format(**locals()), fg='white')
        except Exception:
            echo("Error: malformed setting '{}'".format(s), fg='red')
            return
    write_config(config_file, env)
    do_deploy(app)


@piku.command("config:unset")
@argument('app')
@argument('settings', nargs=-1)
def cmd_config_unset(app, settings):
    """e.g.: piku config:unset <app> FOO"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'ENV')
    env = parse_settings(config_file)
    for s in settings:
        if s in env:
            del env[s]
            echo("Unsetting {} for '{}'".format(s, app), fg='white')
    write_config(config_file, env)
    do_deploy(app)


@piku.command("config:live")
@argument('app')
def cmd_config_live(app):
    """e.g.: piku config:live <app>"""

    app = exit_if_invalid(app)

    live_config = join(ENV_ROOT, app, 'LIVE_ENV')
    if exists(live_config):
        echo(open(live_config).read().strip(), fg='white')
    else:
        echo("Warning: app '{}' not deployed, no config found.".format(app), fg='yellow')


@piku.command("deploy")
@argument('app')
def cmd_deploy(app):
    """e.g.: piku deploy <app>"""

    app = exit_if_invalid(app)
    do_deploy(app)


@piku.command("destroy")
@argument('app')
def cmd_destroy(app):
    """e.g.: piku destroy <app>"""

    app = exit_if_invalid(app)

    # leave DATA_ROOT, since apps may create hard to reproduce data,
    # and CACHE_ROOT, since `nginx` will set permissions to protect it
    for p in [join(x, app) for x in [APP_ROOT, GIT_ROOT, ENV_ROOT, LOG_ROOT]]:
        if exists(p):
            echo("--> Removing folder '{}'".format(p), fg='yellow')
            rmtree(p)

    for p in [join(x, '{}*.ini'.format(app)) for x in [UWSGI_AVAILABLE, UWSGI_ENABLED]]:
        g = glob(p)
        if len(g) > 0:
            for f in g:
                echo("--> Removing file '{}'".format(f), fg='yellow')
                remove(f)

    nginx_files = [join(NGINX_ROOT, "{}.{}".format(app, x)) for x in ['conf', 'sock', 'key', 'crt']]
    for f in nginx_files:
        if exists(f):
            echo("--> Removing file '{}'".format(f), fg='yellow')
            remove(f)

    acme_link = join(ACME_WWW, app)
    acme_certs = realpath(acme_link)
    if exists(acme_certs):
        echo("--> Removing folder '{}'".format(acme_certs), fg='yellow')
        rmtree(acme_certs)
        echo("--> Removing file '{}'".format(acme_link), fg='yellow')
        unlink(acme_link)

    # These come last to make sure they're visible
    for p in [join(x, app) for x in [DATA_ROOT, CACHE_ROOT]]:
        if exists(p):
            echo("==> Preserving folder '{}'".format(p), fg='red')


@piku.command("logs")
@argument('app')
@argument('process', nargs=1, default='*')
def cmd_logs(app, process):
    """Tail running logs, e.g: piku logs <app> [<process>]"""

    app = exit_if_invalid(app)

    logfiles = glob(join(LOG_ROOT, app, process + '.*.log'))
    if len(logfiles) > 0:
        for line in multi_tail(app, logfiles):
            echo(line.strip(), fg='white')
    else:
        echo("No logs found for app '{}'.".format(app), fg='yellow')


@piku.command("ps")
@argument('app')
def cmd_ps(app):
    """Show process count, e.g: piku ps <app>"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'SCALING')
    if exists(config_file):
        echo(open(config_file).read().strip(), fg='white')
    else:
        echo("Error: no workers found for app '{}'.".format(app), fg='red')


@piku.command("ps:scale")
@argument('app')
@argument('settings', nargs=-1)
def cmd_ps_scale(app, settings):
    """e.g.: piku ps:scale <app> <proc>=<count>"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'SCALING')
    worker_count = {k: int(v) for k, v in parse_procfile(config_file).items()}
    deltas = {}
    for s in settings:
        try:
            k, v = map(lambda x: x.strip(), s.split("=", 1))
            c = int(v)  # check for integer value
            if c < 0:
                echo("Error: cannot scale type '{}' below 0".format(k), fg='red')
                return
            if k not in worker_count:
                echo("Error: worker type '{}' not present in '{}'".format(k, app), fg='red')
                return
            deltas[k] = c - worker_count[k]
        except Exception:
            echo("Error: malformed setting '{}'".format(s), fg='red')
            return
    do_deploy(app, deltas)


@piku.command("run")
@argument('app')
@argument('cmd', nargs=-1)
def cmd_run(app, cmd):
    """e.g.: piku run <app> ls -- -al"""

    app = exit_if_invalid(app)

    config_file = join(ENV_ROOT, app, 'LIVE_ENV')
    environ.update(parse_settings(config_file))
    for f in [stdout, stderr]:
        fl = fcntl(f, F_GETFL)
        fcntl(f, F_SETFL, fl | O_NONBLOCK)
    p = Popen(
        ' '.join(cmd),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        env=environ,
        cwd=join(APP_ROOT, app),
        shell=True,
    )
    p.communicate()


@piku.command("restart")
@argument('app')
def cmd_restart(app):
    """Restart an app: piku restart <app>"""

    app = exit_if_invalid(app)

    do_restart(app)


@piku.command("setup")
def cmd_setup():
    """Initialize environment"""

    echo("Running in Python {}".format(".".join(map(str, version_info))))

    # Create required paths
    for p in [
        APP_ROOT,
        CACHE_ROOT,
        DATA_ROOT,
        GIT_ROOT,
        ENV_ROOT,
        UWSGI_ROOT,
        UWSGI_AVAILABLE,
        UWSGI_ENABLED,
        LOG_ROOT,
        NGINX_ROOT,
    ]:
        if not exists(p):
            echo("Creating '{}'.".format(p), fg='green')
            makedirs(p)

    # Set up the uWSGI emperor config
    settings = [
        ('chdir', UWSGI_ROOT),
        ('emperor', UWSGI_ENABLED),
        ('log-maxsize', UWSGI_LOG_MAXSIZE),
        ('logto', join(UWSGI_ROOT, 'uwsgi.log')),
        ('log-backupname', join(UWSGI_ROOT, 'uwsgi.old.log')),
        ('socket', join(UWSGI_ROOT, 'uwsgi.sock')),
        ('uid', getpwuid(getuid()).pw_name),
        ('gid', getgrgid(getgid()).gr_name),
        ('enable-threads', 'true'),
        ('threads', '{}'.format(cpu_count() * 2)),
    ]
    with open(join(UWSGI_ROOT, 'uwsgi.ini'), 'w') as h:
        h.write('[uwsgi]\n')
        # pylint: disable=unused-variable
        for k, v in settings:
            h.write("{k:s} = {v}\n".format(**locals()))

    # mark this script as executable (in case we were invoked via interpreter)
    if not (stat(PIKU_SCRIPT).st_mode & S_IXUSR):
        echo("Setting '{}' as executable.".format(PIKU_SCRIPT), fg='yellow')
        chmod(PIKU_SCRIPT, stat(PIKU_SCRIPT).st_mode | S_IXUSR)


@piku.command("setup:ssh")
@argument('public_key_file')
def cmd_setup_ssh(public_key_file):
    """Set up a new SSH key (use - for stdin)"""

    def add_helper(key_file):
        if exists(key_file):
            try:
                fingerprint = str(check_output('ssh-keygen -lf ' + key_file, shell=True)).split(' ', 4)[1]
                key = open(key_file, 'r').read().strip()
                echo("Adding key '{}'.".format(fingerprint), fg='white')
                setup_authorized_keys(fingerprint, PIKU_SCRIPT, key)
            except Exception:
                echo("Error: invalid public key file '{}': {}".format(key_file, format_exc()), fg='red')
        elif public_key_file == '-':
            buffer = "".join(stdin.readlines())
            with NamedTemporaryFile(mode="w") as f:
                f.write(buffer)
                f.flush()
                add_helper(f.name)
        else:
            echo("Error: public key file '{}' not found.".format(key_file), fg='red')

    add_helper(public_key_file)


@piku.command("stop")
@argument('app')
def cmd_stop(app):
    """Stop an app, e.g: piku stop <app>"""
    app = exit_if_invalid(app)
    do_stop(app)


# --- Internal commands ---


@piku.command("git-hook")
@argument('app')
def cmd_git_hook(app):
    """INTERNAL: Post-receive git hook"""

    app = sanitize_app_name(app)
    repo_path = join(GIT_ROOT, app)
    app_path = join(APP_ROOT, app)
    data_path = join(DATA_ROOT, app)

    for line in stdin:
        # pylint: disable=unused-variable
        oldrev, newrev, refname = line.strip().split(" ")
        # Handle pushes
        if not exists(app_path):
            echo("-----> Creating app '{}'".format(app), fg='green')
            makedirs(app_path)
            # The data directory may already exist, since this may be a full redeployment (we never delete data since it
            # may be expensive to recreate)
            if not exists(data_path):
                makedirs(data_path)
            call("git clone --quiet {} {}".format(repo_path, app), cwd=APP_ROOT, shell=True)
        do_deploy(app, newrev=newrev)


@piku.command("git-receive-pack")
@argument('app')
def cmd_git_receive_pack(app):
    """INTERNAL: Handle git pushes for an app"""

    app = sanitize_app_name(app)
    hook_path = join(GIT_ROOT, app, 'hooks', 'post-receive')
    env = globals()
    env.update(locals())

    if not exists(hook_path):
        makedirs(dirname(hook_path))
        # Initialize the repository with a hook to this script
        call("git init --quiet --bare " + app, cwd=GIT_ROOT, shell=True)
        with open(hook_path, 'w') as h:
            h.write("""#!/usr/bin/env bash
set -e; set -o pipefail;
cat | PIKU_ROOT="{PIKU_ROOT:s}" {PIKU_SCRIPT:s} git-hook {app:s}""".format(**env))
        # Make the hook executable by our user
        chmod(hook_path, stat(hook_path).st_mode | S_IXUSR)
    # Handle the actual receive. We'll be called with 'git-hook' after it happens
    call('git-shell -c "{}" '.format(argv[1] + " '{}'".format(app)), cwd=GIT_ROOT, shell=True)


@piku.command("git-upload-pack")
@argument('app')
def cmd_git_upload_pack(app):
    """INTERNAL: Handle git upload pack for an app"""
    app = sanitize_app_name(app)
    env = globals()
    env.update(locals())
    # Handle the actual receive. We'll be called with 'git-hook' after it happens
    call('git-shell -c "{}" '.format(argv[1] + " '{}'".format(app)), cwd=GIT_ROOT, shell=True)


@piku.command("scp", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@pass_context
def cmd_scp(ctx):
    """Simple wrapper to allow scp to work."""
    call(" ".join(["scp"] + ctx.args), cwd=GIT_ROOT, shell=True)


def _get_plugin_commands(path):
    sys_path.append(abspath(path))

    cli_commands = []
    if isdir(path):
        for item in listdir(path):
            module_path = join(path, item)
            if isdir(module_path):
                try:
                    module = import_module(item)
                except Exception:
                    module = None
                if hasattr(module, 'cli_commands'):
                    cli_commands.append(module.cli_commands())

    return cli_commands


@piku.command("help")
@pass_context
def cmd_help(ctx):
    """display help for piku"""
    echo(ctx.parent.get_help())


@piku.command("update")
def cmd_update():
    """Update the piku cli"""
    echo("Updating piku...")

    with NamedTemporaryFile(mode="w") as f:
        tempfile = f.name
        cmd = """curl -sL -w %{{http_code}} {} -o {}""".format(PIKU_RAW_SOURCE_URL, tempfile)
        response = check_output(cmd.split(' '), stderr=STDOUT)
        http_code = response.decode('utf8').strip()
        if http_code == "200":
            copyfile(tempfile, PIKU_SCRIPT)
            echo("Update successful.")
        else:
            echo("Error updating piku - please check if {} is accessible from this machine.".format(PIKU_RAW_SOURCE_URL))
    echo("Done.")


if __name__ == '__main__':
    cli_commands = _get_plugin_commands(path=PIKU_PLUGIN_ROOT)
    cli_commands.append(piku)
    cli = CommandCollection(sources=cli_commands)
    cli()
