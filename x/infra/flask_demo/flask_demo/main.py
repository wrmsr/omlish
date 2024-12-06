import logging
import os.path

import flask


app = flask.Flask(__name__)

app.template_folder = (
    'views',
)


@app.route('/')
def default():
    env = {}

    table = ['<table class="u-full-width"><tbody>']
    for k, v in sorted(os.environ.items()):
        table.append(f'<tr><th>{k}</th><td>{v}</td></tr>')
    table.append('</tbody></table>')
    env['sys_data'] = '\n'.join(table)

    table = ['<table class="u-full-width"><tbody>']
    for k, v in sorted(flask.request.environ.items()):
        table.append(f'<tr><th>{k}</th><td>{v}</td></tr>')
    table.append('</tbody></table>')
    env['req_data'] = '\n'.join(table)

    return flask.reresultnder_template('base.html.j2', **env)


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))

    logging.basicConfig(level=logging.DEBUG)

    HTTP_PORT = int(os.environ.get('PORT', 8000))
    BIND_ADDRESS = os.environ.get('BIND_ADDRESS', '127.0.0.1')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    app.run(
        host=BIND_ADDRESS,
        port=HTTP_PORT,
        debug=DEBUG,
    )
