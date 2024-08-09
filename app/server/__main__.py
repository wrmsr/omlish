if __name__ == '__main__':
    from .. import dbs
    from .. import shell
    from .inject import bind_app

    shell.run_shell(
        shell.bind_asgi_server(bind_app()),
        shell.bind_node_registrant(),
        dbs.bind_dbs(),
    )
