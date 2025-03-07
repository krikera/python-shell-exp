import sys
import os
import shutil
import subprocess
import shlex
import readline

SHELL_BUILTINS = [
    "alias", "bg", "bind", "break", "cd", "command", "continue", "declare",
    "dirs", "echo", "enable", "eval", "exec", "exit", "export", "fg",
    "getopts", "hash", "help", "history", "jobs", "kill", "let", "local",
    "logout", "popd", "pushd", "pwd", "read", "readonly", "return", "set",
    "shift", "shopt", "source", "test", "times", "trap", "type", "ulimit",
    "umask", "unalias", "unset", "wait"
]

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

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            inputT = input().strip()
        except EOFError:
            break
        if not inputT:
            continue
        try:
            parts = shlex.split(inputT)
        except ValueError as e:
            print(f"Error parsing command: {e}")
            continue
        if not parts:
            continue
        command = []
        stdout_redirection = None
        stdout_mode = None
        stderr_redirection = None
        stderr_mode = None
        stdin_redirection = None 
        i = 0
        while i < len(parts):
            if parts[i] in (">", "1>"):
                if i + 1 < len(parts):
                    stdout_redirection = parts[i + 1]
                    stdout_mode = "w"
                    i += 1
                else:
                    print("Syntax error: missing file for > or 1>")
                    break
            elif parts[i] in (">>", "1>>"):
                if i + 1 < len(parts):
                    stdout_redirection = parts[i + 1]
                    stdout_mode = "a"
                    i += 1
                else:
                    print("Syntax error: missing file for >> or 1>>")
                    break
            elif parts[i] == "2>":
                if i + 1 < len(parts):
                    stderr_redirection = parts[i + 1]
                    stderr_mode = "w"
                    i += 1
                else:
                    print("Syntax error: missing file for 2>")
                    break
            elif parts[i] == "2>>":
                if i + 1 < len(parts):
                    stderr_redirection = parts[i + 1]
                    stderr_mode = "a"
                    i += 1
                else:
                    print("Syntax error: missing file for 2>>")
                    break
            elif parts[i] == "<": 
                if i + 1 < len(parts):
                    stdin_redirection = parts[i + 1]
                    i += 1
                else:
                    print("Syntax error: missing file for <")
                    break
            else:
                command.append(parts[i])
            i += 1
        else:
            if not command:
                continue
            cmd_name = command[0]
            args = command[1:]
            if cmd_name == "type":
                if not args:
                    error_msg = "type: missing operand\n"
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            f.write(error_msg)
                    else:
                        sys.stderr.write(error_msg)
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
                else:
                    shell_built_in = args[0]
                    if shell_built_in in SHELL_BUILTINS:
                        output_text = f"{shell_built_in} is a shell builtin\n"
                    else:
                        path_to_cmd = shutil.which(shell_built_in)
                        if path_to_cmd:
                            output_text = f"{shell_built_in} is {path_to_cmd}\n"
                        else:
                            output_text = f"{shell_built_in}: not found\n"
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            f.write(output_text)
                    else:
                        sys.stdout.write(output_text)
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            pass
            elif cmd_name == "cd":
                try:
                    target_dir = os.path.expanduser(args[0]) if args else os.path.expanduser("~")
                    os.chdir(target_dir)
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            pass
                except FileNotFoundError:
                    error_msg = f"cd: {args[0]}: No such file or directory\n"
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            f.write(error_msg)
                    else:
                        sys.stderr.write(error_msg)
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
            elif cmd_name == "exit":
                if args and args[0] != "0":
                    error_msg = "exit: invalid argument\n"
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            f.write(error_msg)
                    else:
                        sys.stderr.write(error_msg)
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
                else:
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            pass
                    break
            elif cmd_name == "pwd":
                output_text = os.getcwd() + "\n"
                if stdout_redirection:
                    with open(stdout_redirection, stdout_mode) as f:
                        f.write(output_text)
                else:
                    sys.stdout.write(output_text)
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        pass
            elif cmd_name == "echo":
                output_text = " ".join(args) + "\n"
                if stdout_redirection:
                    with open(stdout_redirection, stdout_mode) as f:
                        f.write(output_text)
                else:
                    sys.stdout.write(output_text)
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        pass
            else:
                path_to_cmd = shutil.which(cmd_name)
                if path_to_cmd:
                    stdout_target = None
                    stderr_target = None
                    stdin_target = None 
                    try:
                        if stdout_redirection:
                            stdout_target = open(stdout_redirection, stdout_mode)
                        if stderr_redirection:
                            stderr_target = open(stderr_redirection, stderr_mode)
                        if stdin_redirection:
                            stdin_target = open(stdin_redirection, 'r')
                        subprocess.run(
                            [cmd_name] + args,
                            stdout=stdout_target,
                            stderr=stderr_target,
                            stdin=stdin_target 
                        )
                    except FileNotFoundError:
                        error_msg = f"{cmd_name}: not found\n"
                        if stderr_redirection:
                            with open(stderr_redirection, stderr_mode) as f:
                                f.write(error_msg)
                        else:
                            sys.stderr.write(error_msg)
                        if stdout_redirection:
                            with open(stdout_redirection, stdout_mode) as f:
                                pass
                    except PermissionError:
                        error_msg = f"{cmd_name}: permission denied\n"
                        if stderr_redirection:
                            with open(stderr_redirection, stderr_mode) as f:
                                f.write(error_msg)
                        else:
                            sys.stderr.write(error_msg)
                        if stdout_redirection:
                            with open(stdout_redirection, stdout_mode) as f:
                                pass
                    finally:
                        if stdout_target:
                            stdout_target.close()
                        if stderr_target:
                            stderr_target.close()
                        if stdin_target: 
                            stdin_target.close()
                else:
                    error_msg = f"{cmd_name}: command not found\n"
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            f.write(error_msg)
                    else:
                        sys.stderr.write(error_msg)
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass

if __name__ == "__main__":
    main()