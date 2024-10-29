import dataclasses as dc
import os
import typing as ta

from omlish.lite.strings import format_num_bytes

from ... import prompttoolkit as ptk


def get_directory_size(path: str) -> int:
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size


@dc.dataclass(frozen=True)
class Entry:
    name: str
    size: int
    type: ta.Literal['dir', 'file']


def scan_directory(path: str) -> list[Entry]:
    entries: list[Entry] = []

    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir(follow_symlinks=False):
                size = get_directory_size(entry.path)
                entries.append(Entry(entry.name + '/', size, 'dir'))

            elif entry.is_file(follow_symlinks=False):
                size = entry.stat().st_size
                entries.append(Entry(entry.name, size, 'file'))

    entries.sort(key=lambda x: x.size, reverse=True)
    return entries


class NcduApp:
    def __init__(self, root_path: str) -> None:
        super().__init__()

        self._root_path = root_path
        self._current_path = root_path
        self._entries = scan_directory(root_path)
        self._cursor = 0

        self._text_area = ptk.TextArea(focusable=True)
        self.update_display()

        self._kb = ptk.KeyBindings()
        self._kb.add('q')(self.exit_app)
        for k in ['up', 'p']:
            self._kb.add(k)(self.move_up)
        for k in ['down', 'n']:
            self._kb.add(k)(self.move_down)
        self._kb.add('enter')(self.enter_directory)
        self._kb.add('backspace')(self.go_back)

        self._layout = ptk.Layout(ptk.Frame(self._text_area))

        self._style = ptk.Style.from_dict({
            'frame': 'bg:#008800 bold',
            'text-area': 'bg:#000000 fg:#ffffff',
        })

        self._app: ptk.Application = ptk.Application(
            layout=self._layout,
            key_bindings=self._kb,
            style=self._style,
            full_screen=True,
        )

    #

    def update_display(self) -> None:
        display_text = f'Current Directory: {self._current_path}\n\n'
        for i, e in enumerate(self._entries):
            indicator = '>' if i == self._cursor else ' '
            display_text += f'{indicator} {e.name:<40} {format_num_bytes(e.size):>10}\n'
        self._text_area.text = display_text

    #

    def move_up(self, event: ptk.KeyPressEvent) -> None:
        if self._cursor > 0:
            self._cursor -= 1
            self.update_display()

    def move_down(self, event: ptk.KeyPressEvent) -> None:
        if self._cursor < len(self._entries) - 1:
            self._cursor += 1
            self.update_display()

    def enter_directory(self, event: ptk.KeyPressEvent) -> None:
        selected_entry = self._entries[self._cursor]
        if selected_entry.type == 'dir':
            self._current_path = os.path.join(self._current_path, selected_entry.name[:-1])
            self._entries = scan_directory(self._current_path)
            self._cursor = 0
            self.update_display()

    def go_back(self, event: ptk.KeyPressEvent) -> None:
        if self._current_path != self._root_path:
            self._current_path = os.path.dirname(self._current_path)
            self._entries = scan_directory(self._current_path)
            self._cursor = 0
            self.update_display()

    def exit_app(self, event: ptk.KeyPressEvent) -> None:
        event.app.exit()

    #

    def run(self) -> None:
        self._app.run()


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('dir', default='.', nargs='?')

    args = parser.parse_args()

    ncdu_app = NcduApp(args.dir)
    ncdu_app.run()


if __name__ == '__main__':
    _main()
