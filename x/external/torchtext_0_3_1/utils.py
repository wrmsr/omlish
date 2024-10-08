import csv

import requests
import tqdm


def reporthook(t):
    """https://github.com/tqdm/tqdm"""

    last_b = [0]

    def inner(b=1, bsize=1, tsize=None):
        """
        b: int, optional - Number of blocks just transferred [default: 1].
        bsize: int, optional - Size of each block (in tqdm units) [default: 1].
        tsize: int, optional - Total size (in tqdm units). If [default: None] remains unchanged.
        """

        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return inner


def download_from_url(url, path):
    """Download file, with logic (from tensor2tensor) for Google Drive"""

    def process_response(r):
        chunk_size = 16 * 1024
        total_size = int(r.headers.get('Content-length', 0))
        with open(path, "wb") as file:
            with tqdm.tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=1,
                    desc=path.split('/')[-1],
            ) as t:
                for chunk in r.iter_content(chunk_size):
                    if chunk:
                        file.write(chunk)
                        t.update(len(chunk))

    if 'drive.google.com' not in url:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            stream=True,
        )
        process_response(response)
        return

    print('downloading from Google Drive; may take a few minutes')
    confirm_token = None
    session = requests.Session()
    response = session.get(url, stream=True)
    for k, v in response.cookies.items():
        if k.startswith("download_warning"):
            confirm_token = v

    if confirm_token:
        url = url + "&confirm=" + confirm_token
        response = session.get(url, stream=True)

    process_response(response)


def unicode_csv_reader(unicode_csv_data, **kwargs):
    """
    Since the standard csv library does not handle unicode in Python 2, we need a wrapper.

    Borrowed and slightly modified from the Python docs: https://docs.python.org/2/library/csv.html#csv-examples
    """

    for line in csv.reader(unicode_csv_data, **kwargs):
        yield line


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
