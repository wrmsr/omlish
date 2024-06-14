from collections import defaultdict
from glob import glob
from os import environ
from os import remove
from os import unlink
from os.path import dirname
from os.path import exists
from os.path import join

from click import secho as echo

from .env import APP_ROOT
from .env import ENV_ROOT
from .env import LOG_ROOT
from .env import UWSGI_ENABLED
from .nginx import setup_nginx
from .utils import get_boolean
from .utils import get_free_port
from .utils import parse_procfile
from .utils import parse_settings
from .utils import write_config
from .uwsgi import spawn_worker


def spawn_app(app, deltas={}):
    """Create all workers for an app"""

    # pylint: disable=unused-variable
    app_path = join(APP_ROOT, app)
    procfile = join(app_path, 'Procfile')
    workers = parse_procfile(procfile)
    workers.pop("preflight", None)
    workers.pop("release", None)
    ordinals = defaultdict(lambda: 1)
    worker_count = {k: 1 for k in workers.keys()}

    # the Python virtualenv
    virtualenv_path = join(ENV_ROOT, app)

    # Settings shipped with the app
    env_file = join(APP_ROOT, app, 'ENV')

    # Custom overrides
    settings = join(ENV_ROOT, app, 'ENV')

    # Live settings
    live = join(ENV_ROOT, app, 'LIVE_ENV')

    # Scaling
    scaling = join(ENV_ROOT, app, 'SCALING')

    # Bootstrap environment
    env = {
        'APP': app,
        'LOG_ROOT': LOG_ROOT,
        'HOME': environ['HOME'],
        'USER': environ['USER'],
        'PATH': ':'.join([join(virtualenv_path, 'bin'), environ['PATH']]),
        'PWD': dirname(env_file),
        'VIRTUAL_ENV': virtualenv_path,
    }

    safe_defaults = {
        'NGINX_IPV4_ADDRESS': '0.0.0.0',
        'NGINX_IPV6_ADDRESS': '[::]',
        'BIND_ADDRESS': '127.0.0.1',
    }

    # add node path if present
    node_path = join(virtualenv_path, "node_modules")
    if exists(node_path):
        env["NODE_PATH"] = node_path
        env["PATH"] = ':'.join([join(node_path, ".bin"), env['PATH']])

    # Load environment variables shipped with repo (if any)
    if exists(env_file):
        env.update(parse_settings(env_file, env))

    # Override with custom settings (if any)
    if exists(settings):
        env.update(parse_settings(settings, env))  # lgtm [py/modification-of-default-value]

    if 'web' in workers or 'wsgi' in workers or 'static' in workers:
        # Pick a port if none defined
        if 'PORT' not in env:
            env['PORT'] = str(get_free_port())
            echo("-----> picking free port {PORT}".format(**env))

        if get_boolean(env.get('DISABLE_IPV6', 'false')):
            safe_defaults.pop('NGINX_IPV6_ADDRESS', None)
            echo("-----> nginx will NOT use IPv6".format(**locals()))

        # Safe defaults for addressing
        for k, v in safe_defaults.items():
            if k not in env:
                echo("-----> nginx {k:s} will be set to {v}".format(**locals()))
                env[k] = v

        # Set up nginx if we have NGINX_SERVER_NAME set
        if 'NGINX_SERVER_NAME' in env:
            setup_nginx(
                app,
                env,
                workers,
                app_path,
            )

    # Configured worker count
    if exists(scaling):
        worker_count.update({k: int(v) for k, v in parse_procfile(scaling).items() if k in workers})

    to_create = {}
    to_destroy = {}
    for k, v in worker_count.items():
        to_create[k] = range(1, worker_count[k] + 1)
        if k in deltas and deltas[k]:
            to_create[k] = range(1, worker_count[k] + deltas[k] + 1)
            if deltas[k] < 0:
                to_destroy[k] = range(worker_count[k], worker_count[k] + deltas[k], -1)
            worker_count[k] = worker_count[k] + deltas[k]

    # Cleanup env
    for k, v in list(env.items()):
        if k.startswith('PIKU_INTERNAL_'):
            del env[k]

    # Save current settings
    write_config(live, env)
    write_config(scaling, worker_count, ':')

    if get_boolean(env.get('PIKU_AUTO_RESTART', 'true')):
        config = glob(join(UWSGI_ENABLED, '{}*.ini'.format(app)))
        if len(config):
            echo("-----> Removing uwsgi configs to trigger auto-restart.")
            for c in config:
                remove(c)

    # Create new workers
    for k, v in to_create.items():
        for w in v:
            enabled = join(UWSGI_ENABLED, '{app:s}_{k:s}.{w:d}.ini'.format(**locals()))
            if not exists(enabled):
                echo("-----> spawning '{app:s}:{k:s}.{w:d}'".format(**locals()), fg='green')
                spawn_worker(app, k, workers[k], env, w)

    # Remove unnecessary workers (leave logfiles)
    for k, v in to_destroy.items():
        for w in v:  # lgtm [py/unused-loop-variable]
            enabled = join(UWSGI_ENABLED, '{app:s}_{k:s}.{w:d}.ini'.format(**locals()))
            if exists(enabled):
                echo("-----> terminating '{app:s}:{k:s}.{w:d}'".format(**locals()), fg='yellow')
                unlink(enabled)

    return env
