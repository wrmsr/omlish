import pytest

from .. import triotp2 as t2


class SampleData:
    def __init__(self):
        self.count = 0


@pytest.fixture
def test_data():
    return SampleData()


class sample_app(t2.App):
    __name__ = 'sample_app'

    async def start(self, test_data):
        test_data.count += 1


def test_node_run(test_data):
    t2.node_run(
        [
            t2.AppSpec(
                app=sample_app(),
                start_arg=test_data,
                permanent=False,
            )
        ]
    )

    assert test_data.count == 1
