import collections
import heapq
import typing as ta


T = ta.TypeVar('T')


def distribute_evenly(
        items: ta.Iterable[tuple[T, float]],
        n_bins: int,
) -> list[list[tuple[T, float]]]:
    """
    Distribute items into n bins as evenly as possible in terms of total size.
     - Sorting ensures larger items are placed first, preventing large leftover gaps in bins.
     - A min-heap efficiently finds the least loaded bin in O(log n), keeping the distribution balanced.
     - Each item is placed in the lightest bin, preventing a few bins from getting overloaded early.

    :param items: List of tuples (itemname, size).
    :param n_bins: Number of bins.
    :return: List of n_bins lists, each containing items assigned to that bin.
    """

    # Sort items by size in descending order
    items_sorted = sorted(items, key=lambda x: x[1], reverse=True)

    # Min-heap to track bin loads (size, index)
    bins = [(0, i) for i in range(n_bins)]  # (current size, bin index)
    heapq.heapify(bins)

    # Allocate items to bins
    bin_contents = collections.defaultdict(list)

    for item_name, size in items_sorted:
        # Get the least loaded bin
        bin_size, bin_index = heapq.heappop(bins)

        # Assign item to this bin
        bin_contents[bin_index].append((item_name, size))

        # Update bin load and push back to heap
        heapq.heappush(bins, (bin_size + size, bin_index))  # type: ignore

    # Convert defaultdict to list
    return [bin_contents[i] for i in range(n_bins)]
