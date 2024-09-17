from omdev import datacache as dac


DATA_SPEC = dac.GitCacheDataSpec(
    'https://github.com/starry91/NMT-Lab',
    rev='d439c27dd09f37688ce806c2bdd67d137ec62c86',
    subtrees=[
        'deu.txt',
        'fra.txt',
    ],
)


def _main() -> None:
    data_path = dac.default().get(DATA_SPEC)
    print(data_path)


if __name__ == '__main__':
    _main()
