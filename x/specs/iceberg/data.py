from omlish import cached
from omdev.cache import data as dcache


TEST_DATA_SPEC = dcache.UrlSpec(
    'https://duckdb.org/data/iceberg_data.zip',
    headers={'User-Agent': 'Wget/1.24.5'},
    actions=[dcache.ExtractAction('iceberg_data.zip')],
)


@cached.function(lock=True)
def get_test_data_dir() -> str:
    return dcache.default().get(TEST_DATA_SPEC)


def _main():
    print(get_test_data_dir())


if __name__ == '__main__':
    _main()
