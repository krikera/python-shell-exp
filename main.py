import sys
import os
import shutil
import subprocess
import shlex
import readline
import re
import atexit

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
shell_variables = dict(os.environ)
last_exit_code = 0
history_file = os.path.expanduser("~/.python_shell_history")
history_size = 1024

def setup_history():
    """Set up command history with readline"""
    try:
        readline.read_history_file(history_file)
        readline.set_history_length(history_size)
    except FileNotFoundError:
        open(history_file, 'a').close()
    
    atexit.register(readline.write_history_file, history_file)

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

def expand_variables(text):
    """Expand environment variables in the given text."""
    global shell_variables, last_exit_code
    
    text = text.replace("$$", str(os.getpid()))
    text = text.replace("$?", str(last_exit_code))
    
    def replace_var(match):
        var_name = match.group(1)
        return shell_variables.get(var_name, "")
    
    text = re.sub(r'\${([^}]+)}', replace_var, text)
    
    def replace_simple_var(match):
        var_name = match.group(1)
        return shell_variables.get(var_name, "")
    
    text = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', replace_simple_var, text)
    
    return text

def parse_input(input_text):
    """Parse input with variable expansion respecting quotes."""
    result = []
    current_token = ""
    i = 0
    in_single_quote = False
    in_double_quote = False
    
    while i < len(input_text):
        char = input_text[i]
        
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            i += 1
            continue
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            i += 1
            continue
        
        if char == '\\' and i + 1 < len(input_text):
            current_token += input_text[i + 1]
            i += 2
            continue
        
        if char == '$' and not in_single_quote and i + 1 < len(input_text):
            if input_text[i + 1] == '{':
                end_brace = input_text.find('}', i + 2)
                if end_brace != -1:
                    var_name = input_text[i + 2:end_brace]
                    current_token += shell_variables.get(var_name, "")
                    i = end_brace + 1
                    continue
            elif input_text[i + 1] == '$':
                current_token += str(os.getpid())
                i += 2
                continue
            elif input_text[i + 1] == '?':
                current_token += str(last_exit_code)
                i += 2
                continue
            else:
                var_end = i + 1
                while var_end < len(input_text) and (input_text[var_end].isalnum() or input_text[var_end] == '_'):
                    var_end += 1
                if var_end > i + 1:
                    var_name = input_text[i + 1:var_end]
                    current_token += shell_variables.get(var_name, "")
                    i = var_end
                    continue
        
        if char.isspace() and not in_single_quote and not in_double_quote:
            if current_token:
                result.append(current_token)
                current_token = ""
        else:
            current_token += char
        
        i += 1
    
    if current_token:
        result.append(current_token)
    
    return result

def main():
    global shell_variables, last_exit_code
    
    setup_history()
    
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            inputT = input().strip()
        except EOFError:
            break
        if not inputT:
            continue
            
        if inputT.strip():
            readline.add_history(inputT)

        try:
            parts = shlex.split(inputT)
            
            expanded_parts = []
            for part in parts:
                expanded_parts.append(expand_variables(part))
            parts = expanded_parts
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
            
            if cmd_name == "history":
                if len(args) == 1 and args[0].isdigit():
                    num_entries = min(int(args[0]), readline.get_current_history_length())
                else:
                    num_entries = readline.get_current_history_length()
                
                output_lines = []
                for i in range(1, num_entries + 1):
                    idx = readline.get_current_history_length() - num_entries + i
                    if idx > 0:
                        output_lines.append(f"{idx:5d}  {readline.get_history_item(idx)}")
                
                output_text = "\n".join(output_lines) + "\n" if output_lines else ""
                
                if stdout_redirection:
                    with open(stdout_redirection, stdout_mode) as f:
                        f.write(output_text)
                else:
                    sys.stdout.write(output_text)
                
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        pass
                
                last_exit_code = 0
                
            elif cmd_name == "export":
                if not args:
                    
                    output_text = "\n".join([f"{key}={value}" for key, value in sorted(shell_variables.items())])
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            f.write(output_text + "\n")
                    else:
                        sys.stdout.write(output_text + "\n")
                else:
                    for arg in args:
                        if "=" in arg:
                            key, value = arg.split("=", 1)
                            shell_variables[key] = value
                            os.environ[key] = value
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        pass
                last_exit_code = 0
            elif cmd_name == "type":
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
                    last_exit_code = 1
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
                            last_exit_code = 1
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            f.write(output_text)
                    else:
                        sys.stdout.write(output_text)
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            pass
                    if "not found" not in output_text:
                        last_exit_code = 0
            elif cmd_name == "cd":
                try:
                    target_dir = os.path.expanduser(args[0]) if args else os.path.expanduser("~")
                    os.chdir(target_dir)
                    shell_variables["PWD"] = os.getcwd()
                    os.environ["PWD"] = os.getcwd()
                    if stdout_redirection:
                        with open(stdout_redirection, stdout_mode) as f:
                            pass
                    if stderr_redirection:
                        with open(stderr_redirection, stderr_mode) as f:
                            pass
                    last_exit_code = 0
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
                    last_exit_code = 1
            elif cmd_name == "exit":
                exit_code = 0
                if args:
                    try:
                        exit_code = int(args[0])
                    except ValueError:
                        error_msg = "exit: invalid argument\n"
                        if stderr_redirection:
                            with open(stderr_redirection, stderr_mode) as f:
                                f.write(error_msg)
                        else:
                            sys.stderr.write(error_msg)
                        if stdout_redirection:
                            with open(stdout_redirection, stdout_mode) as f:
                                pass
                        last_exit_code = 1
                        continue
                if stdout_redirection:
                    with open(stdout_redirection, stdout_mode) as f:
                        pass
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        pass
                raise SystemExit(exit_code)
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
                last_exit_code = 0
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
                last_exit_code = 0
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
                        process = subprocess.run(
                            [cmd_name] + args,
                            stdout=stdout_target,
                            stderr=stderr_target,
                            stdin=stdin_target,
                            env=shell_variables  
                        )
                        last_exit_code = process.returncode
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
                        last_exit_code = 127
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
                        last_exit_code = 126
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
                    last_exit_code = 127

if __name__ == "__main__":
    main()