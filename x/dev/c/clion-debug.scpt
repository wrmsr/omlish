-- inspector
tell application "System Events" to tell process "clion"
  set theWindow to first window whose name starts with "cpython "
  set frontmost to true
  perform action "AXRaise" of theWindow
  tell menu bar item "Run" of menu bar 1
    click
    click menu item "Attach to Process..." of menu 1
  end tell

  delay 0.5
  set theWindow to first window whose name is "Attach to Process"
  perform action "AXRaise" of theWindow
  tell text field 1 of theWindow
    set focused to true
    --set value to "barf"
    -- keystroke "a"
    --delay 0.1
    -- keystroke (key code 36)
    keystroke "a"
    keystroke "b"
    keystroke "c"
  end tell
  keystroke (key code 36)
end tell
