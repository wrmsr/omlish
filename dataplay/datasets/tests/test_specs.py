from omlish import marshal as msh

from .. import specs


def test_specs():
    gs = specs.GitDatasetSpec(
        repo_url='https://github.com/wrmsr/deep_learning_cookbook',
        rev='138a99b09ffa3a728d261e461440f029e512ac93',
        repo_suptree='/data/wp_movies_10k.ndjson',
    )
