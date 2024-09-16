"""
https://github.com/run-llama/llama_index/blob/c3e04eeee7f3dbe1bd6789b14e5774c36298caf5/llama-index-core/llama_index/core/indices/query/embedding_utils.py#L11
"""
# The MIT License
#
# Copyright (c) Jerry Liu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import enum
import heapq
import math
import typing as ta

from omlish import lang
import numpy as np


if ta.TYPE_CHECKING:
    from sklearn import linear_model as skl_lm
    from sklearn import svm as skl_svm
else:
    skl_lm = lang.proxy_import('sklearn.linear_model')
    skl_svm = lang.proxy_import('sklearn.svm')


##


class VectorStoreQueryMode(str, enum.Enum):
    """Vector store query mode."""

    DEFAULT = 'default'
    SPARSE = 'sparse'
    HYBRID = 'hybrid'
    TEXT_SEARCH = 'text_search'
    SEMANTIC_HYBRID = 'semantic_hybrid'

    # fit learners
    SVM = 'svm'
    LOGISTIC_REGRESSION = 'logistic_regression'
    LINEAR_REGRESSION = 'linear_regression'

    # maximum marginal relevance
    MMR = 'mmr'


class SimilarityMode(str, enum.Enum):
    """Modes for similarity/distance."""

    DEFAULT = 'cosine'
    DOT_PRODUCT = 'dot_product'
    EUCLIDEAN = 'euclidean'


Embedding: ta.TypeAlias = list[float]


def mean_agg(embeddings: list[Embedding]) -> Embedding:
    """Mean aggregation for embeddings."""

    return np.array(embeddings).mean(axis=0).tolist()


def similarity(
        embedding1: Embedding,
        embedding2: Embedding,
        mode: SimilarityMode = SimilarityMode.DEFAULT,
) -> float:
    """Get embedding similarity."""

    if mode == SimilarityMode.EUCLIDEAN:
        # Using -euclidean distance as similarity to achieve same ranking order
        return -float(np.linalg.norm(np.array(embedding1) - np.array(embedding2)))

    elif mode == SimilarityMode.DOT_PRODUCT:
        return np.dot(embedding1, embedding2)

    else:
        product = np.dot(embedding1, embedding2)
        norm = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        return product / norm


##


def get_top_k_embeddings(
        query_embedding: list[float],
        embeddings: list[list[float]],
        *,
        similarity_fn: ta.Callable[..., float] | None = None,
        similarity_top_k: int | None = None,
        embedding_ids: list | None = None,
        similarity_cutoff: float | None = None,
) -> tuple[list[float], list]:
    """Get top nodes by similarity to the query."""

    if embedding_ids is None:
        embedding_ids = list(range(len(embeddings)))

    similarity_fn = similarity_fn or similarity

    embeddings_np = np.array(embeddings)
    query_embedding_np = np.array(query_embedding)

    similarity_heap: list[tuple[float, ta.Any]] = []
    for i, emb in enumerate(embeddings_np):
        s = similarity_fn(query_embedding_np, emb)  # type: ignore[arg-type]
        if similarity_cutoff is None or s > similarity_cutoff:
            heapq.heappush(similarity_heap, (s, embedding_ids[i]))
            if similarity_top_k and len(similarity_heap) > similarity_top_k:
                heapq.heappop(similarity_heap)
    result_tups = sorted(similarity_heap, key=lambda x: x[0], reverse=True)

    result_similarities = [s for s, _ in result_tups]
    result_ids = [n for _, n in result_tups]

    return result_similarities, result_ids


