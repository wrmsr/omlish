import glob
import os.path
import shutil
import subprocess
import sys

import click

from .env import APP_ROOT
from .env import ENV_ROOT
from .env import LOG_ROOT
from .env import UWSGI_ENABLED
from .spawn import spawn_app
from .utils import check_requirements
from .utils import parse_procfile
from .utils import parse_settings


def found_app(kind):
    """Helper function to output app detected"""
    click.secho("-----> {} app detected.".format(kind), fg='green')
    return True


def do_deploy(app, deltas={}, newrev=None):
    """Deploy an app by resetting the work directory"""

    app_path = os.path.join(APP_ROOT, app)
    procfile = os.path.join(app_path, 'Procfile')
    log_path = os.path.join(LOG_ROOT, app)

    env = {'GIT_WORK_DIR': app_path}
    if os.path.exists(app_path):
        click.secho("-----> Deploying app '{}'".format(app), fg='green')

        subprocess.call('git fetch --quiet', cwd=app_path, env=env, shell=True)
        if newrev:
            subprocess.call('git reset --hard {}'.format(newrev), cwd=app_path, env=env, shell=True)
        subprocess.call('git submodule init', cwd=app_path, env=env, shell=True)
        subprocess.call('git submodule update', cwd=app_path, env=env, shell=True)

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        workers = parse_procfile(procfile)
        if workers and len(workers) > 0:
            settings = {}

            if "preflight" in workers:
                click.secho("-----> Running preflight.", fg='green')
                retval = subprocess.call(workers["preflight"], cwd=app_path, env=settings, shell=True)
                if retval:
                    click.secho("-----> Exiting due to preflight command error value: {}".format(retval))
                    sys.exit(retval)
                workers.pop("preflight", None)

            if os.path.exists(os.path.join(app_path, 'requirements.txt')) and found_app("Python"):
                settings.update(deploy_python(app, deltas))

            elif (
                os.path.exists(os.path.join(app_path, 'package.json')) and
                found_app("Node") and
                (
                    check_requirements(['nodejs', 'npm']) or
                    check_requirements(['node', 'npm']) or
                    check_requirements(['nodeenv'])
                )
            ):
                settings.update(deploy_node(app, deltas))

            elif 'release' in workers and 'web' in workers:
                click.secho("-----> Generic app detected.", fg='green')
                settings.update(deploy_identity(app, deltas))

            elif 'static' in workers:
                click.secho("-----> Static app detected.", fg='green')
                settings.update(deploy_identity(app, deltas))

            else:
                click.secho("-----> Could not detect runtime!", fg='red')

            # TODO: detect other runtimes
            if "release" in workers:
                click.secho("-----> Releasing", fg='green')
                retval = subprocess.call(workers["release"], cwd=app_path, env=settings, shell=True)
                if retval:
                    click.secho("-----> Exiting due to release command error value: {}".format(retval))
                    sys.exit(retval)
                workers.pop("release", None)

        else:
            click.secho("Error: Invalid Procfile for app '{}'.".format(app), fg='red')

    else:
        click.secho("Error: app '{}' not found.".format(app), fg='red')


