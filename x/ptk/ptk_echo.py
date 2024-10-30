from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.widgets import TextArea, Label
from prompt_toolkit.key_binding import KeyBindings

# Read-only text area
log_area = TextArea(style='class:log-area', read_only=True, scrollbar=True)

# Input field at the bottom
input_field = TextArea(height=1, prompt='> ', multiline=False)

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

# Create the application
app = Application(layout=layout, key_bindings=bindings, full_screen=True)

# Run the application
app.run()
