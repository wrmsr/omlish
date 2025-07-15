from ..interleave import interleave_content


def test_interleave():
    print(interleave_content(['hi', 'there'], '\n\n'))

    # from .squeeze import squeeze_content
    # print(interleave_content(['hi', ['there', [['foo', 'bar']]]], '\n\n'))
    # print(interleave_content(squeeze_content(['hi', ['there', [['foo', 'bar']]]]), '\n\n'))
