from ...sequence import BlocksContent
from ...sequence import ConcatContent
from ...tag import TagContent  # noqa
from ..prepare import prepare_content_str  # noqa


def test_materialize_sequences():
    c = ConcatContent([  # noqa
        BlocksContent([
            'block 1 item 1\n',
            'block 1 item 2\n',
        ]),
        BlocksContent([
            'block 2 item 1 ',
            'block 2 item 2',
        ]),
        # TagContent('tag1', BlockContent([
        #     'block 3 item 1 ',
        #     'block 3 item 2',
        # ])),
    ])

    # print(prepare_content_str(c))
