"""
This module provides OS-specific utilities, such as getting selected text.
"""
import platform
import subprocess
import sys
import time
from typing import Optional

import pyperclip


def run_applescript(script: str) -> Optional[str]:
    """Executes an AppleScript command and returns the output."""
    if platform.system() != "Darwin":
        print(
            "Error: AppleScript can only be run on macOS.",
            file=sys.stderr,
        )
        return None
    try:
        process = subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(
                f"AppleScript Error: {stderr.decode('utf-8').strip()}",
                file=sys.stderr,
            )
            return None

        return stdout.decode("utf-8").strip()

    except FileNotFoundError:
        print(
            "Error: 'osascript' command not found. This script can only be run on macOS.",
            file=sys.stderr,
        )
        return None
    except Exception as e:
        print(
            f"An error occurred while running AppleScript: {e}",
            file=sys.stderr,
        )
        return None


def get_selected_text_macos() -> str:
    """
    Gets the currently selected text on macOS using AppleScript to trigger a copy.

    This function saves the current clipboard content, uses AppleScript to tell
    the active application to copy, reads the clipboard, and then restores the
    original clipboard content.

    Returns:
        str: The selected text, or an empty string if no text was selected
             or an error occurred.
    """
    original_clipboard = pyperclip.paste()

    try:
        pyperclip.copy("")
        copy_script = """
            tell application "System Events"
                tell (process 1 where it is frontmost)
                    try
                        click menu item "Copy" of menu "Edit" of menu bar 1
                    on error
                        key code 8 using {command down}
                    end try
                end tell
            end tell
        """
        run_applescript(copy_script)
        time.sleep(0.1)
        selected_text = pyperclip.paste()
        return selected_text

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return ""

    finally:
        pyperclip.copy(original_clipboard)


def get_selected_text() -> str:
    """
    Gets the currently selected text.

    This function is a wrapper that calls the OS-specific implementation.
    Currently, it only supports macOS.

    Returns:
        str: The selected text, or an empty string if not supported on the current OS.
    """
    if platform.system() == "Darwin":
        return get_selected_text_macos()
    else:
        print(
            f"Warning: Getting selected text is not supported on {platform.system()}.",
            file=sys.stderr,
        )
        return ""


if __name__ == "__main__":
    print("This script will get the selected text on your Mac in 5 seconds.")
    print("Please switch to another application and select some text now...")

    time.sleep(5)

    print("\nGetting selected text...")

    text = get_selected_text()

    if text:
        print("\n--- Selected Text ---")
        print(text)
        print("---------------------\n")
    else:
        print("\nNo text was selected or an error occurred.")
        print("Make sure the window with the selected text was active.")

    print("Your original clipboard has been restored.")
