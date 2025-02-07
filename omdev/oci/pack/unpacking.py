# ruff: noqa: UP006 UP007
# @omlish-lite
import contextlib
import os.path
import tarfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked


##


class OciLayerUnpacker(ExitStacked):
    def __init__(
            self,
            input_files: ta.Sequence[ta.Union[str, tarfile.TarFile]],
            output_file_path: str,
    ) -> None:
        super().__init__()

        self._input_files = list(input_files)
        self._output_file_path = output_file_path

    #

    @contextlib.contextmanager
    def _open_input_file(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Iterator[tarfile.TarFile]:
        if isinstance(input_file, tarfile.TarFile):
            yield input_file

        elif isinstance(input_file, str):
            with tarfile.open(input_file) as tar_file:
                yield tar_file

        else:
            raise TypeError(input_file)

    #

    class _Entry(ta.NamedTuple):
        file: ta.Union[str, tarfile.TarFile]
        info: tarfile.TarInfo

    def _build_input_file_sorted_entries(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Sequence[_Entry]:
        dct: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        with self._open_input_file(input_file) as input_tar_file:
            for info in input_tar_file.getmembers():
                check.not_in(info.name, dct)
                dct[info.name] = self._Entry(
                    file=input_file,
                    info=info,
                )

        return sorted(dct.values(), key=lambda entry: entry.info.name)

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, _Entry]:
        root: dict = {}

        def find_dir(dir_name: str) -> dict:  # noqa
            if dir_name:
                dir_parts = dir_name.split('/')
            else:
                dir_parts = []

            cur = root  # noqa
            for dir_part in dir_parts:
                cur = cur[dir_part]  # noqa

            return check.isinstance(cur, dict)

        #

        for input_file in self._input_files:
            sorted_entries = self._build_input_file_sorted_entries(input_file)

            wh_names = set()
            wh_opaques = set()

            #

            for entry in sorted_entries:
                info = entry.info
                name = check.non_empty_str(info.name)
                base_name = os.path.basename(name)
                dir_name = os.path.dirname(name)

                if base_name == '.wh..wh..opq':
                    wh_opaques.add(dir_name)
                    continue

                if base_name.startswith('.wh.'):
                    wh_base_name = os.path.basename(base_name[4:])
                    wh_name = os.path.join(dir_name, wh_base_name)
                    wh_names.add(wh_name)
                    continue

                cur = find_dir(dir_name)

                if info.type == tarfile.DIRTYPE:
                    try:
                        ex = cur[base_name]
                    except KeyError:
                        cur[base_name] = {'': entry}
                    else:
                        ex[''] = entry

                else:
                    cur[base_name] = entry

            #

            for wh_name in reversed(sorted(wh_names)):  # noqa
                wh_dir_name = os.path.dirname(wh_name)
                wh_base_name = os.path.basename(wh_name)

                cur = find_dir(wh_dir_name)
                rm = cur[wh_base_name]

                if isinstance(rm, dict):
                    # Whiteouts wipe out whole directory:
                    # https://github.com/containerd/containerd/blob/59c8cf6ea5f4175ad512914dd5ce554942bf144f/pkg/archive/tar_test.go#L648
                    # check.equal(set(rm), '')
                    del cur[wh_base_name]

                elif isinstance(rm, self._Entry):
                    del cur[wh_base_name]

                else:
                    raise TypeError(rm)

            if wh_opaques:
                raise NotImplementedError

        #

        out: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        def rec(cur):  # noqa
            for _, child in sorted(cur.items(), key=lambda t: t[0]):
                if isinstance(child, dict):
                    rec(child)

                elif isinstance(child, self._Entry):
                    check.not_in(child.info.name, out)
                    out[child.info.name] = child

                else:
                    raise TypeError(child)

        rec(root)

        return out

    #

    @cached_nullary
    def _output_tar_file(self) -> tarfile.TarFile:
        return self._enter_context(tarfile.open(self._output_file_path, 'w'))

    #

    def _add_unpacked_entry(
            self,
            input_tar_file: tarfile.TarFile,
            info: tarfile.TarInfo,
    ) -> None:
        base_name = os.path.basename(info.name)
        check.state(not base_name.startswith('.wh.'))

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(input_tar_file.extractfile(info)) as f:
                self._output_tar_file().addfile(info, f)

        else:
            self._output_tar_file().addfile(info)

    def _unpack_file(
            self,
            input_file: ta.Union[str, tarfile.TarFile],
    ) -> None:
        entries_by_name = self._entries_by_name()

        with self._open_input_file(input_file) as input_tar_file:
            info: tarfile.TarInfo
            for info in input_tar_file.getmembers():
                try:
                    entry = entries_by_name[info.name]
                except KeyError:
                    continue

                if entry.file != input_file:
                    continue

                self._add_unpacked_entry(input_tar_file, info)

    @cached_nullary
    def write(self) -> None:
        for input_file in self._input_files:
            self._unpack_file(input_file)
