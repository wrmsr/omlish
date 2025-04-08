import asyncio
import datetime
import functools
import typing as ta

from omdev import ptk


##


class LiveView:
    """
    Displays dynamically updating content in the terminal without using the full screen, similar to rich.Live but using
    prompt-toolkit Application.

    Note: Intermediate updates are generally NOT preserved in scrollback history. Only the final state remains visible
    after the view exits.
    """

    def __init__(
        self,
        initial_content: ptk.AnyFormattedText = '',
        style: ptk.Style | None = None,
        title: str | None = None,
    ) -> None:
        """
        Initializes the LiveView component.

        Args:
            initial_content: The initial content to display (str, HTML, etc.).
            style: An optional prompt_toolkit Style object to merge with defaults.
            title: An optional title string to display above the content.
        """

        super().__init__()

        self._content: ptk.AnyFormattedText = initial_content
        self._custom_style = style
        self._title = title
        self._is_running = False
        self._app = self._build_app()

    def _get_content(self) -> ptk.AnyFormattedText:
        """Internal method used by FormattedTextControl to get current content."""

        return self._content

    def _build_app(self) -> ptk.Application:
        """Constructs the prompt_toolkit Application object."""

        content_control = ptk.FormattedTextControl(
            text=self._get_content,
        )

        content_window = ptk.Window(
            content=content_control,
            dont_extend_height=True, # Avoids taking up full terminal height
            wrap_lines=True, # Allow content to wrap
        )

        # Create the root container, optionally adding a title bar
        root_container: ptk.Container
        if self._title:
            # Use HTML for simple title formatting
            title_control = ptk.FormattedTextControl(
                text=ptk.HTML(f'<b>{self._title}</b>'),
            )

            title_window = ptk.Window(
                content=title_control,
                height=1, # Title is one line high
                style='class:liveview-title', # Apply specific style
                dont_extend_height=True,
            )

            # Simple separator line
            separator_window = ptk.Window(
                height=1,
                char='─',
                style='class:liveview-separator',
            )

            # Arrange vertically: Title, Separator, Content
            root_container = ptk.HSplit([title_window, separator_window, content_window])

        else:
            # No title, just the content window
            root_container = content_window

        layout = ptk.Layout(container=root_container)

        kb = ptk.KeyBindings()
        @kb.add('c-c', eager=True)
        @kb.add('c-d', eager=True) # Also allow Ctrl+D to exit
        def _handle_exit(event: ptk.KeyPressEvent) -> None:
            """Handle Ctrl+C or Ctrl+D: Exit the application gracefully."""

            # The reason for exit is passed back via app.exit()
            event.app.exit(result=f'Cancelled by user ({event.key_sequence[0].key})')

        # Define default styles for the view components
        default_style = ptk.Style.from_dict({
            'liveview-title': 'fg:ansiblue bold underline',
            'liveview-separator': 'fg:#888888',
            # Add styles for the main content window background/text if desired
            # "default": "bg:#f0f0f0 #000000",
        })

        # Merge default styles with any custom styles provided
        final_style: ptk.BaseStyle
        if self._custom_style:
            final_style = ptk.merge_styles([default_style, self._custom_style])
        else:
            final_style = default_style

        app: ptk.Application = ptk.Application(
            layout=layout,
            key_bindings=kb,
            style=final_style,
            full_screen=False,      # <<<<< Core setting for non-full-screen behavior
            refresh_interval=None,  # Disable automatic refresh, rely on invalidate()
            # mouse_support=True,   # Optional: enable mouse events if needed
        )

        return app

    def update(self, new_content: ptk.AnyFormattedText) -> None:
        """
        Updates the content displayed by the LiveView.

        Call this method from your code whenever the content should change. This method is designed to be safe to call
        from different threads or asyncio tasks relative to where run_async is awaited.

        Args:
            new_content: The new content (str, HTML, FormattedText, etc.).
        """

        self._content = new_content

        # Safely schedule a UI redraw within the application's event loop
        if self._is_running and self._app and self._app.loop:
            # call_from_executor ensures thread/async safety
            ptk.call_soon_threadsafe(self._app.invalidate)

    async def run_async(self) -> ta.Any | None:
        """
        Runs the LiveView application asynchronously until it exits.

        Returns:
            The value passed to `app.exit()` or `self.stop()`.

        Raises:
            RuntimeError: If the LiveView is already running.
        """

        if self._is_running:
            raise RuntimeError('LiveView is already running.')

        self._is_running = True
        try:
            # This will run the application's event loop
            result = await self._app.run_async()
            return result

        finally:
            # Ensure the flag is reset when execution finishes or raises
            self._is_running = False

    def stop(self, result: ta.Any | None = 'Stopped programmatically'):
        """
        Requests the running LiveView application to stop gracefully.

        Safe to call from different threads or asyncio tasks.

        Args:
            result: The value to be returned by the run_async() call.
        """

        if self._is_running and self._app and self._app.loop:
            # Safely schedule the exit call within the app's event loop
            ptk.call_soon_threadsafe(functools.partial(self._app.exit, result))


