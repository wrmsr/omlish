if __name__ == '__main__':
    from .. import shell
    from ..dbs import bind_dbs
    from ..secrets import bind_secrets
    from .inject import bind_app

    shell.run_shell(
        shell.bind_asgi_server(bind_app()),
        shell.bind_node_registrant(),
        bind_dbs(),
        bind_secrets(),
    )
