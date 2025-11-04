import argparse
import pathlib
import typing as ta

from ... import textual as tx


##


class QuitConfirmScreen(tx.ModalScreen[bool]):
    """Screen with a dialog to confirm quit without saving."""

    CSS = """
        QuitConfirmScreen {
            align: center middle;
        }

        #dialog {
            width: 60;
            height: 11;
            border: thick $background 80%;
            background: $surface;
            padding: 1 2;
        }

        #question {
            height: 3;
            content-align: center middle;
        }

        Button {
            width: 1fr;
        }
    """

    def compose(self) -> tx.ComposeResult:
        yield tx.Vertical(
            tx.Label('You have unsaved changes. Do you want to save before quitting?', id='question'),
            tx.Button('Save and Quit', variant='success', id='save'),
            tx.Button('Quit Without Saving', variant='warning', id='quit'),
            tx.Button('Cancel', variant='primary', id='cancel'),
            id='dialog',
        )

    def on_button_pressed(self, event: tx.Button.Pressed) -> None:
        if event.button.id == 'save':
            self.dismiss(True)
        elif event.button.id == 'quit':
            self.dismiss(False)
        else:
            self.dismiss(None)


class TextEditor(tx.App):
    """A simple text editor using Textual."""

    CSS = """
        TextArea {
            height: 1fr;
        }

        Container {
            height: 100%;
        }
    """

    BINDINGS: ta.ClassVar[ta.Sequence[tx.Binding]] = [
        tx.Binding('ctrl+s', 'save', 'Save', show=True),
        tx.Binding('ctrl+q', 'quit', 'Quit', show=True),
    ]

    def __init__(self, filepath: pathlib.Path):
        super().__init__()

        self.filepath = filepath
        self.text_area: tx.TextArea | None = None
        self.modified = False
        self.original_content = ''

    def compose(self) -> tx.ComposeResult:
        """Create child widgets for the app."""

        yield tx.Header()
        yield tx.Container(tx.TextArea(id='editor'))
        yield tx.Footer()

    def on_mount(self) -> None:
        """Load the file content when the app starts."""

        self.text_area = self.query_one('#editor', tx.TextArea)

        # Load existing file or create new
        if self.filepath.exists():
            content = self.filepath.read_text()
            self.text_area.load_text(content)
            self.original_content = content
        else:
            self.original_content = ''

        self.title = f'Text Editor - {self.filepath.name}'
        self.sub_title = str(self.filepath)

    def on_text_area_changed(self, event: tx.TextArea.Changed) -> None:
        """Track if the document has been modified."""

        if self.text_area:
            current_content = self.text_area.text
            self.modified = current_content != self.original_content

            # Update title to show modified status
            status = ' *' if self.modified else ''
            self.title = f'Text Editor - {self.filepath.name}{status}'

    def action_save(self) -> None:
        """Save the current content to file."""

        if self.text_area:
            content = self.text_area.text
            self.filepath.write_text(content)
            self.original_content = content
            self.modified = False
            self.title = f'Text Editor - {self.filepath.name}'
            self.notify(f'Saved to {self.filepath.name}')

    async def action_quit(self) -> None:
        """Quit the editor, prompting to save if modified."""

        if self.modified:
            def check_quit(should_save: bool | None) -> None:
                if should_save is None:
                    # User cancelled
                    return

                if should_save:
                    self.action_save()

                self.exit()

            await self.push_screen(QuitConfirmScreen(), callback=check_quit)

        else:
            self.exit()


def main() -> None:
    """Parse arguments and run the editor."""

    parser = argparse.ArgumentParser(description='Simple text editor')
    parser.add_argument('filename', help='File to edit')
    args = parser.parse_args()

    filepath = pathlib.Path(args.filename).resolve()

    # Create parent directories if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)

    app = TextEditor(filepath)
    app.run()


if __name__ == '__main__':
    main()
