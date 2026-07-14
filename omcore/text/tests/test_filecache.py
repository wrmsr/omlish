from ..filecache import TextFileCache


def test_text_file_cache() -> None:
    tfc = TextFileCache()
    e = tfc.get_entry(__file__)
    print(e.lines()[4])
