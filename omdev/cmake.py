import abc
import io
import typing as ta

from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class Command:
    name: str
    args: str | ta.Sequence[str]
    lines: ta.Sequence[str] | None = None


@dc.dataclass(frozen=True)
class Var:
    name: str
    value: str | ta.Sequence[str]


@dc.dataclass(frozen=True)
class Target(abc.ABC):
    name: str
    src_files: ta.Sequence[str]

    include_dirs: ta.Sequence[str] | None = None
    compile_opts: ta.Sequence[str] | None = None
    link_dirs: ta.Sequence[str] | None = None
    link_opts: ta.Sequence[str] | None = None

    compile_flags_by_source_file: ta.Mapping[str, ta.Sequence[str]] | None = None

    link_libs: ta.Sequence[str] | None = None

    extra_cmds: ta.Sequence[Command] | None = None

    @property
    @abc.abstractmethod
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

    def __init__(
            self,
            out: io.TextIOBase,
            *,
            indent: int = 4,
    ) -> None:
        super().__init__()

        self._out = out
        self._indent = indent

    def write(
            self,
            obj: str | ta.Sequence[str] = '',
            *,
            spacing: int | str = 0,
            indent: int | str | None = None,
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

    def write_section(self, label: str) -> None:
        self.write(['', f'### {label}', ''])

    def write_cmd(self, cmd: Command) -> None:
        args = cmd.args
        if not isinstance(args, str):
            args = ' '.join(args)
        if not cmd.lines:
            self.write(f'{cmd.name}({args})')
        else:
            if isinstance(cmd.lines, str):
                raise TypeError(cmd.lines)
            self.write(f'{cmd.name}({args}')
            self.write(cmd.lines, indent=self._indent)
            self.write(')')
            self.write()

    def write_var(self, var: Var) -> None:
        return self.write_cmd(Command('set', var.name, [var.value] if isinstance(var.value, str) else var.value))

    def write_target(self, target: Target) -> None:
        self.write_section(target.name)

        self.write_cmd(Command(target.command_name, [target.name, *target.command_extra], target.src_files))

        if target.include_dirs:
            self.write_cmd(Command('target_include_directories', [target.name, 'PRIVATE'], target.include_dirs))
        if target.compile_opts:
            self.write_cmd(Command('target_compile_options', [target.name, 'PRIVATE'], target.compile_opts))

        if target.link_dirs:
            self.write_cmd(Command('target_link_directories', [target.name, 'PRIVATE'], target.link_dirs))
        if target.link_opts:
            self.write_cmd(Command('target_link_options', [target.name, 'PRIVATE'], target.link_opts))

        if target.compile_flags_by_source_file:
            for sf, cf in target.compile_flags_by_source_file.items():
                cf = ['"' + f.replace('"', '\\"') + '"' for f in cf]
                self.write_cmd(Command('set_source_files_properties', [sf, 'PROPERTIES', 'COMPILE_FLAGS'], cf))

        if target.link_libs:
            self.write_cmd(Command('target_link_libraries', [target.name, 'PRIVATE'], target.link_libs))

        for cmd in (target.extra_cmds or ()):
            self.write_cmd(cmd)

    @property
    def preamble(self) -> ta.Sequence[str]:
        return [
            'cmake_minimum_required(VERSION 3.1...3.16)',
            'set(EXECUTABLE_OUTPUT_PATH ${CMAKE_SOURCE_DIR})',
        ]
