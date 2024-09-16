"""
https://github.com/run-llama/llama_index/blob/c3e04eeee7f3dbe1bd6789b14e5774c36298caf5/llama-index-core/llama_index/core/indices/query/embedding_utils.py#L11

numpy.inner
numpy.dot

scipy.spatial.distance
  directed_hausdorff
  minkowski
  euclidean
  sqeuclidean
  correlation
  cosine
  hamming
  jaccard
  kulczynski1
  seuclidean
  cityblock
  mahalanobis
  chebyshev
  braycurtis
  canberra
  jensenshannon
  yule
  dice
  rogerstanimoto
  russellrao
  sokalmichener
  sokalsneath
  pdist
  squareform
  cdist

sklearn.metrics.pairwise
  euclidean_distances
  nan_euclidean_distances
  pairwise_distances_argmin_min
  pairwise_distances_argmin
  haversine_distances
  manhattan_distances
  cosine_distances
  paired_euclidean_distances
  paired_manhattan_distances
  paired_cosine_distances
  paired_distances
  linear_kernel
  polynomial_kernel
  sigmoid_kernel
  rbf_kernel
  laplacian_kernel
  cosine_similarity
  additive_chi2_kernel
  chi2_kernel
  distance_metrics
  pairwise_distances_chunked
  pairwise_distances
  kernel_metrics
  pairwise_kernels

simsimd:
  bilinear
  cdist
  cosine
  disable_capability
  dot
  enable_capability
  get_capabilities
  hamming
  inner
  intersect
  jaccard
  mahalanobis
  pointer_to_cosine
  pointer_to_dot
  pointer_to_inner
  pointer_to_jensenshannon
  pointer_to_kullbackleibler
  pointer_to_sqeuclidean
  pointer_to_vdot
  sqeuclidean
  vdot

https://pypi.org/project/faiss-cpu/
https://github.com/unum-cloud/usearch
"""
import typing as ta


Vector: ta.TypeAlias = ta.Sequence[float]
Matrix: ta.TypeAlias = ta.Sequence[Vector]

DistanceFn: ta.TypeAlias = ta.Callable[[Vector, Vector], float]


def _main() -> None:
    import numpy as np
    from usearch.index import Index, Matches

    index = Index(
        ndim=3,  # Define the number of dimensions in input vectors
        metric='cos',  # Choose 'l2sq', 'haversine' or other metric, default = 'ip'
        dtype='f32',  # Quantize to 'f16' or 'i8' if needed, default = 'f32'
        connectivity=16,  # How frequent should the connections in the graph be, optional
        expansion_add=128,  # Control the recall of indexing, optional
        expansion_search=64,  # Control the quality of search, optional
    )

    vector = np.array([0.2, 0.6, 0.4])
    index.add(42, vector)
    matches: Matches = index.search(vector, 10)

    assert len(index) == 1
    assert len(matches) == 1
    assert matches[0].key == 42
    assert matches[0].distance <= 0.001
    assert np.allclose(index[42], vector)


if __name__ == '__main__':
    _main()
