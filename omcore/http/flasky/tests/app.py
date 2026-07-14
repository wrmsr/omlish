def run_app(flask) -> None:
    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        return f'Hello, World! Method: {flask.request.method}'

    app.run(port=8000)


##


def _main() -> None:
    import flask  # noqa

    run_app(flask)


if __name__ == '__main__':
    _main()