def get_top_k_embeddings_learner(
        query_embedding: list[float],
        embeddings: list[list[float]],
        *,
        similarity_top_k: int | None = None,
        embedding_ids: list | None = None,
        query_mode: VectorStoreQueryMode = VectorStoreQueryMode.SVM,
) -> tuple[list[float], list]:
    """Get top embeddings by fitting a learner against query.

    Inspired by Karpathy's SVM demo:
    https://github.com/karpathy/randomfun/blob/master/knn_vs_svm.ipynb

    Can fit SVM, linear regression, and more.
    """

    if embedding_ids is None:
        embedding_ids = list(range(len(embeddings)))
    query_embedding_np = np.array(query_embedding)
    embeddings_np = np.array(embeddings)
    # create dataset
    dataset_len = len(embeddings) + 1
    dataset = np.concatenate([query_embedding_np[None, ...], embeddings_np])
    y = np.zeros(dataset_len)
    y[0] = 1

    if query_mode == VectorStoreQueryMode.SVM:
        # train our SVM
        # TODO: make params configurable
        clf = skl_svm.LinearSVC(
            class_weight='balanced',
            verbose=False,
            max_iter=10000,
            tol=1e-6,
            C=0.1,
        )

    elif query_mode == VectorStoreQueryMode.LINEAR_REGRESSION:
        clf = skl_lm.LinearRegression()

    elif query_mode == VectorStoreQueryMode.LOGISTIC_REGRESSION:
        clf = skl_lm.LogisticRegression(class_weight='balanced')

    else:
        raise ValueError(f'Unknown query mode: {query_mode}')

    clf.fit(dataset, y)  # train

    # infer on whatever data you wish, e.g. the original data
    similarities = clf.decision_function(dataset[1:])
    sorted_ix = np.argsort(-similarities)
    top_sorted_ix = sorted_ix[:similarity_top_k]

    result_similarities = similarities[top_sorted_ix]
    result_ids = [embedding_ids[ix] for ix in top_sorted_ix]

    return result_similarities, result_ids


def get_top_k_mmr_embeddings(
        query_embedding: list[float],
        embeddings: list[list[float]],
        *,
        similarity_fn: ta.Callable[..., float] | None = None,
        similarity_top_k: int | None = None,
        embedding_ids: list | None = None,
        mmr_threshold: float | None = None,
) -> tuple[list[float], list]:
    """Get top nodes by similarity to the query,
    discount by their similarity to previous results.

    A mmr_threshold of 0 will strongly avoid similarity to previous results.
    A mmr_threshold of 1 will check similarity the query and ignore previous results.
    """

    threshold = mmr_threshold or 0.5
    similarity_fn = similarity_fn or similarity

    if embedding_ids is None or embedding_ids == []:
        embedding_ids = list(range(len(embeddings)))
    full_embed_map = dict(zip(embedding_ids, range(len(embedding_ids))))
    embed_map = full_embed_map.copy()
    embed_similarity = {}
    score: float = -math.inf
    high_score_id = None

    for i, emb in enumerate(embeddings):
        s = similarity_fn(query_embedding, emb)
        embed_similarity[embedding_ids[i]] = s
        if s * threshold > score:
            high_score_id = embedding_ids[i]
            score = s * threshold

    results: list[tuple[ta.Any, ta.Any]] = []

    embedding_length = len(embeddings or [])
    similarity_top_k_count = similarity_top_k or embedding_length
    while len(results) < min(similarity_top_k_count, embedding_length):
        # Calculate the similarity score the for the leading one.
        results.append((score, high_score_id))

        # Reset so a new high scoring result can be found
        del embed_map[high_score_id]
        recent_embedding_id = high_score_id
        score = -math.inf

        # Iterate through results to find high score
        for embed_id in embed_map:
            overlap_with_recent = similarity_fn(
                embeddings[embed_map[embed_id]],
                embeddings[full_embed_map[recent_embedding_id]],
            )
            if threshold * embed_similarity[embed_id] - ((1 - threshold) * overlap_with_recent) > score:
                score = threshold * embed_similarity[embed_id] - ((1 - threshold) * overlap_with_recent)
                high_score_id = embed_id

    result_similarities = [s for s, _ in results]
    result_ids = [n for _, n in results]

    return result_similarities, result_ids
