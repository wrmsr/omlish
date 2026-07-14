from ..backends import MemoryStats


def test_memory_stats():
    ms = MemoryStats(total_b=10)
    ms += MemoryStats(total_b=20)
    assert ms.total_b == 30
