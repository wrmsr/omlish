from omdev.cache import data as dcache


DATA_SPEC = dcache.GitSpec(
    'https://github.com/starry91/NMT-Lab',
    rev='d439c27dd09f37688ce806c2bdd67d137ec62c86',
    subtrees=[
        'deu.txt',
        'fra.txt',
    ],
)


def _main() -> None:
    data_path = dcache.default().get(DATA_SPEC)
    print(data_path)


if __name__ == '__main__':
    _main()
