from omlish import cached
from omdev.cache import data as dac


TEST_DATA_SPEC = dac.UrlSpec(
    'https://duckdb.org/data/iceberg_data.zip',
    actions=[dac.ExtractAction('iceberg_data.zip')],
)


@cached.function(lock=True)
def get_test_data_dir() -> str:
    return dac.default().get(TEST_DATA_SPEC)


def _main():
    print(get_test_data_dir())


if __name__ == '__main__':
    _main()
