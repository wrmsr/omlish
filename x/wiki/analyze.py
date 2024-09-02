"""
https://www.mediawiki.org/wiki/Help:Export#Export_format

https://github.com/5j9/wikitextparser
https://github.com/tatuylonen/wikitextprocessor
https://github.com/earwig/mwparserfromhell

https://github.com/WillKoehrsen/wikipedia-data-science/blob/master/notebooks/Downloading%20and%20Parsing%20Wikipedia%20Articles.ipynb

https://en.wikipedia.org/wiki/Help:Wikitext
https://en.wikipedia.org/wiki/Wikipedia:Lua

==

if rev.text and '#invoke' in rev.text.text:
    import wikitextparser as wtp
    parsed = wtp.parse(rev.text.text)
    print(parsed)

    from wikitextprocessor import Wtp
    ctx = Wtp()
    ctx.start_page(page.title)
    tree = ctx.parse(rev.text.text)
    print(tree)

"""
import contextlib
import glob
import io
import os.path

import lz4.frame
from omlish import lang  # noqa
from omlish import marshal as msh  # noqa
from omlish.formats import json  # noqa

from . import models as mdl


LZ4_JSONL_DIR = os.path.expanduser('~/data/enwiki/json/')


def _main() -> None:
    for fn in glob.glob(os.path.join(LZ4_JSONL_DIR, '*.jsonl.lz4')):
        with contextlib.ExitStack() as es:
            f = es.enter_context(open(fn, 'rb'))
            zf = es.enter_context(lz4.frame.open(f))
            tw = io.TextIOWrapper(zf, 'utf-8')

            while (l := tw.readline()):
                page = msh.unmarshal(json.loads(l), mdl.Page)
                print(page)


if __name__ == '__main__':
    _main()
