from ..chat import ResponseFormat
from ..chat import TEXT_RESPONSE_FORMAT
from ..models import TopK
from ..options import Options


def test_options():
    opts = Options(
        TopK(5),
        TEXT_RESPONSE_FORMAT,
    )
    print(opts)
