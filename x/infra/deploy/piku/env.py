import os.path


# === Make sure we can access all system binaries ===

if 'sbin' not in os.environ['PATH']:
    os.environ['PATH'] = "/usr/local/sbin:/usr/sbin:/sbin:" + os.environ['PATH']


# === Globals - all tweakable settings are here ===

PIKU_RAW_SOURCE_URL = "https://raw.githubusercontent.com/piku/piku/master/piku.py"
PIKU_ROOT = os.environ.get('PIKU_ROOT', os.path.join(os.environ['HOME'], '.piku'))
PIKU_BIN = os.path.join(os.environ['HOME'], 'bin')
PIKU_SCRIPT = os.path.realpath(__file__)
PIKU_PLUGIN_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "plugins"))
APP_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "apps"))
DATA_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "data"))
ENV_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "envs"))
GIT_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "repos"))
LOG_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "logs"))
NGINX_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "nginx"))
CACHE_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "cache"))
UWSGI_AVAILABLE = os.path.abspath(os.path.join(PIKU_ROOT, "uwsgi-available"))
UWSGI_ENABLED = os.path.abspath(os.path.join(PIKU_ROOT, "uwsgi-enabled"))
UWSGI_ROOT = os.path.abspath(os.path.join(PIKU_ROOT, "uwsgi"))
UWSGI_LOG_MAXSIZE = '1048576'
ACME_ROOT = os.environ.get('ACME_ROOT', os.path.join(os.environ['HOME'], '.acme.sh'))
ACME_WWW = os.path.abspath(os.path.join(PIKU_ROOT, "acme"))
ACME_ROOT_CA = os.environ.get('ACME_ROOT_CA', 'letsencrypt.org')


# === Make sure we can access piku user-installed binaries === #

if PIKU_BIN not in os.environ['PATH']:
    os.environ['PATH'] = PIKU_BIN + ":" + os.environ['PATH']
