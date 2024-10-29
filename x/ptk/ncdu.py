import os
import typing as ta

from omlish.lite.strings import format_num_bytes

from . import prompttoolkit as ptk


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


def scan_directory(path: str) -> list[tuple[str, int, ta.Literal['dir', 'file']]]:
    entries = []

    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir(follow_symlinks=False):
                size = get_directory_size(entry.path)
                entries.append((entry.name + '/', size, 'dir'))

            elif entry.is_file(follow_symlinks=False):
                size = entry.stat().st_size
                entries.append((entry.name, size, 'file'))

    entries.sort(key=lambda x: x[1], reverse=True)
    return entries


class NcduApp:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.current_path = root_path
        self.entries = scan_directory(root_path)
        self.cursor = 0

        self.text_area = ptk.TextArea(focusable=True)
        self.update_display()

        # Set up key bindings
        self.kb = ptk.KeyBindings()
        self.kb.add('q')(self.exit_app)
        for k in ['up', 'p']:
            self.kb.add(k)(self.move_up)
        for k in ['down', 'n']:
            self.kb.add(k)(self.move_down)
        self.kb.add('enter')(self.enter_directory)
        self.kb.add('backspace')(self.go_back)

        # Layout and Application
        self.layout = ptk.Layout(ptk.Frame(self.text_area))
        self.style = ptk.Style.from_dict({
            'frame': 'bg:#008800 bold',
            'text-area': 'bg:#000000 fg:#ffffff',
        })
        self.app = ptk.Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
        )

    def update_display(self) -> None:
        display_text = f'Current Directory: {self.current_path}\n\n'
        for i, (name, size, type_) in enumerate(self.entries):
            indicator = '>' if i == self.cursor else ' '
            display_text += f'{indicator} {name:<40} {format_num_bytes(size):>10}\n'
        self.text_area.text = display_text

    def move_up(self, event) -> None:
        if self.cursor > 0:
            self.cursor -= 1
            self.update_display()

    def move_down(self, event) -> None:
        if self.cursor < len(self.entries) - 1:
            self.cursor += 1
            self.update_display()

    def enter_directory(self, event) -> None:
        selected_entry = self.entries[self.cursor]
        if selected_entry[2] == 'dir':
            self.current_path = os.path.join(self.current_path, selected_entry[0][:-1])
            self.entries = scan_directory(self.current_path)
            self.cursor = 0
            self.update_display()

    def go_back(self, event) -> None:
        if self.current_path != self.root_path:
            self.current_path = os.path.dirname(self.current_path)
            self.entries = scan_directory(self.current_path)
            self.cursor = 0
            self.update_display()

    def exit_app(self, event) -> None:
        event.app.exit()

    def run(self) -> None:
        self.app.run()


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('dir', default='.', nargs='?')

    args = parser.parse_args()

    ncdu_app = NcduApp(args.dir)
    ncdu_app.run()


if __name__ == '__main__':
    _main()
