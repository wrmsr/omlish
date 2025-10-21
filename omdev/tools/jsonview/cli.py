"""
TODO:
 - read from stdin
 - evaluate jmespath on server using extended engine
 - integrate with json tool
 - use omlish server and templates
 - vendor deps, serve local
 - update to https://github.com/josdejong/svelte-jsoneditor
"""
import argparse
import http.server
import json
import os
import socketserver
import sys
import threading
import typing as ta
import webbrowser

from omlish import check
from omlish import lang


##


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JSON Viewer</title>
  <link
    href="https://cdn.jsdelivr.net/npm/jsoneditor/dist/jsoneditor.min.css"
    rel="stylesheet"
    type="text/css"
  >
  <style>
{css_src}
  </style>
</head>

<body>
  <div class="input-area">
    <label for="jmespath-input">JMESPath:</label>
    <input
     type="text"
     id="jmespath-input"
     list="jmespath-history"
     placeholder="Enter JMESPath expression..."
     autocomplete="off"
    >
    <datalist id="jmespath-history"></datalist>
    <span id="error-message"></span>
  </div>
  <div id="jsoneditor"></div>

  <script src="https://cdn.jsdelivr.net/npm/jsoneditor@10.2.0/dist/jsoneditor.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jmespath@0.16.0/jmespath.min.js"></script>
  <script>
    const originalJsonData = {json_data};
  </script>
  <script>
{js_src}
  </script>
</body>

</html>
"""


def view_json(
        filepath: str,
        port: int,
        *,
        mode: ta.Literal['jsonl', 'json5', 'json', None] = None,
) -> None:
    if filepath == '-':
        filepath = '/dev/stdin'

    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'", file=sys.stderr)
        return

    try:
        with open(filepath, encoding='utf-8') as f:
            raw_content = f.read()
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON file. {e}', file=sys.stderr)
        return

    if mode is None:
        if filepath.endswith('.jsonl'):
            mode = 'json'
        elif filepath.endswith('.json5'):
            mode = 'json5'

    if mode == 'jsonl':
        json_content = [json.loads(sl) for l in raw_content.splitlines() if (sl := l.strip())]
    elif mode == 'json5':
        from omlish.formats import json5
        json_content = json5.loads(raw_content)
    elif mode in ('json', None):
        json_content = json.loads(raw_content)
    else:
        raise ValueError(mode)

    # Use compact dumps for embedding in JS, it's more efficient
    json_string = json.dumps(json_content)

    resources = lang.get_relative_resources('resources', globals=globals())
    css_src = resources['jsonview.css'].read_text()
    js_src = resources['jsonview.js'].read_text()

    class JsonViewerHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html_content = HTML_TEMPLATE.format(
                    css_src=css_src,
                    js_src=js_src,
                    json_data=json_string,
                )
                self.wfile.write(html_content.encode('utf-8'))
            else:
                super().do_GET()

    handler_cls = JsonViewerHttpRequestHandler
    with socketserver.TCPServer(('127.0.0.1', port), handler_cls) as httpd:
        url = f'http://127.0.0.1:{port}'
        print(f'Serving JSON file: {os.path.abspath(filepath)}', file=sys.stderr)
        print(f'Viewer running at: {url}', file=sys.stderr)
        print('Press Ctrl+C to stop the server.', file=sys.stderr)

        threading.Timer(1, lambda: webbrowser.open_new(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nShutting down server.', file=sys.stderr)
            httpd.shutdown()


def _main() -> None:
    parser = argparse.ArgumentParser(
        description='Launch a web-based JSON viewer with JMESPath transformations.',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        'filepath',
        help='The path to the JSON file you want to view.',
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=(default_port := 8999),
        help=f'The port to run the web server on. Defaults to {default_port}.',
    )
    parser.add_argument('-l', '--lines', action='store_true')
    parser.add_argument('-5', '--five', action='store_true')
    args = parser.parse_args()

    check.state(not (args.lines and args.five))

    view_json(
        args.filepath,
        args.port,
        mode='jsonl' if args.lines else 'json5' if args.five else None,
    )


if __name__ == '__main__':
    _main()
