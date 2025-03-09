# Python Shell Emulator

This project is a lightweight command-line shell emulator written in Python. It implements basic command execution, tab completion, redirection features, and command history similar to those found in traditional Unix shells.

## Features

- **Tab Completion**:  
  Automatically completes both built-in commands and external executables found in your system's `PATH`.

- **Command History**:  
  - Tracks commands entered during the current and previous sessions
  - Navigate through history using up/down arrow keys
  - View command history with the `history` command
  - Limit history display with `history N` (shows last N commands)
  - History persists between shell sessions in `~/.python_shell_history`
  - Supports redirection of history output to files

- **Built-in Commands**:  
  Supports a handful of common built-ins including:
  - `type`: Identifies whether a command is a shell built-in or an external executable.
  - `cd`: Changes the current working directory.
  - `exit`: Exits the shell.
  - `pwd`: Prints the current working directory.
  - `echo`: Displays text on the terminal.
  - `export`: Sets or displays environment variables.
  - `history`: Displays command history.

- **Command Redirection**:  
  Basic support for redirecting input, output, and errors:
  - `>` or `1>`: Redirect standard output to a file (write mode).
  - `>>` or `1>>`: Redirect standard output to a file (append mode).
  - `2>`: Redirect standard error to a file (write mode).
  - `2>>`: Redirect standard error to a file (append mode).
  - `<`: Redirect standard input from a file.

- **Environment Variables**:  
  Full support for environment variable management:
  - Set variables using `export VAR=value`.
  - Use variables in commands with `$VAR` or `${VAR}` syntax.
  - Access special variables like `$$` (process ID) and `$?` (exit code).
  - Variables persist throughout the shell session.
  - View all variables using `export` without argument.

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
  - `re`
  - `atexit`

## Usage

1. **Run the Shell**:  
   Execute the script from the terminal:
   ```bash
   python main.py
   ```

2. **Environment Variable Examples**:

   - **Set a variable**:
     ```bash
     export NAME=World
     ```

   - **Use variables in commands**:
     ```bash
     echo "Hello $NAME"
     ```

   - **Check exit codes**:
     ```bash
     ls /nonexistent
     echo $?
     ```

3. **Command History Examples**:

   - **View all command history**:
     ```bash
     history
     ```

   - **View last 5 commands**:
     ```bash
     history 5
     ```

   - **Save history to a file**:
     ```bash
     history > my_history.txt
     ```

   - **Navigate history**: Press up/down arrow keys to cycle through previous commands