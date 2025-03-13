import sys
import os
import shutil
import subprocess
import shlex
import readline
import atexit

from utils import shell_variables, last_exit_code, history_file, history_size, SHELL_BUILTINS
from parser import expand_variables, expand_tilde, parse_command_tokens
from builtin import execute_builtin
from completion import setup_completion

def setup_history():
    """Set up command history with readline"""
    try:
        readline.read_history_file(history_file)
        readline.set_history_length(history_size)
    except FileNotFoundError:
        open(history_file, 'a').close()
    
    atexit.register(readline.write_history_file, history_file)

def execute_command(tokens, input_data=None):
    """Execute a command with possible redirections and return its output."""
    global shell_variables, last_exit_code
    
    cmd_tokens, stdout_redirection, stdout_mode, stderr_redirection, stderr_mode, stdin_redirection = parse_command_tokens(tokens)
    
    if not cmd_tokens:
        return None
    
    cmd_name = cmd_tokens[0]
    args = cmd_tokens[1:]
    
    if cmd_name in SHELL_BUILTINS:
        if input_data is not None:
            # TODO: Handle input data for builtins if needed
            pass
        
        return execute_builtin(cmd_name, args, stdout_redirection, stdout_mode, 
                               stderr_redirection, stderr_mode, stdin_redirection)
    
    path_to_cmd = shutil.which(cmd_name)
    if path_to_cmd:
        try:
            if stdout_redirection:
                stdout_target = open(stdout_redirection, stdout_mode)
            else:
                stdout_target = subprocess.PIPE
            
            if stderr_redirection:
                stderr_target = open(stderr_redirection, stderr_mode)
            else:
                stderr_target = subprocess.PIPE
            
            if input_data is not None:
                stdin_target = subprocess.PIPE
            elif stdin_redirection:
                stdin_target = open(stdin_redirection, 'r')
            else:
                stdin_target = None
            
            process = subprocess.Popen(
                [cmd_name] + args,
                stdout=stdout_target,
                stderr=stderr_target,
                stdin=stdin_target,
                text=True,
                env=shell_variables
            )
            
            stdout_data, stderr_data = process.communicate(input=input_data)
            
            if stdout_redirection and stdout_target != subprocess.PIPE:
                stdout_target.close()
            if stderr_redirection and stderr_target != subprocess.PIPE:
                stderr_target.close()
            if stdin_redirection and stdin_target != subprocess.PIPE:
                stdin_target.close()
            
            last_exit_code = process.returncode
            return stdout_data
            
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
    
    return None

def execute_pipeline(commands):
    """Execute a pipeline of commands."""
    if not commands:
        return
    
    if len(commands) == 1:
        output = execute_command(commands[0])
        # Only print output if it's from an external command, not a builtin
        if output and commands[0][0] not in SHELL_BUILTINS:
            sys.stdout.write(output)
        return
    
    first_output = execute_command(commands[0])
    
    current_input = first_output
    for i in range(1, len(commands) - 1):
        current_input = execute_command(commands[i], current_input)
    
    execute_command(commands[-1], current_input)

def run_shell():
    """Run the main shell loop."""
    global shell_variables, last_exit_code
    
    setup_history()
    setup_completion()
    
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
            commands = []
            current_command = []
            in_single_quote = False
            in_double_quote = False
            
            parts = shlex.split(inputT)
            
            # Expand variables and tildes
            expanded_parts = []
            for part in parts:
                expanded_part = expand_variables(part)
                expanded_part = expand_tilde(expanded_part)
                expanded_parts.append(expanded_part)
            parts = expanded_parts
            
            # Group commands by pipes
            current_command = []
            for part in parts:
                if part == "|" and not in_single_quote and not in_double_quote:
                    if current_command:
                        commands.append(current_command)
                        current_command = []
                else:
                    current_command.append(part)
            
            if current_command:
                commands.append(current_command)
                
            if commands:
                execute_pipeline(commands)
                
        except ValueError as e:
            print(f"Error parsing command: {e}")
            continue