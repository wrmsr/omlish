import os

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame
from prompt_toolkit.widgets import TextArea


# import humanize


# Function to calculate the size of a directory and its contents
def get_directory_size(path: str):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Use try-except to avoid permission errors or broken symlinks
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size


# Scan a directory and gather file and directory sizes
def scan_directory(path: str):
    entries = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir(follow_symlinks=False):
                size = get_directory_size(entry.path)
                entries.append((entry.name + '/', size, 'dir'))
            elif entry.is_file(follow_symlinks=False):
                size = entry.stat().st_size
                entries.append((entry.name, size, 'file'))
    # Sort by size, largest first
    entries.sort(key=lambda x: x[1], reverse=True)
    return entries


# A function to display the size in a human-readable format (e.g., KB, MB)
def format_size(size):
    # return humanize.naturalsize(size, binary=True)
    return str(size)


# A simple prompt-toolkit app that mimics ncdu
class NcduApp:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.current_path = root_path
        self.entries = scan_directory(root_path)
        self.cursor = 0

        self.text_area = TextArea(focusable=True)
        self.update_display()

        # Set up key bindings
        self.kb = KeyBindings()
        self.kb.add('q')(self.exit_app)
        self.kb.add('up')(self.move_up)
        self.kb.add('down')(self.move_down)
        self.kb.add('enter')(self.enter_directory)
        self.kb.add('backspace')(self.go_back)

        # Layout and Application
        self.layout = Layout(Frame(self.text_area))
        self.style = Style.from_dict(
            {
                'frame': 'bg:#008800 bold',
                'text-area': 'bg:#000000 fg:#ffffff',
            },
        )
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
        )

    def update_display(self):
        """Update the content of the text area."""
        display_text = f'Current Directory: {self.current_path}\n\n'
        for i, (name, size, type_) in enumerate(self.entries):
            indicator = '>' if i == self.cursor else ' '
            display_text += f'{indicator} {name:<40} {format_size(size):>10}\n'
        self.text_area.text = display_text

    def move_up(self, event):
        """Move the cursor up."""
        if self.cursor > 0:
            self.cursor -= 1
            self.update_display()

    def move_down(self, event):
        """Move the cursor down."""
        if self.cursor < len(self.entries) - 1:
            self.cursor += 1
            self.update_display()

    def enter_directory(self, event):
        """Enter the selected directory."""
        selected_entry = self.entries[self.cursor]
        if selected_entry[2] == 'dir':
            self.current_path = os.path.join(self.current_path, selected_entry[0][:-1])
            self.entries = scan_directory(self.current_path)
            self.cursor = 0
            self.update_display()

    def go_back(self, event):
        """Go back to the parent directory."""
        if self.current_path != self.root_path:
            self.current_path = os.path.dirname(self.current_path)
            self.entries = scan_directory(self.current_path)
            self.cursor = 0
            self.update_display()

    def exit_app(self, event):
        """Exit the application."""
        event.app.exit()

    def run(self):
        """Run the application."""
        self.app.run()


# Entry point
if __name__ == '__main__':
    root_directory = (
        '.'  # Start at current directory, modify this to set a different root
    )
    ncdu_app = NcduApp(root_directory)
    ncdu_app.run()