def deploy_node(app, deltas={}):
    """Deploy a Node  application"""

    virtualenv_path = os.path.join(ENV_ROOT, app)
    node_path = os.path.join(ENV_ROOT, app, "node_modules")
    node_modules_symlink = os.path.join(APP_ROOT, app, "node_modules")
    npm_prefix = os.path.abspath(os.path.join(node_path, ".."))
    env_file = os.path.join(APP_ROOT, app, 'ENV')
    deps = os.path.join(APP_ROOT, app, 'package.json')

    first_time = False
    if not os.path.exists(node_path):
        click.secho("-----> Creating node_modules for '{}'".format(app), fg='green')
        os.makedirs(node_path)
        first_time = True

    env = {
        'VIRTUAL_ENV': virtualenv_path,
        'NODE_PATH': node_path,
        'NPM_CONFIG_PREFIX': npm_prefix,
        "PATH": ':'.join([os.path.join(virtualenv_path, "bin"), os.path.join(node_path, ".bin"), os.environ['PATH']])
    }
    if os.path.exists(env_file):
        env.update(parse_settings(env_file, env))

    # include node binaries on our path
    os.environ["PATH"] = env["PATH"]

    version = env.get("NODE_VERSION")
    node_binary = os.path.join(virtualenv_path, "bin", "node")
    installed = subprocess.check_output(
        "{} -v".format(node_binary),
        cwd=os.path.join(APP_ROOT, app),
        env=env,
        shell=True,
    ).decode("utf8").rstrip("\n") if os.path.exists(node_binary) else ""

    if version and check_requirements(['nodeenv']):
        if not installed.endswith(version):
            started = glob.glob(os.path.join(UWSGI_ENABLED, '{}*.ini'.format(app)))
            if installed and len(started):
                click.secho("Warning: Can't update node with app running. Stop the app & retry.", fg='yellow')
            else:
                click.secho("-----> Installing node version '{NODE_VERSION:s}' using nodeenv".format(**env), fg='green')
                subprocess.call(
                    "nodeenv --prebuilt --node={NODE_VERSION:s} --clean-src --force {VIRTUAL_ENV:s}".format(**env),
                    cwd=virtualenv_path,
                    env=env,
                    shell=True,
                )
        else:
            click.secho("-----> Node is installed at {}.".format(version))

    if os.path.exists(deps) and check_requirements(['npm']):
        if first_time or os.path.getmtime(deps) > os.path.getmtime(node_path):
            shutil.copyfile(os.path.join(APP_ROOT, app, 'package.json'), os.path.join(ENV_ROOT, app, 'package.json'))
            if not os.path.exists(node_modules_symlink):
                os.symlink(node_path, node_modules_symlink)
            click.secho("-----> Running npm for '{}'".format(app), fg='green')
            subprocess.call(
                'npm install --prefix {} --package-lock=false'.format(npm_prefix),
                cwd=os.path.join(APP_ROOT, app),
                env=env,
                shell=True,
            )
    return spawn_app(app, deltas)


def deploy_python(app, deltas={}):
    """Deploy a Python application"""

    virtualenv_path = os.path.join(ENV_ROOT, app)
    requirements = os.path.join(APP_ROOT, app, 'requirements.txt')
    env_file = os.path.join(APP_ROOT, app, 'ENV')
    # Set unbuffered output and readable UTF-8 mapping
    env = {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'UTF_8:replace'
    }
    if os.path.exists(env_file):
        env.update(parse_settings(env_file, env))

    # TODO: improve version parsing
    # pylint: disable=unused-variable
    version = int(env.get("PYTHON_VERSION", "3"))

    first_time = False
    if not os.path.exists(os.path.join(virtualenv_path, "bin", "activate")):
        click.secho("-----> Creating virtualenv for '{}'".format(app), fg='green')
        try:
            os.makedirs(virtualenv_path)
        except FileExistsError:
            click.secho("-----> Env dir already exists: '{}'".format(app), fg='yellow')
        subprocess.call('virtualenv --python=python{version:d} {app:s}'.format(**locals()), cwd=ENV_ROOT, shell=True)
        first_time = True

    activation_script = os.path.join(virtualenv_path, 'bin', 'activate_this.py')
    exec(open(activation_script).read(), dict(__file__=activation_script))

    if first_time or os.path.getmtime(requirements) > os.path.getmtime(virtualenv_path):
        click.secho("-----> Running pip for '{}'".format(app), fg='green')
        subprocess.call('pip install -r {}'.format(requirements), cwd=virtualenv_path, shell=True)
    return spawn_app(app, deltas)


def deploy_identity(app, deltas={}):
    env_path = os.path.join(ENV_ROOT, app)
    if not os.path.exists(env_path):
        os.makedirs(env_path)
    return spawn_app(app, deltas)


def do_stop(app):
    config = glob.glob(os.path.join(UWSGI_ENABLED, '{}*.ini'.format(app)))

    if len(config) > 0:
        click.secho("Stopping app '{}'...".format(app), fg='yellow')
        for c in config:
            os.remove(c)
    else:
        # TODO app could be already stopped. Need to able to tell the difference.
        click.secho("Error: app '{}' not deployed!".format(app), fg='red')


def do_restart(app):
    """Restarts a deployed app"""
    # This must work even if the app is stopped when called. At the end, the app should be running.
    click.secho("restarting app '{}'...".format(app), fg='yellow')
    do_stop(app)
    spawn_app(app)
