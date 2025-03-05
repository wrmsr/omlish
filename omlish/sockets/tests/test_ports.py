from ..ports import get_available_ports


def test_get_available_ports():
    exclude = {5000, 8000}
    ports = get_available_ports(2, exclude=exclude)
    assert len(ports) == 2
    assert not set(ports) & exclude
