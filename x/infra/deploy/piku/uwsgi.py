import grp
import os.path
import pwd
import shutil

import click

from .env import UWSGI_AVAILABLE
from .env import UWSGI_LOG_MAXSIZE
from .env import APP_ROOT
from .env import ENV_ROOT
from .env import LOG_ROOT
from .env import NGINX_ROOT
from .env import UWSGI_ENABLED
from .utils import parse_settings


def spawn_worker(app, kind, command, env, ordinal=1):
    """Set up and deploy a single worker of a given kind"""

    # pylint: disable=unused-variable
    env['PROC_TYPE'] = kind
    env_path = os.path.join(ENV_ROOT, app)
    available = os.path.join(UWSGI_AVAILABLE, '{app:s}_{kind:s}.{ordinal:d}.ini'.format(**locals()))
    enabled = os.path.join(UWSGI_ENABLED, '{app:s}_{kind:s}.{ordinal:d}.ini'.format(**locals()))
    log_file = os.path.join(LOG_ROOT, app, kind)

    settings = [
        ('chdir', os.path.join(APP_ROOT, app)),
        ('uid', pwd.getpwuid(os.getuid()).pw_name),
        ('gid', grp.getgrgid(os.getgid()).gr_name),
        ('master', 'true'),
        ('project', app),
        ('max-requests', env.get('UWSGI_MAX_REQUESTS', '1024')),
        ('listen', env.get('UWSGI_LISTEN', '16')),
        ('processes', env.get('UWSGI_PROCESSES', '1')),
        ('procname-prefix', '{app:s}:{kind:s}:'.format(**locals())),
        ('enable-threads', env.get('UWSGI_ENABLE_THREADS', 'true').lower()),
        ('log-x-forwarded-for', env.get('UWSGI_LOG_X_FORWARDED_FOR', 'false').lower()),
        ('log-maxsize', env.get('UWSGI_LOG_MAXSIZE', UWSGI_LOG_MAXSIZE)),
        ('logfile-chown', '%s:%s' % (pwd.getpwuid(os.getuid()).pw_name, grp.getgrgid(os.getgid()).gr_name)),
        ('logfile-chmod', '640'),
        ('logto2', '{log_file:s}.{ordinal:d}.log'.format(**locals())),
        ('log-backupname', '{log_file:s}.{ordinal:d}.log.old'.format(**locals())),
    ]

    # only add virtualenv to uwsgi if it's a real virtualenv
    if os.path.exists(os.path.join(env_path, "bin", "activate_this.py")):
        settings.append(('virtualenv', env_path))

    if 'UWSGI_IDLE' in env:
        try:
            idle_timeout = int(env['UWSGI_IDLE'])
            settings.extend([
                ('idle', str(idle_timeout)),
                ('cheap', 'True'),
                ('die-on-idle', 'True')
            ])
            click.secho("-----> uwsgi will start workers on demand and kill them after {}s of inactivity".format(idle_timeout), fg='yellow')
        except Exception:
            click.secho("Error: malformed setting 'UWSGI_IDLE', ignoring it.".format(), fg='red')
            pass

    if kind == 'cron':
        settings.extend([
            ['cron', command.replace("*/", "-").replace("*", "-1")],
        ])

    python_version = int(env.get('PYTHON_VERSION', '3'))

    if kind == 'wsgi':
        settings.extend([
            ('module', command),
            ('threads', env.get('UWSGI_THREADS', '4')),
        ])

        settings.extend([
            ('plugin', 'python3'),
        ])
        if 'UWSGI_ASYNCIO' in env:
            try:
                tasks = int(env['UWSGI_ASYNCIO'])
                settings.extend([
                    ('plugin', 'asyncio_python3'),
                    ('async', tasks),
                ])
                click.secho("-----> uwsgi will support {} async tasks".format(tasks), fg='yellow')
            except ValueError:
                click.secho("Error: malformed setting 'UWSGI_ASYNCIO', ignoring it.".format(), fg='red')

        # If running under nginx, don't expose a port at all
        if 'NGINX_SERVER_NAME' in env:
            sock = os.path.join(NGINX_ROOT, "{}.sock".format(app))
            click.secho("-----> nginx will talk to uWSGI via {}".format(sock), fg='yellow')
            settings.extend([
                ('socket', sock),
                ('chmod-socket', '664'),
            ])
        else:
            click.secho("-----> nginx will talk to uWSGI via {BIND_ADDRESS:s}:{PORT:s}".format(**env), fg='yellow')
            settings.extend([
                ('http', '{BIND_ADDRESS:s}:{PORT:s}'.format(**env)),
                ('http-use-socket', '{BIND_ADDRESS:s}:{PORT:s}'.format(**env)),
                ('http-socket', '{BIND_ADDRESS:s}:{PORT:s}'.format(**env)),
            ])
    elif kind == 'web':
        click.secho("-----> nginx will talk to the 'web' process via {BIND_ADDRESS:s}:{PORT:s}".format(**env), fg='yellow')
        settings.append(('attach-daemon', command))
    elif kind == 'static':
        click.secho("-----> nginx serving static files only".format(**env), fg='yellow')
    elif kind == 'cron':
        click.secho("-----> uwsgi scheduled cron for {command}".format(**locals()), fg='yellow')
    else:
        settings.append(('attach-daemon', command))

    if kind in ['wsgi', 'web']:
        settings.append(('log-format', '%%(addr) - %%(user) [%%(ltime)] "%%(method) %%(uri) %%(proto)" %%(status) %%(size) "%%(referer)" "%%(uagent)" %%(msecs)ms'))

    # remove unnecessary variables from the env in nginx.ini
    for k in ['NGINX_ACL']:
        if k in env:
            del env[k]

    # insert user defined uwsgi settings if set
    settings += parse_settings(os.path.join(APP_ROOT, app, env.get("UWSGI_INCLUDE_FILE"))).items() if env.get("UWSGI_INCLUDE_FILE") else []

    for k, v in env.items():
        settings.append(('env', '{k:s}={v}'.format(**locals())))

    if kind != 'static':
        with open(available, 'w') as h:
            h.write('[uwsgi]\n')
            for k, v in settings:
                h.write("{k:s} = {v}\n".format(**locals()))

        shutil.copyfile(available, enabled)
