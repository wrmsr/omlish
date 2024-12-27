# ruff: noqa: UP006 UP007
import typing as ta

from ..configs.formats import DEFAULT_CONFIG_FILE_LOADER
from ..configs.types import ConfigMap
from .marshal import OBJ_MARSHALER_MANAGER
from .marshal import ObjMarshalerManager


T = ta.TypeVar('T')


##


def load_config_file_obj(
        f: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Union[
            ta.Callable[[ConfigMap], ConfigMap],
            ta.Iterable[ta.Callable[[ConfigMap], ConfigMap]],
        ] = (),
        msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
) -> T:
    config_data = DEFAULT_CONFIG_FILE_LOADER.load_file(f)

    config_dct = config_data.as_map()

    if prepare is not None:
        if isinstance(prepare, ta.Iterable):
            pfs = list(prepare)
        else:
            pfs = [prepare]
        for pf in pfs:
            config_dct = pf(config_dct)

    return msh.unmarshal_obj(config_dct, cls)