async def example_usage() -> None:
    """Demonstrates how to instantiate and use the LiveView class."""

    # Use current time from datetime to avoid collision with time module import
    now_func = datetime.datetime.now

    print('Initializing LiveView...')

    # Create an instance with a title and initial content
    live_view = LiveView(
        initial_content=ptk.HTML('<i>Waiting for first update...</i>'),
        title='Real-time Status Dashboard',
    )

    async def background_task_simulator() -> None:
        """Simulates external events updating the LiveView."""

        try:
            status_messages = [
                'Connecting to server...',
                'Authenticating...',
                'Fetching data batch 1...',
                'Processing batch 1...',
                'Fetching data batch 2...',
                'Processing batch 2...',
                'Generating report...',
                'Almost done...',
            ]

            for i, status in enumerate(status_messages):
                # Simulate work
                await asyncio.sleep(.2)
                current_time = now_func().strftime('%H:%M:%S.%f')[:-3]

                # Prepare new content using HTML formatting
                content = ptk.HTML(
                    f'Timestamp: <ansiyellow>{current_time}</ansiyellow>\n'
                    f'Progress: <ansigreen>{i+1}/{len(status_messages)}</ansigreen>\n'
                    f'Status:   <b>{status}</b>',
                )

                # Push the update to the LiveView instance
                live_view.update(content)

            # Final update after loop
            await asyncio.sleep(0.5)

            # live_view.update(HTML("<b ansidefault bg:ansigreen> Processing Complete! </b>"))
            live_view.update(ptk.HTML('<b> Processing Complete! </b>'))
            await asyncio.sleep(2.0) # Keep final status visible

            # Programmatically stop the LiveView when done
            print('\nBackground task finished, stopping LiveView...')
            live_view.stop(result='Task Completed Successfully')

        except asyncio.CancelledError:
            print('\nBackground task was cancelled.')
            # Optionally update the view one last time on cancellation
            # live_view.update(HTML("<b ansired>Task Cancelled!</b>"))
            # If cancelled, don't call stop(), let run_async return from Ctrl+C etc.

    print('Starting LiveView. Press Ctrl+C or Ctrl+D to exit early.')

    # Run the LiveView UI and the background task concurrently
    view_task = asyncio.create_task(live_view.run_async())
    bg_task = asyncio.create_task(background_task_simulator())

    # Wait for the LiveView UI task to complete. It will finish either by the background task calling stop() or by user
    # (Ctrl+C/D)
    exit_result = await view_task
    print(f'\nLiveView exited with result: {exit_result}')

    # Clean up the background task if the view task finished before it (e.g., user pressed Ctrl+C)
    if not bg_task.done():
        print('View exited early, cancelling background task...')
        bg_task.cancel()
        try:
            await bg_task  # Allow cancellation to propagate
        except asyncio.CancelledError:
            print('Background task successfully cancelled.')


if __name__ == '__main__':
    try:
        # Run the main async function for the example
        asyncio.run(example_usage())
    except KeyboardInterrupt:
        # Catch Ctrl+C at the top level if it happens outside the app's handling
        print('\nCaught KeyboardInterrupt in main script. Exiting.')
    finally:
        print('LiveView example script finished.')
