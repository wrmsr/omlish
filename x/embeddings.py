"""
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
"""
import typing as ta


Vector: ta.TypeAlias = ta.Sequence[float]
Matrix: ta.TypeAlias = ta.Sequence[Vector]

DistanceFn: ta.TypeAlias = ta.Callable[[Vector, Vector], float]

