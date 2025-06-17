# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import heapq
import tarfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import ExitStacked

from ..compression import OciCompression
from ..tars import OciDataTarWriter
from ..tars import WrittenOciDataTarFileInfo


##


class OciLayerPacker(ExitStacked):
    def __init__(
            self,
            input_file_path: str,
            output_file_paths: ta.Sequence[str],
            *,
            compression: ta.Optional[OciCompression] = None,
    ) -> None:
        super().__init__()

        self._input_file_path = input_file_path
        self._output_file_paths = list(output_file_paths)
        self._compression = compression

        self._output_file_indexes_by_name: ta.Dict[str, int] = {}

    #

    @cached_nullary
    def _input_tar_file(self) -> tarfile.TarFile:
        # FIXME: check uncompressed
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
        links_by_name: ta.Mapping[str, tarfile.TarInfo]

    @cached_nullary
    def _categorized_entries(self) -> _CategorizedEntries:
        files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        non_files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        links_by_name: ta.Dict[str, tarfile.TarInfo] = {}

        for name, info in self._entries_by_name().items():
            if info.type in tarfile.REGULAR_TYPES:
                files_by_name[name] = info
            elif info.type in (tarfile.LNKTYPE, tarfile.GNUTYPE_LONGLINK):
                links_by_name[name] = info
            else:
                non_files_by_name[name] = info

        return self._CategorizedEntries(
            files_by_name=files_by_name,
            non_files_by_name=non_files_by_name,
            links_by_name=links_by_name,
        )

    #

    @cached_nullary
    def _non_files_sorted_by_name(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().non_files_by_name.values(),
            key=lambda info: info.name,
        )

    @cached_nullary
    def _files_descending_by_size(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().files_by_name.values(),
            key=lambda info: -check.isinstance(info.size, int),
        )

    #

    @cached_nullary
    def _output_files(self) -> ta.Sequence[ta.BinaryIO]:
        return [
            self._enter_context(open(output_file_path, 'wb'))
            for output_file_path in self._output_file_paths
        ]

    @cached_nullary
    def _output_tar_writers(self) -> ta.Sequence[OciDataTarWriter]:
        return [
            self._enter_context(
                OciDataTarWriter(
                    output_file,
                    compression=self._compression,
                ),
            )
            for output_file in self._output_files()
        ]

    #

    def _write_entry(
            self,
            info: tarfile.TarInfo,
            output_file_idx: int,
    ) -> None:
        check.not_in(info.name, self._output_file_indexes_by_name)

        writer = self._output_tar_writers()[output_file_idx]

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(self._input_tar_file().extractfile(info)) as f:
                writer.add_file(info, f)  # type: ignore

        else:
            writer.add_file(info)

        self._output_file_indexes_by_name[info.name] = output_file_idx

    @cached_nullary
    def _write_non_files(self) -> None:
        for non_file in self._non_files_sorted_by_name():
            self._write_entry(non_file, 0)

    @cached_nullary
    def _write_files(self) -> None:
        writers = self._output_tar_writers()

        bins = [
            (writer.info().compressed_sz, i)
            for i, writer in enumerate(writers)
        ]

        heapq.heapify(bins)

        for file in self._files_descending_by_size():
            _, bin_index = heapq.heappop(bins)

            writer = writers[bin_index]

            self._write_entry(file, bin_index)

            bin_size = writer.info().compressed_sz

            heapq.heappush(bins, (bin_size, bin_index))

    @cached_nullary
    def _write_links(self) -> None:
        for link in self._categorized_entries().links_by_name.values():
            link_name = check.non_empty_str(link.linkname)

            output_file_idx = self._output_file_indexes_by_name[link_name]

            self._write_entry(link, output_file_idx)

    @cached_nullary
    def write(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        writers = self._output_tar_writers()

        self._write_non_files()
        self._write_files()
        self._write_links()

        for output_tar_writer in writers:
            output_tar_writer.tar_file().close()

        return {
            output_file_path: output_tar_writer.info()
            for output_file_path, output_tar_writer in zip(self._output_file_paths, writers)
        }
