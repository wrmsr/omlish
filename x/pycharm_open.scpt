on run argv
    set projectPath to item 1 of argv
    tell application "PyCharm"
        activate
        open projectPath
    end tell
end run
