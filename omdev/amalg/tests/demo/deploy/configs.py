import dataclasses as dc


@dc.dataclass(frozen=True)
class DeployConfig:
    python_bin: str
    app_name: str
    repo_url: str
    revision: str
    requirements_txt: str
    entrypoint: str


@dc.dataclass(frozen=True)
class HostConfig:
    username: str = 'deploy'

    global_supervisor_conf_file_path: str = '/etc/supervisor/conf.d/supervisord.conf'
    global_nginx_conf_file_path: str = '/etc/nginx/sites-enabled/deploy.conf'
