import collections
import json
import os.path
import subprocess
import traceback
import urllib.request

import click

from .env import ACME_ROOT
from .env import ACME_ROOT_CA
from .env import ACME_WWW
from .env import CACHE_ROOT
from .env import NGINX_ROOT
from .utils import command_output
from .utils import expandvars
from .utils import get_boolean


# pylint: disable=anomalous-backslash-in-string
NGINX_TEMPLATE = """
$PIKU_INTERNAL_PROXY_CACHE_PATH
upstream $APP {
  server $NGINX_SOCKET;
}
server {
  listen              $NGINX_IPV6_ADDRESS:80;
  listen              $NGINX_IPV4_ADDRESS:80;

  location ^~ /.well-known/acme-challenge {
    allow all;
    root ${ACME_WWW};
  }
$PIKU_INTERNAL_NGINX_COMMON
}
"""

NGINX_HTTPS_ONLY_TEMPLATE = """
$PIKU_INTERNAL_PROXY_CACHE_PATH
upstream $APP {
  server $NGINX_SOCKET;
}
server {
  listen              $NGINX_IPV6_ADDRESS:80;
  listen              $NGINX_IPV4_ADDRESS:80;
  server_name         $NGINX_SERVER_NAME;

  location ^~ /.well-known/acme-challenge {
    allow all;
    root ${ACME_WWW};
  }

  location / {
    return 301 https://$server_name$request_uri;
  }
}

server {
$PIKU_INTERNAL_NGINX_COMMON
}
"""
# pylint: enable=anomalous-backslash-in-string

NGINX_COMMON_FRAGMENT = r"""
  listen              $NGINX_IPV6_ADDRESS:$NGINX_SSL;
  listen              $NGINX_IPV4_ADDRESS:$NGINX_SSL;
  ssl_certificate     $NGINX_ROOT/$APP.crt;
  ssl_certificate_key $NGINX_ROOT/$APP.key;
  server_name         $NGINX_SERVER_NAME;
  # These are not required under systemd - enable for debugging only
  # access_log        $LOG_ROOT/$APP/access.log;
  # error_log         $LOG_ROOT/$APP/error.log;

  # Enable gzip compression
  gzip on;
  gzip_proxied any;
  gzip_types text/plain text/xml text/css text/javascript text/js application/x-javascript application/javascript application/json application/xml+rss application/atom+xml image/svg+xml;
  gzip_comp_level 7;
  gzip_min_length 2048;
  gzip_vary on;
  gzip_disable "MSIE [1-6]\.(?!.*SV1)";
  # set a custom header for requests
  add_header X-Deployed-By Piku;

  $PIKU_INTERNAL_NGINX_CUSTOM_CLAUSES
  $PIKU_INTERNAL_NGINX_STATIC_MAPPINGS
  $PIKU_INTERNAL_NGINX_CACHE_MAPPINGS
  $PIKU_INTERNAL_NGINX_BLOCK_GIT
  $PIKU_INTERNAL_NGINX_PORTMAP
"""

NGINX_PORTMAP_FRAGMENT = """
  location    / {
    $PIKU_INTERNAL_NGINX_UWSGI_SETTINGS
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Remote-Address $remote_addr;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Request-Start $msec;
    $NGINX_ACL
  }
"""

NGINX_ACME_FIRSTRUN_TEMPLATE = """
server {
  listen              $NGINX_IPV6_ADDRESS:80;
  listen              $NGINX_IPV4_ADDRESS:80;
  server_name         $NGINX_SERVER_NAME;
  location ^~ /.well-known/acme-challenge {
    allow all;
    root ${ACME_WWW};
  }
}
"""

PIKU_INTERNAL_NGINX_STATIC_MAPPING = """
  location $static_url {
      sendfile on;
      sendfile_max_chunk 1m;
      tcp_nopush on;
      directio 8m;
      aio threads;
      alias $static_path;
      try_files $uri $uri.html $uri/ =404;
  }
"""

