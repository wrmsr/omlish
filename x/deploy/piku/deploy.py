from glob import glob
from os import environ
from os import makedirs
from os import remove
from os import symlink
from os.path import abspath
from os.path import exists
from os.path import getmtime
from os.path import join
from shutil import copyfile
from subprocess import call
from subprocess import check_output
from sys import exit

from click import secho as echo

from .env import APP_ROOT
from .env import ENV_ROOT
from .env import LOG_ROOT
from .env import UWSGI_ENABLED
from .nginx import spawn_app
from .utils import check_requirements
from .utils import parse_procfile
from .utils import parse_settings


def found_app(kind):
    """Helper function to output app detected"""
    echo("-----> {} app detected.".format(kind), fg='green')
    return True


def do_deploy(app, deltas={}, newrev=None):
    """Deploy an app by resetting the work directory"""

    app_path = join(APP_ROOT, app)
    procfile = join(app_path, 'Procfile')
    log_path = join(LOG_ROOT, app)

    env = {'GIT_WORK_DIR': app_path}
    if exists(app_path):
        echo("-----> Deploying app '{}'".format(app), fg='green')
        call('git fetch --quiet', cwd=app_path, env=env, shell=True)
        if newrev:
            call('git reset --hard {}'.format(newrev), cwd=app_path, env=env, shell=True)
        call('git submodule init', cwd=app_path, env=env, shell=True)
        call('git submodule update', cwd=app_path, env=env, shell=True)
        if not exists(log_path):
            makedirs(log_path)
        workers = parse_procfile(procfile)
        if workers and len(workers) > 0:
            settings = {}
            if "preflight" in workers:
                echo("-----> Running preflight.", fg='green')
                retval = call(workers["preflight"], cwd=app_path, env=settings, shell=True)
                if retval:
                    echo("-----> Exiting due to preflight command error value: {}".format(retval))
                    exit(retval)
                workers.pop("preflight", None)
            if exists(join(app_path, 'requirements.txt')) and found_app("Python"):
                settings.update(deploy_python(app, deltas))
            elif exists(join(app_path, 'package.json')) and found_app("Node") and (check_requirements(['nodejs', 'npm']) or check_requirements(['node', 'npm']) or check_requirements(['nodeenv'])):
                settings.update(deploy_node(app, deltas))
            elif 'release' in workers and 'web' in workers:
                echo("-----> Generic app detected.", fg='green')
                settings.update(deploy_identity(app, deltas))
            elif 'static' in workers:
                echo("-----> Static app detected.", fg='green')
                settings.update(deploy_identity(app, deltas))
            else:
                echo("-----> Could not detect runtime!", fg='red')
            # TODO: detect other runtimes
            if "release" in workers:
                echo("-----> Releasing", fg='green')
                retval = call(workers["release"], cwd=app_path, env=settings, shell=True)
                if retval:
                    echo("-----> Exiting due to release command error value: {}".format(retval))
                    exit(retval)
                workers.pop("release", None)
        else:
            echo("Error: Invalid Procfile for app '{}'.".format(app), fg='red')
    else:
        echo("Error: app '{}' not found.".format(app), fg='red')


