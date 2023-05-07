from .. import stats as stats_


def test_stats_basic():
    st = stats_.Stats(range(20))
    assert st.mean == 9.5
    assert round(st.std_dev, 2) == 5.77
    assert st.variance == 33.25
    assert st.skewness == 0
    assert round(st.kurtosis, 1) == 1.9
    assert st.median == 9.5
    print(st.get_zscore(3.))
    print(st.get_histogram_counts())
    print(st.get_histogram_counts([3, 7, 13]))


def test_sampling_histogram():
    sh = stats_.SamplingHistogram(size=10)

    st = sh.get()
    assert st.count == 0

    sh.add(1.0)
    st = sh.get()
    assert st.count == 1
    assert st.min == st.max == 1.0
    assert [v for p, v in st.last_percentiles if p == 0.5] == [1.0]

    sh.add(3.0)
    st = sh.get()
    assert st.count == 2
    assert st.min == 1.0
    assert st.max == 3.0
    assert [v for p, v in st.last_percentiles if p == 0.75] == [1.0]
    assert [v for p, v in st.last_percentiles if p == 0.95] == [3.0]

    sh.add(10.0)
    st = sh.get()
    assert st.count == 3
    assert st.min == 1.0
    assert st.max == 10.0
    assert [v for p, v in st.last_percentiles if p == 0.5] == [1.0]
    assert [v for p, v in st.last_percentiles if p == 0.75] == [3.0]
    assert [v for p, v in st.last_percentiles if p == 0.95] == [10.0]

    for i in range(10, 20):
        sh.add(i)
    st = sh.get()
    assert st.count == 13
    assert st.min == 1.0
    assert st.max == 19.0
    assert [v for p, v in st.last_percentiles if p == 0.5] == [14.0]
    assert [v for p, v in st.last_percentiles if p == 0.75] == [16.0]
    assert [v for p, v in st.last_percentiles if p == 0.95] == [18.0]