PIKU_INTERNAL_PROXY_CACHE_PATH = """
uwsgi_cache_path $cache_path levels=1:2 keys_zone=$app:20m inactive=$cache_time_expiry max_size=$cache_size use_temp_path=off;
"""

PIKU_INTERNAL_NGINX_CACHE_MAPPING = """
    location ~* ^/($cache_prefixes) {
        uwsgi_cache $APP;
        uwsgi_cache_min_uses 1;
        uwsgi_cache_key $host$uri;
        uwsgi_cache_valid 200 304 $cache_time_content;
        uwsgi_cache_valid 301 307 $cache_time_redirects;
        uwsgi_cache_valid 500 502 503 504 0s;
        uwsgi_cache_valid any $cache_time_any;
        uwsgi_hide_header Cache-Control;
        add_header Cache-Control "public, max-age=$cache_time_control";
        add_header X-Cache $upstream_cache_status;
        $PIKU_INTERNAL_NGINX_UWSGI_SETTINGS
    }
"""

PIKU_INTERNAL_NGINX_UWSGI_SETTINGS = """
    uwsgi_pass $APP;
    uwsgi_param QUERY_STRING $query_string;
    uwsgi_param REQUEST_METHOD $request_method;
    uwsgi_param CONTENT_TYPE $content_type;
    uwsgi_param CONTENT_LENGTH $content_length;
    uwsgi_param REQUEST_URI $request_uri;
    uwsgi_param PATH_INFO $document_uri;
    uwsgi_param DOCUMENT_ROOT $document_root;
    uwsgi_param SERVER_PROTOCOL $server_protocol;
    uwsgi_param X_FORWARDED_FOR $proxy_add_x_forwarded_for;
    uwsgi_param REMOTE_ADDR $remote_addr;
    uwsgi_param REMOTE_PORT $remote_port;
    uwsgi_param SERVER_ADDR $server_addr;
    uwsgi_param SERVER_PORT $server_port;
    uwsgi_param SERVER_NAME $server_name;
"""


