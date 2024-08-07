from os import environ
from os.path import abspath
from os.path import join
from os.path import realpath


# === Make sure we can access all system binaries ===

if 'sbin' not in environ['PATH']:
    environ['PATH'] = "/usr/local/sbin:/usr/sbin:/sbin:" + environ['PATH']


# === Globals - all tweakable settings are here ===

PIKU_RAW_SOURCE_URL = "https://raw.githubusercontent.com/piku/piku/master/piku.py"
PIKU_ROOT = environ.get('PIKU_ROOT', join(environ['HOME'], '.piku'))
PIKU_BIN = join(environ['HOME'], 'bin')
PIKU_SCRIPT = realpath(__file__)
PIKU_PLUGIN_ROOT = abspath(join(PIKU_ROOT, "plugins"))
APP_ROOT = abspath(join(PIKU_ROOT, "apps"))
DATA_ROOT = abspath(join(PIKU_ROOT, "data"))
ENV_ROOT = abspath(join(PIKU_ROOT, "envs"))
GIT_ROOT = abspath(join(PIKU_ROOT, "repos"))
LOG_ROOT = abspath(join(PIKU_ROOT, "logs"))
NGINX_ROOT = abspath(join(PIKU_ROOT, "nginx"))
CACHE_ROOT = abspath(join(PIKU_ROOT, "cache"))
UWSGI_AVAILABLE = abspath(join(PIKU_ROOT, "uwsgi-available"))
UWSGI_ENABLED = abspath(join(PIKU_ROOT, "uwsgi-enabled"))
UWSGI_ROOT = abspath(join(PIKU_ROOT, "uwsgi"))
UWSGI_LOG_MAXSIZE = '1048576'
ACME_ROOT = environ.get('ACME_ROOT', join(environ['HOME'], '.acme.sh'))
ACME_WWW = abspath(join(PIKU_ROOT, "acme"))
ACME_ROOT_CA = environ.get('ACME_ROOT_CA', 'letsencrypt.org')


# === Make sure we can access piku user-installed binaries === #

if PIKU_BIN not in environ['PATH']:
    environ['PATH'] = PIKU_BIN + ":" + environ['PATH']
