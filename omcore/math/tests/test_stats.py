from .. import stats


def test_statsbasic():
    st = stats.Stats(range(20))
    assert st.mean == 9.5
    assert round(st.std_dev, 2) == 5.77
    assert st.variance == 33.25
    assert st.skewness == 0
    assert round(st.kurtosis, 1) == 1.9
    assert st.median == 9.5
    print(st.get_zscore(3.))
    print(st.get_histogram_counts())
    print(st.get_histogram_counts([3, 7, 13]))