def setup_nginx(
        app,
        env,
        workers,
        app_path,
):
    # Hack to get around ClickCommand
    env['NGINX_SERVER_NAME'] = env['NGINX_SERVER_NAME'].split(',')
    env['NGINX_SERVER_NAME'] = ' '.join(env['NGINX_SERVER_NAME'])

    nginx = command_output("nginx -V")
    nginx_ssl = "443 ssl"
    if "--with-http_v2_module" in nginx:
        nginx_ssl += " http2"
    elif "--with-http_spdy_module" in nginx and "nginx/1.6.2" not in nginx:  # avoid Raspbian bug
        nginx_ssl += " spdy"
    nginx_conf = os.path.join(NGINX_ROOT, "{}.conf".format(app))

    env.update({  # lgtm [py/modification-of-default-value]
        'NGINX_SSL': nginx_ssl,
        'NGINX_ROOT': NGINX_ROOT,
        'ACME_WWW': ACME_WWW,
    })

    # default to reverse proxying to the TCP port we picked
    env['PIKU_INTERNAL_NGINX_UWSGI_SETTINGS'] = 'proxy_pass http://{BIND_ADDRESS:s}:{PORT:s};'.format(**env)
    if 'wsgi' in workers:
        sock = os.path.join(NGINX_ROOT, "{}.sock".format(app))
        env['PIKU_INTERNAL_NGINX_UWSGI_SETTINGS'] = expandvars(PIKU_INTERNAL_NGINX_UWSGI_SETTINGS, env)
        env['NGINX_SOCKET'] = env['BIND_ADDRESS'] = "unix://" + sock
        if 'PORT' in env:
            del env['PORT']
    else:
        env['NGINX_SOCKET'] = "{BIND_ADDRESS:s}:{PORT:s}".format(**env)
        click.secho("-----> nginx will look for app '{}' on {}".format(app, env['NGINX_SOCKET']))

    domains = env['NGINX_SERVER_NAME'].split()
    domain = domains[0]
    issuefile = os.path.join(ACME_ROOT, domain, "issued-" + "-".join(domains))
    key, crt = [os.path.join(NGINX_ROOT, "{}.{}".format(app, x)) for x in ['key', 'crt']]
    if os.path.exists(os.path.join(ACME_ROOT, "acme.sh")):
        acme = ACME_ROOT
        www = ACME_WWW
        root_ca = ACME_ROOT_CA
        # if this is the first run there will be no nginx conf yet
        # create a basic conf stub just to serve the acme auth
        if not os.path.exists(nginx_conf):
            click.secho("-----> writing temporary nginx conf")
            buffer = expandvars(NGINX_ACME_FIRSTRUN_TEMPLATE, env)
            with open(nginx_conf, "w") as h:
                h.write(buffer)
        if not os.path.exists(key) or not os.path.exists(issuefile):
            click.secho("-----> getting letsencrypt certificate")
            certlist = " ".join(["-d {}".format(d) for d in domains])
            subprocess.call(
                (
                    '{acme:s}/acme.sh '
                    '--issue {certlist:s} '
                    '-w {www:s} '
                    '--server {root_ca:s}'
                ).format(**locals()),
                shell=True,
            )
            subprocess.call(
                (
                    '{acme:s}/acme.sh '
                    '--install-cert {certlist:s} '
                    '--key-file {key:s} '
                    '--fullchain-file {crt:s}'
                ).format(**locals()),
                shell=True,
            )
            if os.path.exists(os.path.join(ACME_ROOT, domain)) and not os.path.exists(os.path.join(ACME_WWW, app)):
                os.symlink(os.path.join(ACME_ROOT, domain), os.path.join(ACME_WWW, app))
            try:
                os.symlink("/dev/null", issuefile)
            except Exception:
                pass
        else:
            click.secho("-----> letsencrypt certificate already installed")

    # fall back to creating self-signed certificate if acme failed
    if not os.path.exists(key) or os.stat(crt).st_size == 0:
        click.secho("-----> generating self-signed certificate")
        subprocess.call(
            (
                'openssl req -new '
                '-newkey rsa:4096 '
                '-days 365 '
                '-nodes '
                '-x509 '
                '-subj "/C=US/ST=NY/L=New York/O=Piku/OU=Self-Signed/CN={domain:s}" '
                '-keyout {key:s} '
                '-out {crt:s}'
            ).format(**locals()),
            shell=True,
        )

    # restrict access to server from CloudFlare IP addresses
    acl = []
    if get_boolean(env.get('NGINX_CLOUDFLARE_ACL', 'false')):
        try:
            cf = json.loads(urllib.request.urlopen('https://api.cloudflare.com/client/v4/ips').read().decode("utf-8"))
            if cf['success'] is True:
                for i in cf['result']['ipv4_cidrs']:
                    acl.append("allow {};".format(i))
                if get_boolean(env.get('DISABLE_IPV6', 'false')):
                    for i in cf['result']['ipv6_cidrs']:
                        acl.append("allow {};".format(i))
                # allow access from controlling machine
                if 'SSH_CLIENT' in os.environ:
                    remote_ip = os.environ['SSH_CLIENT'].split()[0]
                    click.secho("-----> nginx ACL will include your IP ({})".format(remote_ip))
                    acl.append("allow {};".format(remote_ip))
                acl.extend(["allow 127.0.0.1;", "deny all;"])
        except Exception:
            cf = collections.defaultdict()
            click.secho("-----> Could not retrieve CloudFlare IP ranges: {}".format(traceback.format_exc()), fg="red")

    env['NGINX_ACL'] = " ".join(acl)

    env['PIKU_INTERNAL_NGINX_BLOCK_GIT'] = "" if env.get('NGINX_ALLOW_GIT_FOLDERS') else r"location ~ /\.git { deny all; }"

    env['PIKU_INTERNAL_PROXY_CACHE_PATH'] = ''
    env['PIKU_INTERNAL_NGINX_CACHE_MAPPINGS'] = ''

    # Get a mapping of /prefix1,/prefix2
    default_cache_path = os.path.join(CACHE_ROOT, app)
    if not os.path.exists(default_cache_path):
        os.makedirs(default_cache_path)

    try:
        cache_size = int(env.get('NGINX_CACHE_SIZE', '1'))
    except Exception:
        click.secho("=====> Invalid cache size, defaulting to 1GB")
        cache_size = 1
    cache_size = str(cache_size) + "g"

    try:
        cache_time_control = int(env.get('NGINX_CACHE_CONTROL', '3600'))
    except Exception:
        click.secho("=====> Invalid time for cache control, defaulting to 3600s")
        cache_time_control = 3600
    cache_time_control = str(cache_time_control)

    try:
        cache_time_content = int(env.get('NGINX_CACHE_TIME', '3600'))
    except Exception:
        click.secho("=====> Invalid cache time for content, defaulting to 3600s")
        cache_time_content = 3600
    cache_time_content = str(cache_time_content) + "s"

    try:
        cache_time_redirects = int(env.get('NGINX_CACHE_REDIRECTS', '3600'))
    except Exception:
        click.secho("=====> Invalid cache time for redirects, defaulting to 3600s")
        cache_time_redirects = 3600
    cache_time_redirects = str(cache_time_redirects) + "s"

    try:
        cache_time_any = int(env.get('NGINX_CACHE_ANY', '3600'))
    except Exception:
        click.secho("=====> Invalid cache expiry fallback, defaulting to 3600s")
        cache_time_any = 3600
    cache_time_any = str(cache_time_any) + "s"

    try:
        cache_time_expiry = int(env.get('NGINX_CACHE_EXPIRY', '86400'))
    except Exception:
        click.secho("=====> Invalid cache expiry, defaulting to 86400s")
        cache_time_expiry = 86400
    cache_time_expiry = str(cache_time_expiry) + "s"

    cache_prefixes = env.get('NGINX_CACHE_PREFIXES', '')
    cache_path = env.get('NGINX_CACHE_PATH', default_cache_path)

    if not os.path.exists(cache_path):
        click.secho("=====> Cache path {} does not exist, using default {}, be aware of disk usage.".format(cache_path, default_cache_path))
        cache_path = env.get(default_cache_path)

    if len(cache_prefixes):
        prefixes = []  # this will turn into part of /(path1|path2|path3)
        try:
            items = cache_prefixes.split(',')
            for item in items:
                if item[0] == '/':
                    prefixes.append(item[1:])
                else:
                    prefixes.append(item)
            cache_prefixes = "|".join(prefixes)
            click.secho("-----> nginx will cache /({}) prefixes up to {} or {} of disk space, with the following timings:".format(cache_prefixes, cache_time_expiry, cache_size))
            click.secho("-----> nginx will cache content for {}.".format(cache_time_content))
            click.secho("-----> nginx will cache redirects for {}.".format(cache_time_redirects))
            click.secho("-----> nginx will cache everything else for {}.".format(cache_time_any))
            click.secho("-----> nginx will send caching headers asking for {} seconds of public caching.".format(cache_time_control))
            env['PIKU_INTERNAL_PROXY_CACHE_PATH'] = expandvars(PIKU_INTERNAL_PROXY_CACHE_PATH, locals())
            env['PIKU_INTERNAL_NGINX_CACHE_MAPPINGS'] = expandvars(PIKU_INTERNAL_NGINX_CACHE_MAPPING, locals())
            env['PIKU_INTERNAL_NGINX_CACHE_MAPPINGS'] = expandvars(env['PIKU_INTERNAL_NGINX_CACHE_MAPPINGS'], env)
        except Exception as e:
            click.secho("Error {} in cache path spec: should be /prefix1:[,/prefix2], ignoring.".format(e))
            env['PIKU_INTERNAL_NGINX_CACHE_MAPPINGS'] = ''

    env['PIKU_INTERNAL_NGINX_STATIC_MAPPINGS'] = ''

    # Get a mapping of /prefix1:path1,/prefix2:path2
    static_paths = env.get('NGINX_STATIC_PATHS', '')

    # prepend static worker path if present
    if 'static' in workers:
        stripped = workers['static'].strip("/").rstrip("/")
        static_paths = ("/" if stripped[0:1] == ":" else "/:") + (stripped if stripped else ".") + "/" + (
            "," if static_paths else "") + static_paths
    if len(static_paths):
        try:
            items = static_paths.split(',')
            for item in items:
                static_url, static_path = item.split(':')
                if static_path[0] != '/':
                    static_path = os.path.join(app_path, static_path).rstrip("/") + "/"
                click.secho("-----> nginx will map {} to {}.".format(static_url, static_path))
                env['PIKU_INTERNAL_NGINX_STATIC_MAPPINGS'] = env['PIKU_INTERNAL_NGINX_STATIC_MAPPINGS'] + expandvars(PIKU_INTERNAL_NGINX_STATIC_MAPPING, locals())
        except Exception as e:
            click.secho("Error {} in static path spec: should be /prefix1:path1[,/prefix2:path2], ignoring.".format(e))
            env['PIKU_INTERNAL_NGINX_STATIC_MAPPINGS'] = ''

    env['PIKU_INTERNAL_NGINX_CUSTOM_CLAUSES'] = expandvars(open(os.path.join(app_path, env["NGINX_INCLUDE_FILE"])).read(), env) if env.get("NGINX_INCLUDE_FILE") else ""
    env['PIKU_INTERNAL_NGINX_PORTMAP'] = ""
    if 'web' in workers or 'wsgi' in workers:
        env['PIKU_INTERNAL_NGINX_PORTMAP'] = expandvars(NGINX_PORTMAP_FRAGMENT, env)
    env['PIKU_INTERNAL_NGINX_COMMON'] = expandvars(NGINX_COMMON_FRAGMENT, env)

    click.secho("-----> nginx will map app '{}' to hostname(s) '{}'".format(app, env['NGINX_SERVER_NAME']))
    if get_boolean(env.get('NGINX_HTTPS_ONLY', 'false')):
        buffer = expandvars(NGINX_HTTPS_ONLY_TEMPLATE, env)
        click.secho("-----> nginx will redirect all requests to hostname(s) '{}' to HTTPS".format(env['NGINX_SERVER_NAME']))
    else:
        buffer = expandvars(NGINX_TEMPLATE, env)

    # remove all references to IPv6 listeners (for enviroments where it's disabled)
    if get_boolean(env.get('DISABLE_IPV6', 'false')):
        buffer = '\n'.join([line for line in buffer.split('\n') if 'NGINX_IPV6' not in line])
    # change any unecessary uWSGI specific directives to standard proxy ones
    if 'wsgi' not in workers:
        buffer = buffer.replace("uwsgi_", "proxy_")

    # map Cloudflare connecting IP to REMOTE_ADDR
    if get_boolean(env.get('NGINX_CLOUDFLARE_ACL', 'false')):
        buffer = buffer.replace("REMOTE_ADDR $remote_addr", "REMOTE_ADDR $http_cf_connecting_ip")

    with open(nginx_conf, "w") as h:
        h.write(buffer)

    # prevent broken config from breaking other deploys
    try:
        nginx_config_test = str(subprocess.check_output("nginx -t 2>&1 | grep {}".format(app), env=os.environ, shell=True))
    except Exception:
        nginx_config_test = None
    if nginx_config_test:
        click.secho("Error: [nginx config] {}".format(nginx_config_test), fg='red')
        click.secho("Warning: removing broken nginx config.", fg='yellow')
        os.unlink(nginx_conf)
