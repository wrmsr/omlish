import os.path
import shutil
import subprocess
import tempfile
import urllib.parse

from omlish import cached


TEST_DATA_DIR = 'lineitem_iceberg'
TEST_DATA_ZIP_URL = 'https://duckdb.org/data/iceberg_data.zip'


@cached.function(lock=True)
def get_test_data_dir() -> str:
    data_dir = os.path.join(os.path.dirname(__file__), '.data')
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    test_data_dir = os.path.join(data_dir, TEST_DATA_DIR)
    if not os.path.isdir(test_data_dir):
        tmp_dir = tempfile.mkdtemp()
        subprocess.check_output(
            ['wget', TEST_DATA_ZIP_URL],
            cwd=tmp_dir,
        )
        subprocess.check_output(
            ['unzip', urllib.parse.urlparse(TEST_DATA_ZIP_URL).path.split('/')[-1]],
            cwd=tmp_dir,
        )
        shutil.copytree(
            os.path.join(tmp_dir, 'data', 'iceberg', TEST_DATA_DIR),
            os.path.join(data_dir, TEST_DATA_DIR),
        )

    return test_data_dir


def _main():
    print(get_test_data_dir())


if __name__ == '__main__':
    _main()
