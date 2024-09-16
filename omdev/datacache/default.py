import os.path

from omlish import lang

from .cache import DataCache


##


@lang.cached_function(lock=True)
def default_dir() -> str:
    return os.path.expanduser('~/.cache/omlish/data')


@lang.cached_function(lock=True)
def default() -> DataCache:
    return DataCache(default_dir())


def _main() -> None:
    from omlish import logs

    logs.configure_standard_logging('INFO')

    #

    from .specs import GitCacheDataSpec
    from .specs import GithubContentCacheDataSpec
    from .specs import HttpCacheDataSpec

    for spec in [
        GitCacheDataSpec(
            'https://github.com/wrmsr/deep_learning_cookbook',
            rev='138a99b09ffa3a728d261e461440f029e512ac93',
            subtrees=['data/wp_movies_10k.ndjson'],
        ),
        GithubContentCacheDataSpec(
            'karpathy/char-rnn',
            'master',
            ['data/tinyshakespeare/input.txt'],
        ),
        HttpCacheDataSpec('https://github.com/VanushVaswani/keras_mnistm/releases/download/1.0/keras_mnistm.pkl.gz'),
    ]:
        print(spec)
        for _ in range(2):
            print(default().get(spec))


if __name__ == '__main__':
    _main()
