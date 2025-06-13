import typing as ta

from ...resources import ResourceManaged
from ...resources import Resources
from ...types import Output
from ..responses import Response


IntManagerResponse: ta.TypeAlias = Response[ResourceManaged[Response[int, Output]], Output]


def test_int_response():
    with Resources.new() as rsrc:
        irm = IntManagerResponse(
            ResourceManaged(
                Response[int, Output](420),
                rsrc,
            ),
        )

        # ta.reveal_type(irm)

        with irm.v as irm2:
            # ta.reveal_type(irm2)
            assert not irm.v._ResourceManaged__resources.closed  # type: ignore[attr-defined]  # noqa
            print(irm2.v * 2)

    assert rsrc.closed


IntStreamManagerResponse: ta.TypeAlias = Response[
    ResourceManaged[
        ta.Iterator[
            Response[
                int,
                Output,
            ],
        ],
    ],
    Output,
]


def test_int_stream_response():
    with Resources.new() as rsrc:
        irm = IntStreamManagerResponse(
            ResourceManaged(
                iter([Response[int, Output](420)]),
                rsrc,
            ),
        )
        # ta.reveal_type(irm)

        with irm.v as irm2s:
            # ta.reveal_type(irm2s)
            for irm2 in irm2s:
                # ta.reveal_type(irm2)
                assert not irm.v._ResourceManaged__resources.closed  # type: ignore[attr-defined]  # noqa
                print(irm2.v * 2)

    assert rsrc.closed


def test_int_stream_response_from_fn():
    def fn():
        with Resources.new() as rsrc:
            return IntStreamManagerResponse(
                ResourceManaged(
                    iter([Response[int, Output](420)]),
                    rsrc,
                ),
            )

    irm = fn()
    with irm.v as irm2s:
        # ta.reveal_type(irm2s)
        for irm2 in irm2s:
            # ta.reveal_type(irm2)
            assert not irm.v._ResourceManaged__resources.closed  # noqa
            print(irm2.v * 2)

    assert irm.v._ResourceManaged__resources.closed  # noqa
