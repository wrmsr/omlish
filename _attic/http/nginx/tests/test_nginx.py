import pytest

from .. import configs as ngc
from .. import process as ngp


def test_config():
    cfg = ngc.ConfigItems.of([
        'abc;',
        'def;',
        ('ghi', [
            'a;',
            'b;',
            ('c', [
                'd;'
            ]),
        ]),
    ])
    print(cfg.render().getvalue())


@pytest.mark.xfail()
def test_nginx_process():
    with ngp.NginxProcess() as proc:
        print(proc._config.connect_timeout)
        print(proc.nginx_version)
        print(proc.nginx_cfg_args)
