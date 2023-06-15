import abc
import typing as ta

from ... import dataclasses as dc


@dc.dataclass(frozen=True)
class Command:
    name: str
    args: ta.Union[str, ta.Sequence[str]]
    lines: ta.Optional[ta.Sequence[str]] = None


@dc.dataclass(frozen=True)
class Var:
    name: str
    value: ta.Union[str, ta.Sequence[str]]


@dc.dataclass(frozen=True)
class Target(abc.ABC):
    name: str
    source_files: ta.Sequence[str]

    include_directories: ta.Optional[ta.Sequence[str]] = None
    compile_options: ta.Optional[ta.Sequence[str]] = None
    link_options: ta.Optional[ta.Sequence[str]] = None

    compile_flags_by_source_file: ta.Optional[ta.Mapping[str, ta.Sequence[str]]] = None

    link_libraries: ta.Optional[ta.Sequence[str]] = None

    @abc.abstractproperty
    def command_name(self) -> str:
        raise NotImplementedError

    @property
    def command_extra(self) -> ta.Sequence[str]:
        return []


@dc.dataclass(frozen=True)
class Library(Target):

    @property
    def command_name(self) -> str:
        return 'add_library'


@dc.dataclass(frozen=True)
class StaticLibrary(Library):

    @property
    def command_extra(self) -> ta.Sequence[str]:
        return ['STATIC']


@dc.dataclass(frozen=True)
class ModuleLibrary(Library):

    @property
    def command_extra(self) -> ta.Sequence[str]:
        return ['MODULE']


@dc.dataclass(frozen=True)
class Executable(Target):

    @property
    def command_name(self) -> str:
        return 'add_executable'


class CmakeGen:

    def __init__(self, out) -> None:
        super().__init__()

        self._out = out

    def _write(
            self,
            obj: ta.Union[str, ta.Sequence[str]] = '',
            *,
            spacing: ta.Union[int, str] = 0,
            indent: ta.Union[int, str, None] = None,
    ) -> None:
        if isinstance(obj, str):
            obj = [obj]
        if isinstance(spacing, int):
            spacing = '\n' * spacing
        if isinstance(indent, int):
            indent = ' ' * indent
        for line in obj:
            if indent is not None:
                line = indent + line
            self._out.write(line)
            self._out.write('\n')
            if spacing is not None:
                self._out.write(spacing)

    def _write_section(self, label: str) -> None:
        self._write(['', f'### {label}', ''])

    def _write_cmd(self, cmd: Command) -> None:
        args = cmd.args
        if not isinstance(args, str):
            args = ' '.join(args)
        if not cmd.lines:
            self._write(f'{cmd.name}({args})')
        else:
            if isinstance(cmd.lines, str):
                raise TypeError(cmd.lines)
            self._write(f'{cmd.name}({args}')
            self._write(cmd.lines, indent=8)
            self._write(')', indent=8)
            self._write()

    def _write_var(self, var: Var) -> None:
        return self._write_cmd(Command('set', var.name, [var.value] if isinstance(var.value, str) else var.value))

    def _write_target(self, target: Target) -> None:
        self._write_section(target.name)
        self._write_cmd(Command(target.command_name, [target.name, *target.command_extra], target.source_files))
        if target.include_directories:
            self._write_cmd(Command('target_include_directories', [target.name, 'PRIVATE'], target.include_directories))
        if target.compile_options:
            self._write_cmd(Command('target_compile_options', [target.name, 'PRIVATE'], target.compile_options))
        if target.link_options:
            self._write_cmd(Command('target_link_options', [target.name, 'PRIVATE'], target.link_options))
        if target.compile_flags_by_source_file:
            for sf, cf in target.compile_flags_by_source_file.items():
                cf = ['"' + f.replace('"', '\\"') + '"' for f in cf]
                self._write_cmd(Command('set_source_files_properties', [sf, 'PROPERTIES', 'COMPILE_FLAGS'], cf))
        if target.link_libraries:
            self._write_cmd(Command('target_link_libraries', [target.name, 'PRIVATE'], target.link_libraries))

    @property
    def preamble(self) -> ta.List[str]:
        return [
            'cmake_minimum_required(VERSION 3.1...3.16)',
            'set(EXECUTABLE_OUTPUT_PATH ${CMAKE_SOURCE_DIR})',
        ]

    @property
    def common_vars(self) -> ta.List[Var]:
        return []

    def write(self) -> None:
        self._write(self.preamble, spacing=1)

        self._write_section('Common')
        for var in self.common_vars:
            self._write_var(var)
