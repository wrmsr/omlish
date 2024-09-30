# typing_extensions hack
import sys
import os

import sublime_plugin
dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, 'libs'))  # needed so typing_extensions can be imported like `from typing_extensions import NotRequired`
# Add the following to LSP-pyright.sublime-settings
# {
#     "settings": {
#         "pyright.dev_environment": "sublime_text_38",
#         "python.analysis.extraPaths": [
#             "${folder}/libs"
#         ]
#     }
# }
# end of typing_extensions hack

# setup event loop
from event_loop import setup_event_loop, shutdown_event_loop

setup_event_loop()

class EventListener(sublime_plugin.EventListener):
    def on_exit(self) -> None:
        shutdown_event_loop()
# end of setup event loop