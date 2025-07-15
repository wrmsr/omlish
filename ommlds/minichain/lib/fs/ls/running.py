import dataclasses as dc
import os.path
import typing as ta

from omlish import check
from omlish import lang


##


@dc.dataclass(frozen=True)
class LsItem(lang.Abstract):
    name: str
    path: str


@dc.dataclass(frozen=True)
class FileLsItem(LsItem):
    pass


@dc.dataclass(frozen=True)
class DirLsItem(LsItem):
    children: ta.Mapping[str, LsItem]


class LsRunner:
    def __init__(
            self,
            *,
            path_filter: ta.Callable[[str], bool] | None = None,
    ) -> None:
        super().__init__()

        self._path_filter = path_filter

    def run(self, base_path: str) -> DirLsItem:
        check.arg(base_path.startswith('/'))
        check.arg(not base_path.endswith('/'))

        def rec(pfx: list[str]) -> DirLsItem | None:
            cur_path = os.path.join(base_path, *pfx)

            names = sorted(os.listdir(cur_path))
            children: dict[str, LsItem] = {}
            for n in names:
                np = os.path.join(cur_path, n)

                if self._path_filter is not None and not self._path_filter(np):
                    continue

                if os.path.isdir(np):
                    di = rec([*pfx, n])
                    if di is not None:
                        children[di.name] = di

                else:
                    children[n] = FileLsItem(
                        n,
                        np,
                    )

            return DirLsItem(
                base_path if not pfx else pfx[-1],
                cur_path,
                children,
            )

        return check.not_none(rec([]))
