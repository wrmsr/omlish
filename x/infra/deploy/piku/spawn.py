import collections
import glob
import os.path

import click

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
    app_path = os.path.join(APP_ROOT, app)
    procfile = os.path.join(app_path, 'Procfile')
    workers = parse_procfile(procfile)
    workers.pop("preflight", None)
    workers.pop("release", None)
    ordinals = collections.defaultdict(lambda: 1)
    worker_count = {k: 1 for k in workers.keys()}

    # the Python virtualenv
    virtualenv_path = os.path.join(ENV_ROOT, app)

    # Settings shipped with the app
    env_file = os.path.join(APP_ROOT, app, 'ENV')

    # Custom overrides
    settings = os.path.join(ENV_ROOT, app, 'ENV')

    # Live settings
    live = os.path.join(ENV_ROOT, app, 'LIVE_ENV')

    # Scaling
    scaling = os.path.join(ENV_ROOT, app, 'SCALING')

    # Bootstrap environment
    env = {
        'APP': app,
        'LOG_ROOT': LOG_ROOT,
        'HOME': os.environ['HOME'],
        'USER': os.environ['USER'],
        'PATH': ':'.join([os.path.join(virtualenv_path, 'bin'), os.environ['PATH']]),
        'PWD': os.path.dirname(env_file),
        'VIRTUAL_ENV': virtualenv_path,
    }

    safe_defaults = {
        'NGINX_IPV4_ADDRESS': '0.0.0.0',
        'NGINX_IPV6_ADDRESS': '[::]',
        'BIND_ADDRESS': '127.0.0.1',
    }

    # add node path if present
    node_path = os.path.join(virtualenv_path, "node_modules")
    if os.path.exists(node_path):
        env["NODE_PATH"] = node_path
        env["PATH"] = ':'.join([os.path.join(node_path, ".bin"), env['PATH']])

    # Load environment variables shipped with repo (if any)
    if os.path.exists(env_file):
        env.update(parse_settings(env_file, env))

    # Override with custom settings (if any)
    if os.path.exists(settings):
        env.update(parse_settings(settings, env))  # lgtm [py/modification-of-default-value]

    if 'web' in workers or 'wsgi' in workers or 'static' in workers:
        # Pick a port if none defined
        if 'PORT' not in env:
            env['PORT'] = str(get_free_port())
            click.secho("-----> picking free port {PORT}".format(**env))

        if get_boolean(env.get('DISABLE_IPV6', 'false')):
            safe_defaults.pop('NGINX_IPV6_ADDRESS', None)
            click.secho("-----> nginx will NOT use IPv6".format(**locals()))

        # Safe defaults for addressing
        for k, v in safe_defaults.items():
            if k not in env:
                click.secho("-----> nginx {k:s} will be set to {v}".format(**locals()))
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
    if os.path.exists(scaling):
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
        config = glob.glob(os.path.join(UWSGI_ENABLED, '{}*.ini'.format(app)))
        if len(config):
            click.secho("-----> Removing uwsgi configs to trigger auto-restart.")
            for c in config:
                os.remove(c)

    # Create new workers
    for k, v in to_create.items():
        for w in v:
            enabled = os.path.join(UWSGI_ENABLED, '{app:s}_{k:s}.{w:d}.ini'.format(**locals()))
            if not os.path.exists(enabled):
                click.secho("-----> spawning '{app:s}:{k:s}.{w:d}'".format(**locals()), fg='green')
                spawn_worker(app, k, workers[k], env, w)

    # Remove unnecessary workers (leave logfiles)
    for k, v in to_destroy.items():
        for w in v:  # lgtm [py/unused-loop-variable]
            enabled = os.path.join(UWSGI_ENABLED, '{app:s}_{k:s}.{w:d}.ini'.format(**locals()))
            if os.path.exists(enabled):
                click.secho("-----> terminating '{app:s}:{k:s}.{w:d}'".format(**locals()), fg='yellow')
                os.unlink(enabled)

    return env
