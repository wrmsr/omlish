#!/usr/bin/env python3
"""Piku Micro-PaaS"""
import fcntl
import glob
import grp
import importlib
import multiprocessing
import os.path
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback

import click

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


@click.group(context_settings=CONTEXT_SETTINGS)
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
    apps = os.listdir(APP_ROOT)
    if not apps:
        click.secho("There are no applications deployed.")
        return

    for a in apps:
        running = len(glob.glob(os.path.join(UWSGI_ENABLED, '{}*.ini'.format(a)))) != 0
        click.secho(('*' if running else ' ') + a, fg='green')


@piku.command("config")
@click.argument('app')
def cmd_config(app):
    """Show config, e.g.: piku config <app>"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'ENV')
    if os.path.exists(config_file):
        click.secho(open(config_file).read().strip(), fg='white')
    else:
        click.secho("Warning: app '{}' not deployed, no config found.".format(app), fg='yellow')


@piku.command("config:get")
@click.argument('app')
@click.argument('setting')
def cmd_config_get(app, setting):
    """e.g.: piku config:get <app> FOO"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'ENV')
    if os.path.exists(config_file):
        env = parse_settings(config_file)
        if setting in env:
            click.secho("{}".format(env[setting]), fg='white')
    else:
        click.secho("Warning: no active configuration for '{}'".format(app))


@piku.command("config:set")
@click.argument('app')
@click.argument('settings', nargs=-1)
def cmd_config_set(app, settings):
    """e.g.: piku config:set <app> FOO=bar BAZ=quux"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'ENV')
    env = parse_settings(config_file)
    for s in settings:
        try:
            k, v = map(lambda x: x.strip(), s.split("=", 1))
            env[k] = v
            click.secho("Setting {k:s}={v} for '{app:s}'".format(**locals()), fg='white')
        except Exception:
            click.secho("Error: malformed setting '{}'".format(s), fg='red')
            return
    write_config(config_file, env)
    do_deploy(app)


@piku.command("config:unset")
@click.argument('app')
@click.argument('settings', nargs=-1)
def cmd_config_unset(app, settings):
    """e.g.: piku config:unset <app> FOO"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'ENV')
    env = parse_settings(config_file)
    for s in settings:
        if s in env:
            del env[s]
            click.secho("Unsetting {} for '{}'".format(s, app), fg='white')
    write_config(config_file, env)
    do_deploy(app)


@piku.command("config:live")
@click.argument('app')
def cmd_config_live(app):
    """e.g.: piku config:live <app>"""

    app = exit_if_invalid(app)

    live_config = os.path.join(ENV_ROOT, app, 'LIVE_ENV')
    if os.path.exists(live_config):
        click.secho(open(live_config).read().strip(), fg='white')
    else:
        click.secho("Warning: app '{}' not deployed, no config found.".format(app), fg='yellow')


@piku.command("deploy")
@click.argument('app')
def cmd_deploy(app):
    """e.g.: piku deploy <app>"""

    app = exit_if_invalid(app)
    do_deploy(app)


@piku.command("destroy")
@click.argument('app')
def cmd_destroy(app):
    """e.g.: piku destroy <app>"""

    app = exit_if_invalid(app)

    # leave DATA_ROOT, since apps may create hard to reproduce data,
    # and CACHE_ROOT, since `nginx` will set permissions to protect it
    for p in [os.path.join(x, app) for x in [APP_ROOT, GIT_ROOT, ENV_ROOT, LOG_ROOT]]:
        if os.path.exists(p):
            click.secho("--> Removing folder '{}'".format(p), fg='yellow')
            shutil.rmtree(p)

    for p in [os.path.join(x, '{}*.ini'.format(app)) for x in [UWSGI_AVAILABLE, UWSGI_ENABLED]]:
        g = glob.glob(p)
        if len(g) > 0:
            for f in g:
                click.secho("--> Removing file '{}'".format(f), fg='yellow')
                os.remove(f)

    nginx_files = [os.path.join(NGINX_ROOT, "{}.{}".format(app, x)) for x in ['conf', 'sock', 'key', 'crt']]
    for f in nginx_files:
        if os.path.exists(f):
            click.secho("--> Removing file '{}'".format(f), fg='yellow')
            os.remove(f)

    acme_link = os.path.join(ACME_WWW, app)
    acme_certs = os.path.realpath(acme_link)
    if os.path.exists(acme_certs):
        click.secho("--> Removing folder '{}'".format(acme_certs), fg='yellow')
        shutil.rmtree(acme_certs)
        click.secho("--> Removing file '{}'".format(acme_link), fg='yellow')
        os.unlink(acme_link)

    # These come last to make sure they're visible
    for p in [os.path.join(x, app) for x in [DATA_ROOT, CACHE_ROOT]]:
        if os.path.exists(p):
            click.secho("==> Preserving folder '{}'".format(p), fg='red')


