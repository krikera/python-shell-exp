# Python Shell Emulator

This project is a lightweight command-line shell emulator written in Python. It implements basic command execution, tab completion, and redirection features similar to those found in traditional Unix shells.

## Features

- **Tab Completion**:  
  Automatically completes both built-in commands and external executables found in your system's `PATH`.

- **Built-in Commands**:  
  Supports a handful of common built-ins including:
  - `type`: Identifies whether a command is a shell built-in or an external executable.
  - `cd`: Changes the current working directory.
  - `exit`: Exits the shell.
  - `pwd`: Prints the current working directory.
  - `echo`: Displays text on the terminal.

- **Command Redirection**:  
  Basic support for redirecting input, output, and errors:
  - `>` or `1>`: Redirect standard output to a file (write mode).
  - `>>` or `1>>`: Redirect standard output to a file (append mode).
  - `2>`: Redirect standard error to a file (write mode).
  - `2>>`: Redirect standard error to a file (append mode).
  - `<`: Redirect standard input from a file.

- **External Command Execution**:  
  Executes external commands by searching for them in your system's `PATH` with proper error handling for cases like command not found or permission issues.

## Requirements

- **Python 3.x**
- Standard Python libraries:
  - `sys`
  - `os`
  - `shutil`
  - `subprocess`
  - `shlex`
  - `readline`

## Usage

1. **Run the Shell**:  
   Execute the script from the terminal:
   ```bash
   python main.py
   ```