def deploy_node(app, deltas={}):
    """Deploy a Node  application"""

    virtualenv_path = join(ENV_ROOT, app)
    node_path = join(ENV_ROOT, app, "node_modules")
    node_modules_symlink = join(APP_ROOT, app, "node_modules")
    npm_prefix = abspath(join(node_path, ".."))
    env_file = join(APP_ROOT, app, 'ENV')
    deps = join(APP_ROOT, app, 'package.json')

    first_time = False
    if not exists(node_path):
        echo("-----> Creating node_modules for '{}'".format(app), fg='green')
        makedirs(node_path)
        first_time = True

    env = {
        'VIRTUAL_ENV': virtualenv_path,
        'NODE_PATH': node_path,
        'NPM_CONFIG_PREFIX': npm_prefix,
        "PATH": ':'.join([join(virtualenv_path, "bin"), join(node_path, ".bin"), environ['PATH']])
    }
    if exists(env_file):
        env.update(parse_settings(env_file, env))

    # include node binaries on our path
    environ["PATH"] = env["PATH"]

    version = env.get("NODE_VERSION")
    node_binary = join(virtualenv_path, "bin", "node")
    installed = check_output("{} -v".format(node_binary), cwd=join(APP_ROOT, app), env=env, shell=True).decode("utf8").rstrip("\n") if exists(node_binary) else ""

    if version and check_requirements(['nodeenv']):
        if not installed.endswith(version):
            started = glob(join(UWSGI_ENABLED, '{}*.ini'.format(app)))
            if installed and len(started):
                echo("Warning: Can't update node with app running. Stop the app & retry.", fg='yellow')
            else:
                echo("-----> Installing node version '{NODE_VERSION:s}' using nodeenv".format(**env), fg='green')
                call("nodeenv --prebuilt --node={NODE_VERSION:s} --clean-src --force {VIRTUAL_ENV:s}".format(**env), cwd=virtualenv_path, env=env, shell=True)
        else:
            echo("-----> Node is installed at {}.".format(version))

    if exists(deps) and check_requirements(['npm']):
        if first_time or getmtime(deps) > getmtime(node_path):
            copyfile(join(APP_ROOT, app, 'package.json'), join(ENV_ROOT, app, 'package.json'))
            if not exists(node_modules_symlink):
                symlink(node_path, node_modules_symlink)
            echo("-----> Running npm for '{}'".format(app), fg='green')
            call('npm install --prefix {} --package-lock=false'.format(npm_prefix), cwd=join(APP_ROOT, app), env=env, shell=True)
    return spawn_app(app, deltas)


def deploy_python(app, deltas={}):
    """Deploy a Python application"""

    virtualenv_path = join(ENV_ROOT, app)
    requirements = join(APP_ROOT, app, 'requirements.txt')
    env_file = join(APP_ROOT, app, 'ENV')
    # Set unbuffered output and readable UTF-8 mapping
    env = {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'UTF_8:replace'
    }
    if exists(env_file):
        env.update(parse_settings(env_file, env))

    # TODO: improve version parsing
    # pylint: disable=unused-variable
    version = int(env.get("PYTHON_VERSION", "3"))

    first_time = False
    if not exists(join(virtualenv_path, "bin", "activate")):
        echo("-----> Creating virtualenv for '{}'".format(app), fg='green')
        try:
            makedirs(virtualenv_path)
        except FileExistsError:
            echo("-----> Env dir already exists: '{}'".format(app), fg='yellow')
        call('virtualenv --python=python{version:d} {app:s}'.format(**locals()), cwd=ENV_ROOT, shell=True)
        first_time = True

    activation_script = join(virtualenv_path, 'bin', 'activate_this.py')
    exec(open(activation_script).read(), dict(__file__=activation_script))

    if first_time or getmtime(requirements) > getmtime(virtualenv_path):
        echo("-----> Running pip for '{}'".format(app), fg='green')
        call('pip install -r {}'.format(requirements), cwd=virtualenv_path, shell=True)
    return spawn_app(app, deltas)


def deploy_identity(app, deltas={}):
    env_path = join(ENV_ROOT, app)
    if not exists(env_path):
        makedirs(env_path)
    return spawn_app(app, deltas)


def do_stop(app):
    config = glob(join(UWSGI_ENABLED, '{}*.ini'.format(app)))

    if len(config) > 0:
        echo("Stopping app '{}'...".format(app), fg='yellow')
        for c in config:
            remove(c)
    else:
        echo("Error: app '{}' not deployed!".format(app), fg='red')  # TODO app could be already stopped. Need to able to tell the difference.


def do_restart(app):
    """Restarts a deployed app"""
    # This must work even if the app is stopped when called. At the end, the app should be running.
    echo("restarting app '{}'...".format(app), fg='yellow')
    do_stop(app)
    spawn_app(app)
