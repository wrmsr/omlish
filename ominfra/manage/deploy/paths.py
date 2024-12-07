# ruff: noqa: UP006 UP007
"""
~deploy
  deploy.pid (flock)
  /app
    /<appspec> - shallow clone
  /conf
    /env
      <appspec>.env
    /nginx
      <appspec>.conf
    /supervisor
      <appspec>.conf
  /venv
    /<appspec>

?
  /logs
    /wrmsr--omlish--<spec>

spec = <name>--<rev>--<when>

==

for dn in [
    'app',
    'conf',
    'conf/env',
    'conf/nginx',
    'conf/supervisor',
    'venv',
]:
"""
