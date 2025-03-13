import os
import sys
import readline
from utils import SHELL_BUILTINS

last_tab_prefix = ""
tab_pressed_once = False

def get_matching_executables(text):
    """Get all executables in PATH that match the given prefix."""
    matches = []
    matches.extend([cmd for cmd in SHELL_BUILTINS if cmd.startswith(text)])
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for dir_path in path_dirs:
        if os.path.isdir(dir_path):
            try:
                for filename in os.listdir(dir_path):
                    filepath = os.path.join(dir_path, filename)
                    if os.path.isfile(filepath) and os.access(filepath, os.X_OK):
                        if filename.startswith(text):
                            matches.append(filename)
            except (PermissionError, FileNotFoundError):
                pass
    return sorted(set(matches))

def find_longest_common_prefix(strings):
    """Find the longest common prefix of a list of strings."""
    if not strings:
        return ""
    if len(strings) == 1:
        return strings[0]
    prefix = strings[0]
    for i in range(len(prefix)):
        for string in strings:
            if i >= len(string) or string[i] != prefix[i]:
                return prefix[:i]
    return prefix

def completer(text, state):
    global last_tab_prefix, tab_pressed_once
    buffer = readline.get_line_buffer()
    words = buffer.split()
    if len(words) == 0 or (len(words) == 1 and not buffer.endswith(' ')):
        matches = get_matching_executables(text)
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0] + " " if state == 0 else None
        common_prefix = find_longest_common_prefix(matches)
        if len(common_prefix) > len(text):
            return common_prefix if state == 0 else None
        if common_prefix == text and tab_pressed_once:
            if state == 0:
                print()
                print("  ".join(matches))
                print(f"$ {text}", end="")
                tab_pressed_once = False
            return None
        if common_prefix == text:
            tab_pressed_once = True
            sys.stdout.write('\a')
            sys.stdout.flush()
            return None
    tab_pressed_once = False
    return None

def setup_completion():
    """Set up tab completion."""
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")