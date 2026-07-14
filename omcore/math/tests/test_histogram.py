from ..histogram import SamplingHistogram


def test_sampling_histogram():
    sh = SamplingHistogram(size=10)

    st = sh.get()
    assert st.count == 0

    sh.add(1.0)
    st = sh.get()
    assert st.count == 1
    assert st.min == st.max == 1.0
    assert [p.value for p in st.last_percentiles if p.p == 0.5] == [1.0]

    sh.add(3.0)
    st = sh.get()
    assert st.count == 2
    assert st.min == 1.0
    assert st.max == 3.0
    assert [p.value for p in st.last_percentiles if p.p == 0.75] == [1.0]
    assert [p.value for p in st.last_percentiles if p.p == 0.95] == [3.0]

    sh.add(10.0)
    st = sh.get()
    assert st.count == 3
    assert st.min == 1.0
    assert st.max == 10.0
    assert [p.value for p in st.last_percentiles if p.p == 0.5] == [1.0]
    assert [p.value for p in st.last_percentiles if p.p == 0.75] == [3.0]
    assert [p.value for p in st.last_percentiles if p.p == 0.95] == [10.0]

    for i in range(10, 20):
        sh.add(i)
    st = sh.get()
    assert st.count == 13
    assert st.min == 1.0
    assert st.max == 19.0
    assert [p.value for p in st.last_percentiles if p.p == 0.5] == [14.0]
    assert [p.value for p in st.last_percentiles if p.p == 0.75] == [16.0]
    assert [p.value for p in st.last_percentiles if p.p == 0.95] == [18.0]
