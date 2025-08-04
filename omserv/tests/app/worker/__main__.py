if __name__ == '__main__':
    from .. import dbs
    from .. import shell
    from .inject import bind

    shell.run_shell(
        shell.bind_asgi_server(bind()),
        shell.bind_node_registrant(),
        dbs.bind_dbs(),
    )
