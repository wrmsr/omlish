# ruff: noqa: UP006 UP007
# @omlish-lite
import heapq
import tarfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked

from .tars import OciDataTarGzWriter
from .tars import WrittenOciDataTarGzFileInfo


##


class OciLayerUnpacker(ExitStacked):
    def __init__(
            self,
            input_file_paths: ta.Sequence[str],
            output_file_path: str,
    ) -> None:
        super().__init__()

        self._input_file_paths = list(input_file_paths)
        self._output_file_path = output_file_path

        self._seen: ta.Set[str] = set()

    @cached_nullary
    def _output_tar_file(self) -> tarfile.TarFile:
        return self._enter_context(tarfile.open(self._output_file_path, 'w'))

    def _unpack_entry(
            self,
            input_tar_file: tarfile.TarFile,
            info: tarfile.TarInfo,
    ) -> None:
        if info.name in self._seen:
            return

        self._seen.add(info.name)

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(input_tar_file.extractfile(info)) as f:
                self._output_tar_file().addfile(info, f)

        else:
            self._output_tar_file().addfile(info)

    def _unpack_file(
            self,
            input_file_path: str,
    ) -> None:
        with tarfile.open(input_file_path) as input_tar_file:
            info: tarfile.TarInfo
            for info in input_tar_file.getmembers():
                self._unpack_entry(input_tar_file, info)

    @cached_nullary
    def write(self) -> None:
        for input_file_path in reversed(self._input_file_paths):
            self._unpack_file(input_file_path)


#


class OciLayerPacker(ExitStacked):
    def __init__(
            self,
            input_file_path: str,
            output_file_paths: ta.Sequence[str],
    ) -> None:
        super().__init__()

        self._input_file_path = input_file_path
        self._output_file_paths = list(output_file_paths)

    #

    @cached_nullary
    def _input_tar_file(self) -> tarfile.TarFile:
        return self._enter_context(tarfile.open(self._input_file_path))

    #

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, tarfile.TarInfo]:
        return {
            info.name: info
            for info in self._input_tar_file().getmembers()
        }

    #

    class _CategorizedEntries(ta.NamedTuple):
        files_by_name: ta.Mapping[str, tarfile.TarInfo]
        non_files_by_name: ta.Mapping[str, tarfile.TarInfo]

    @cached_nullary
    def _categorized_entries(self) -> _CategorizedEntries:
        files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        non_files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        for name, info in self._entries_by_name().items():
            if info.type in tarfile.REGULAR_TYPES:
                files_by_name[name] = info
            else:
                non_files_by_name[name] = info
        return self._CategorizedEntries(
            files_by_name=files_by_name,
            non_files_by_name=non_files_by_name,
        )

    #

    @cached_nullary
    def _files_descending_by_size(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().files_by_name.values(),
            key=lambda info: -check.isinstance(info.size, int),
        )

    @cached_nullary
    def _non_files_sorted_by_name(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().non_files_by_name.values(),
            key=lambda info: info.name,
        )

    #

    @cached_nullary
    def _output_files(self) -> ta.Sequence[ta.BinaryIO]:
        return [
            self._enter_context(open(output_file_path, 'wb'))
            for output_file_path in self._output_file_paths
        ]

    @cached_nullary
    def _output_tar_writers(self) -> ta.Sequence[OciDataTarGzWriter]:
        return [
            self._enter_context(OciDataTarGzWriter(output_file))
            for output_file in self._output_files()
        ]

    #

    @cached_nullary
    def _write_non_files(self) -> None:
        writer = self._output_tar_writers()[0]

        for non_file in self._non_files_sorted_by_name():
            writer.add_file(non_file)

    @cached_nullary
    def _write_files(self) -> None:
        writers = self._output_tar_writers()

        bins = [
            (writer.info().tar_sz, i)
            for i, writer in enumerate(writers)
        ]

        heapq.heapify(bins)

        for file in self._files_descending_by_size():
            _, bin_index = heapq.heappop(bins)

            writer = writers[bin_index]

            with check.not_none(self._input_tar_file().extractfile(file)) as f:
                writer.add_file(file, f)  # type: ignore

            bin_size = writer.info().tar_sz

            heapq.heappush(bins, (bin_size, bin_index))

    @cached_nullary
    def write(self) -> ta.Mapping[str, WrittenOciDataTarGzFileInfo]:
        writers = self._output_tar_writers()

        self._write_non_files()
        self._write_files()

        for output_tar_writer in writers:
            output_tar_writer.tar_file().close()

        return {
            output_file_path: output_tar_writer.info()
            for output_file_path, output_tar_writer in zip(self._output_file_paths, writers)
        }