@piku.command("logs")
@click.argument('app')
@click.argument('process', nargs=1, default='*')
def cmd_logs(app, process):
    """Tail running logs, e.g: piku logs <app> [<process>]"""

    app = exit_if_invalid(app)

    logfiles = glob.glob(os.path.join(LOG_ROOT, app, process + '.*.log'))
    if len(logfiles) > 0:
        for line in multi_tail(app, logfiles):
            click.secho(line.strip(), fg='white')
    else:
        click.secho("No logs found for app '{}'.".format(app), fg='yellow')


@piku.command("ps")
@click.argument('app')
def cmd_ps(app):
    """Show process count, e.g: piku ps <app>"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'SCALING')
    if os.path.exists(config_file):
        click.secho(open(config_file).read().strip(), fg='white')
    else:
        click.secho("Error: no workers found for app '{}'.".format(app), fg='red')


@piku.command("ps:scale")
@click.argument('app')
@click.argument('settings', nargs=-1)
def cmd_ps_scale(app, settings):
    """e.g.: piku ps:scale <app> <proc>=<count>"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'SCALING')
    worker_count = {k: int(v) for k, v in parse_procfile(config_file).items()}
    deltas = {}
    for s in settings:
        try:
            k, v = map(lambda x: x.strip(), s.split("=", 1))
            c = int(v)  # check for integer value
            if c < 0:
                click.secho("Error: cannot scale type '{}' below 0".format(k), fg='red')
                return
            if k not in worker_count:
                click.secho("Error: worker type '{}' not present in '{}'".format(k, app), fg='red')
                return
            deltas[k] = c - worker_count[k]
        except Exception:
            click.secho("Error: malformed setting '{}'".format(s), fg='red')
            return
    do_deploy(app, deltas)


@piku.command("run")
@click.argument('app')
@click.argument('cmd', nargs=-1)
def cmd_run(app, cmd):
    """e.g.: piku run <app> ls -- -al"""

    app = exit_if_invalid(app)

    config_file = os.path.join(ENV_ROOT, app, 'LIVE_ENV')
    os.environ.update(parse_settings(config_file))
    for f in [sys.stdout, sys.stderr]:
        fl = fcntl.fcntl(f, fcntl.F_GETFL)
        fcntl.fcntl(f, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    p = subprocess.Popen(
        ' '.join(cmd),
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ,
        cwd=os.path.join(APP_ROOT, app),
        shell=True,
    )
    p.communicate()


@piku.command("restart")
@click.argument('app')
def cmd_restart(app):
    """Restart an app: piku restart <app>"""

    app = exit_if_invalid(app)

    do_restart(app)


@piku.command("setup")
def cmd_setup():
    """Initialize environment"""

    click.secho("Running in Python {}".format(".".join(map(str, sys.version_info))))

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
        if not os.path.exists(p):
            click.secho("Creating '{}'.".format(p), fg='green')
            os.makedirs(p)

    # Set up the uWSGI emperor config
    settings = [
        ('chdir', UWSGI_ROOT),
        ('emperor', UWSGI_ENABLED),
        ('log-maxsize', UWSGI_LOG_MAXSIZE),
        ('logto', os.path.join(UWSGI_ROOT, 'uwsgi.log')),
        ('log-backupname', os.path.join(UWSGI_ROOT, 'uwsgi.old.log')),
        ('socket', os.path.join(UWSGI_ROOT, 'uwsgi.sock')),
        ('uid', pwd.getpwuid(os.getuid()).pw_name),
        ('gid', grp.getgrgid(os.getgid()).gr_name),
        ('enable-threads', 'true'),
        ('threads', '{}'.format(multiprocessing.cpu_count() * 2)),
    ]
    with open(os.path.join(UWSGI_ROOT, 'uwsgi.ini'), 'w') as h:
        h.write('[uwsgi]\n')
        # pylint: disable=unused-variable
        for k, v in settings:
            h.write("{k:s} = {v}\n".format(**locals()))

    # mark this script as executable (in case we were invoked via interpreter)
    if not (os.stat(PIKU_SCRIPT).st_mode & stat.S_IXUSR):
        click.secho("Setting '{}' as executable.".format(PIKU_SCRIPT), fg='yellow')
        os.chmod(PIKU_SCRIPT, os.stat(PIKU_SCRIPT).st_mode | stat.S_IXUSR)


@piku.command("setup:ssh")
@click.argument('public_key_file')
def cmd_setup_ssh(public_key_file):
    """Set up a new SSH key (use - for stdin)"""

    def add_helper(key_file):
        if os.path.exists(key_file):
            try:
                fingerprint = str(subprocess.check_output('ssh-keygen -lf ' + key_file, shell=True)).split(' ', 4)[1]
                key = open(key_file, 'r').read().strip()
                click.secho("Adding key '{}'.".format(fingerprint), fg='white')
                setup_authorized_keys(fingerprint, PIKU_SCRIPT, key)
            except Exception:
                click.secho("Error: invalid public key file '{}': {}".format(key_file, traceback.format_exc()), fg='red')
        elif public_key_file == '-':
            buffer = "".join(sys.stdin.readlines())
            with tempfile.NamedTemporaryFile(mode="w") as f:
                f.write(buffer)
                f.flush()
                add_helper(f.name)
        else:
            click.secho("Error: public key file '{}' not found.".format(key_file), fg='red')

    add_helper(public_key_file)


@piku.command("stop")
@click.argument('app')
def cmd_stop(app):
    """Stop an app, e.g: piku stop <app>"""

    app = exit_if_invalid(app)
    do_stop(app)


# --- Internal commands ---


@piku.command("git-hook")
@click.argument('app')
def cmd_git_hook(app):
    """INTERNAL: Post-receive git hook"""

    app = sanitize_app_name(app)
    repo_path = os.path.join(GIT_ROOT, app)
    app_path = os.path.join(APP_ROOT, app)
    data_path = os.path.join(DATA_ROOT, app)

    for line in sys.stdin:
        # pylint: disable=unused-variable
        oldrev, newrev, refname = line.strip().split(" ")
        # Handle pushes
        if not os.path.exists(app_path):
            click.secho("-----> Creating app '{}'".format(app), fg='green')
            os.makedirs(app_path)
            # The data directory may already exist, since this may be a full redeployment (we never delete data since it
            # may be expensive to recreate)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            subprocess.call("git clone --quiet {} {}".format(repo_path, app), cwd=APP_ROOT, shell=True)
        do_deploy(app, newrev=newrev)


@piku.command("git-receive-pack")
@click.argument('app')
def cmd_git_receive_pack(app):
    """INTERNAL: Handle git pushes for an app"""

    app = sanitize_app_name(app)
    hook_path = os.path.join(GIT_ROOT, app, 'hooks', 'post-receive')
    env = globals()
    env.update(locals())

    if not os.path.exists(hook_path):
        os.makedirs(os.path.dirname(hook_path))
        # Initialize the repository with a hook to this script
        subprocess.call("git init --quiet --bare " + app, cwd=GIT_ROOT, shell=True)
        with open(hook_path, 'w') as h:
            h.write("""#!/usr/bin/env bash
set -e; set -o pipefail;
cat | PIKU_ROOT="{PIKU_ROOT:s}" {PIKU_SCRIPT:s} git-hook {app:s}""".format(**env))
        # Make the hook executable by our user
        os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR)
    # Handle the actual receive. We'll be called with 'git-hook' after it happens
    subprocess.call('git-shell -c "{}" '.format(sys.argv[1] + " '{}'".format(app)), cwd=GIT_ROOT, shell=True)


