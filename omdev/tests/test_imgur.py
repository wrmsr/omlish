from omlish import dataclasses as dc
from omlish import marshal as msh

from ..imgur import ImageUploadData


def test_marshal():
    ad = dict(
        **{f.name: f.type() for f in dc.fields(ImageUploadData) if f.type in (int, str, bool)},  # type: ignore  # noqa
        tags=(),
    )

    xd = dict(
        barf=True,
        frab=False,
    )

    o = msh.unmarshal({**ad, **xd}, ImageUploadData)

    assert o == ImageUploadData(
        **ad,
        x=xd,
    )
