"""
TODO:
 - dep-updates equiv
  - https://hub.docker.com/v2/repositories/bkuhl/game-watcher/tags
"""
import typing as ta  # noqa

from ... import lang
from ...serde.formats import yaml


def reorder_cfg_service_ports(cfg: dict) -> dict:
    return cfg


def test_compose():
    with open('docker/docker-compose.yml') as r:
        buf = r.read()

    import io
    import pprint

    import yaml as yaml_

    class CommentToken(yaml_.tokens.Token):
        id = '#'

    class CommentWrappedLoader(yaml.WrappedLoaders.Full):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self._pending_comment_tokens = []
            self._comment_token_lists_by_start_mark = {}

        def scan_to_next_token(self):
            # We ignore spaces, line breaks and comments.
            # If we find a line break in the block context, we set the flag
            # `allow_simple_key` on.
            # The byte order mark is stripped if it's the first character in the
            # stream. We do not yet support BOM inside the stream as the
            # specification requires. Any such mark will be considered as a part
            # of the document.
            #
            # TODO: We need to make tab handling rules more sane. A good rule is
            #   Tabs cannot precede tokens
            #   BLOCK-SEQUENCE-START, BLOCK-MAPPING-START, BLOCK-END,
            #   KEY(block), VALUE(block), BLOCK-ENTRY
            # So the checking code is
            #   if <TAB>:
            #       self.allow_simple_keys = False
            # We also need to add the check for `allow_simple_keys == True` to
            # `unwind_indent` before issuing BLOCK-END.
            # Scanners for block, flow, and plain scalars need to be modified.

            if self.index == 0 and self.peek() == '\uFEFF':
                self.forward()
            found = False
            while not found:
                while self.peek() == ' ':
                    self.forward()
                if self.peek() == '#':
                    start_mark = self.get_mark()
                    while self.peek() not in '\0\r\n\x85\u2028\u2029':
                        self.forward()
                    end_mark = self.get_mark()
                    if end_mark.buffer is not start_mark.buffer:
                        raise RuntimeError
                    self._pending_comment_tokens.append(CommentToken(start_mark, end_mark))
                if self.scan_line_break():
                    if not self.flow_level:
                        self.allow_simple_key = True
                else:
                    found = True

        def fetch_more_tokens(self):
            super().fetch_more_tokens()
            if self.tokens and self._pending_comment_tokens:
                self._comment_token_lists_by_start_mark[self.tokens[0].start_mark] = self._pending_comment_tokens
                self._pending_comment_tokens = []

    with lang.disposing(CommentWrappedLoader(io.StringIO(buf))) as loader:
        wcfg = loader.get_single_data()
    pprint.pprint(wcfg)

    cfg = yaml.full_load(buf)
    pprint.pprint(cfg)

    rocfg = reorder_cfg_service_ports(cfg)
    pprint.pprint(rocfg)

    print(yaml_.dump(rocfg, default_flow_style=False))