@piku.command("git-upload-pack")
@click.argument('app')
def cmd_git_upload_pack(app):
    """INTERNAL: Handle git upload pack for an app"""

    app = sanitize_app_name(app)
    env = globals()
    env.update(locals())
    # Handle the actual receive. We'll be called with 'git-hook' after it happens
    subprocess.call('git-shell -c "{}" '.format(sys.argv[1] + " '{}'".format(app)), cwd=GIT_ROOT, shell=True)


@piku.command("scp", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def cmd_scp(ctx):
    """Simple wrapper to allow scp to work."""

    subprocess.call(" ".join(["scp"] + ctx.args), cwd=GIT_ROOT, shell=True)


def _get_plugin_commands(path):
    sys.path.append(os.path.abspath(path))

    cli_commands = []
    if os.path.isdir(path):
        for item in os.listdir(path):
            module_path = os.path.join(path, item)
            if os.path.isdir(module_path):
                try:
                    module = importlib.import_module(item)
                except Exception:
                    module = None
                if hasattr(module, 'cli_commands'):
                    cli_commands.append(module.cli_commands())

    return cli_commands


@piku.command("help")
@click.pass_context
def cmd_help(ctx):
    """display help for piku"""

    click.secho(ctx.parent.get_help())


@piku.command("update")
def cmd_update():
    """Update the piku cli"""

    click.secho("Updating piku...")

    with tempfile.NamedTemporaryFile(mode="w") as f:
        tf = f.name
        cmd = """curl -sL -w %{{http_code}} {} -o {}""".format(PIKU_RAW_SOURCE_URL, tf)
        response = subprocess.check_output(cmd.split(' '), stderr=subprocess.STDOUT)
        http_code = response.decode('utf8').strip()
        if http_code == "200":
            shutil.copyfile(tf, PIKU_SCRIPT)
            click.secho("Update successful.")
        else:
            click.secho("Error updating piku - please check if {} is accessible from this machine.".format(PIKU_RAW_SOURCE_URL))
    click.secho("Done.")


if __name__ == '__main__':
    cli_commands = _get_plugin_commands(path=PIKU_PLUGIN_ROOT)
    cli_commands.append(piku)
    cli = click.CommandCollection(sources=cli_commands)
    cli()
