from textual.app import App

from omlish import check


##


def setup_app_devtools(
        app: App,
        host: str = '127.0.0.1',
        port: int | None = None,
) -> bool:
    if app.devtools is not None:
        return False

    check.none(app._devtools_redirector)  # noqa

    try:
        from textual_dev.client import DevtoolsClient  # noqa
        from textual_dev.redirect_output import StdoutRedirector  # noqa
    except ImportError:
        # Dev dependencies not installed
        return False

    app.devtools = DevtoolsClient(
        host,
        port,
    )

    app._devtools_redirector = StdoutRedirector(app.devtools)  # noqa

    return True
