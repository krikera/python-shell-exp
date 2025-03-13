import os
import sys
import readline
import shutil
from utils import shell_variables, last_exit_code, SHELL_BUILTINS, HELP_TEXT

def execute_builtin(cmd_name, args, stdout_redirection=None, stdout_mode=None,
                   stderr_redirection=None, stderr_mode=None, stdin_redirection=None):
    """Execute a built-in command and return its output."""
    global shell_variables, last_exit_code
    
    output = ""
    
    if cmd_name == "help":
        if not args:
            output = "Shell built-in commands:\n\n"
            commands = sorted(HELP_TEXT.keys())
            command_list = "\n".join([f"  {cmd}" for cmd in commands])
            output += command_list + "\n\n"
            output += "Type 'help command' to find out more about the function of a specific command.\n"
        else:
            command = args[0]
            if command in HELP_TEXT:
                output = HELP_TEXT[command] + "\n"
            else:
                error_msg = f"help: no help topics match '{command}'.\n"
                if stderr_redirection:
                    with open(stderr_redirection, stderr_mode) as f:
                        f.write(error_msg)
                else:
                    sys.stderr.write(error_msg)
                last_exit_code = 1
                return ""
        
        if stdout_redirection:
            with open(stdout_redirection, stdout_mode) as f:
                f.write(output)
        else:
            sys.stdout.write(output)
        
        last_exit_code = 0
    elif cmd_name == "history":
        if len(args) == 1 and args[0].isdigit():
            num_entries = min(int(args[0]), readline.get_current_history_length())
        else:
            num_entries = readline.get_current_history_length()
        
        output_lines = []
        for i in range(1, num_entries + 1):
            idx = readline.get_current_history_length() - num_entries + i
            if idx > 0:
                output_lines.append(f"{idx:5d}  {readline.get_history_item(idx)}")
        
        output = "\n".join(output_lines) + "\n" if output_lines else ""
        
        if stdout_redirection:
            with open(stdout_redirection, stdout_mode) as f:
                f.write(output)
        else:
            sys.stdout.write(output)
        
        if stderr_redirection:
            with open(stderr_redirection, stderr_mode) as f:
                pass
        
        last_exit_code = 0
        
    elif cmd_name == "export":
        if not args:
            output = "\n".join([f"{key}={value}" for key, value in sorted(shell_variables.items())])
            if stdout_redirection:
                with open(stdout_redirection, stdout_mode) as f:
                    f.write(output + "\n")
            else:
                sys.stdout.write(output + "\n")
            
            output += "\n"
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
                output = f"{shell_built_in} is a shell builtin\n"
            else:
                path_to_cmd = shutil.which(shell_built_in)
                if path_to_cmd:
                    output = f"{shell_built_in} is {path_to_cmd}\n"
                else:
                    output = f"{shell_built_in}: not found\n"
                    last_exit_code = 1
                    
            if stdout_redirection:
                with open(stdout_redirection, stdout_mode) as f:
                    f.write(output)
            else:
                sys.stdout.write(output)
                
            if stderr_redirection:
                with open(stderr_redirection, stderr_mode) as f:
                    pass
                    
            if "not found" not in output:
                last_exit_code = 0
                
    elif cmd_name == "cd":
        try:
            target_dir = args[0] if args else "~"
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
                return ""
        if stdout_redirection:
            with open(stdout_redirection, stdout_mode) as f:
                pass
        if stderr_redirection:
            with open(stderr_redirection, stderr_mode) as f:
                pass
        raise SystemExit(exit_code)
        
    elif cmd_name == "pwd":
        output = os.getcwd() + "\n"
        if stdout_redirection:
            with open(stdout_redirection, stdout_mode) as f:
                f.write(output)
        else:
            sys.stdout.write(output)
        if stderr_redirection:
            with open(stderr_redirection, stderr_mode) as f:
                pass
        last_exit_code = 0
        
    elif cmd_name == "echo":
        output = " ".join(args) + "\n"
        if stdout_redirection:
            with open(stdout_redirection, stdout_mode) as f:
                f.write(output)
        else:
            sys.stdout.write(output)
        if stderr_redirection:
            with open(stderr_redirection, stderr_mode) as f:
                pass
        last_exit_code = 0
        
    return output