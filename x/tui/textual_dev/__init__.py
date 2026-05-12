"""
The Textual developer tools and previews.

====

help='Enable development mode.'
features = set(parse_features(environment.get('TEXTUAL', '')))
if dev:
    features.add('debug')
    features.add('devtools')
env['TEXTUAL'] = ','.join(sorted(features))

help=f'Host where the development console is running. Defaults to {DEVTOOLS_HOST}.',
environment['TEXTUAL_DEVTOOLS_HOST'] = str(host)

help=f'Port where the development console is running. Defaults to {DEVTOOLS_PORT}.',
environment['TEXTUAL_DEVTOOLS_PORT'] = str(port)

help='Comma separated keys to simulate press.',
environment['TEXTUAL_PRESS'] = str(press)

type=int, help='Take screenshot after DELAY seconds.',
environment['TEXTUAL_SCREENSHOT'] = str(screenshot)

help='The target location for the screenshot',
environment['TEXTUAL_SCREENSHOT_LOCATION'] = str(screenshot_path)

help='The filename for the screenshot',
environment['TEXTUAL_SCREENSHOT_FILENAME'] = str(screenshot_filename)

help='Show any return value on exit.',
environment['TEXTUAL_SHOW_RETURN'] = '1'
"""
