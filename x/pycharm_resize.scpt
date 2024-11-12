tell application "System Events"
    -- Specify the target application by its name
    set targetApp to application process "PyCharm"

    -- Ensure the application is running
    if targetApp exists then
        -- Access the front window of the specified application
        set targetWindow to front window of targetApp

        -- Access the first-level group inside the window
        set group1 to (first group of targetWindow whose description is "Root Pane")

        -- Access the second-level group inside the first group
        set targetElement to (first group of group1 whose description is "Project Tool Window")

        -- Get the current size of the element
        set currentSize to size of targetElement
        set currentWidth to item 1 of currentSize
        set currentHeight to item 2 of currentSize
        log currentSize

        -- Set a new width while preserving the original height
        set newWidth to 700
        set newSize to {newWidth, currentHeight}
        set size of targetElement to newSize

    else
        display dialog "PyCharm is not running."
    end if
end tell
