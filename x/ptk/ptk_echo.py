from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import TextArea


# Read-only text area
log_area = TextArea(
    text='\n'.join(f'line {i}' for i in range(50)),
    style='class:log-area',
    scrollbar=True,
    focusable=False,
)


# Input field at the bottom
input_field = TextArea(
    height=1,
    prompt='> ',
    multiline=False,
)


# Add the input to the log area
def accept_text(buff):
    text = input_field.text
    log_area.buffer.insert_text(text + '\n')
    input_field.text = ''


input_field.accept_handler = accept_text

# Layout with HSplit for vertical stacking
layout = Layout(HSplit([log_area, input_field]))

# Key bindings
bindings = KeyBindings()


@bindings.add('c-c')
def exit_app(event):
    event.app.exit()


# Page Up: Scroll up the log area
@bindings.add('pageup')
def page_up(event):
    log_area.buffer.cursor_up(count=10)


# Page Down: Scroll down the log area
@bindings.add('pagedown')
def page_down(event):
    log_area.buffer.cursor_down(count=10)


# Create the application
app = Application(
    layout=layout,
    key_bindings=bindings,
    full_screen=True
)

# Set initial focus to the input field
layout.focus(input_field)

# Run the application
app.run()
