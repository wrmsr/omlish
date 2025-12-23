from ..prepare import prepare_content_str
from ..sequence import BlockContent
from ..sequence import InlineContent


def test_materialize_sequences():
    c = InlineContent([
        BlockContent([
            'block 1 item 1\n',
            'block 1 item 2\n',
        ]),
        BlockContent([
            'block 2 item 1 ',
            'block 2 item 2',
        ]),
    ])

    print(prepare_content_str(c))
