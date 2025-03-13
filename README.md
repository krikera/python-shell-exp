# Python Shell Emulator

This project is a lightweight command-line shell emulator written in Python. It implements basic command execution, tab completion, redirection features, command history, and pipeline functionality similar to those found in traditional Unix shells.

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
  - `help`: Displays information about built-in commands.

- **Command Redirection**:  
  Basic support for redirecting input, output, and errors:
  - `>` or `1>`: Redirect standard output to a file (write mode).
  - `>>` or `1>>`: Redirect standard output to a file (append mode).
  - `2>`: Redirect standard error to a file (write mode).
  - `2>>`: Redirect standard error to a file (append mode).
  - `<`: Redirect standard input from a file.

- **Pipes**:  
  Connect multiple commands together with the pipe operator (`|`):
  - Redirect the output of one command as input to another
  - Chain multiple commands together in a pipeline
  - Combine pipes with redirections for complex command sequences
  - Both built-in and external commands support piping

- **Environment Variables**:  
  Full support for environment variable management:
  - Set variables using `export VAR=value`.
  - Use variables in commands with `$VAR` or `${VAR}` syntax.
  - Access special variables like `$$` (process ID) and `$?` (exit code).
  - Variables persist throughout the shell session.
  - View all variables using `export` without argument.

- **Tilde Expansion**:  
  Support for using `~` as a shortcut:
  - Standalone `~` expands to the user's home directory
  - Paths starting with `~/` expand to paths relative to home
  - `~username/` expands to another user's home directory
  - Works in all contexts where paths are expected

- **Help System**:  
  Documentation for built-in commands:
  - `help` lists all available built-in commands
  - `help command` provides detailed help on a specific command
  - Includes syntax, description, and usage information
  - Supports redirection and can be used in pipes

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

4. **Pipe Examples**:

   - **Basic pipe to filter output**:
     ```bash
     ls | grep .py
     ```

   - **Chain multiple commands**:
     ```bash
     ls -la | grep "^d" | sort
     ```

   - **Combine pipes with redirections**:
     ```bash
     ls | grep .txt > text_files.txt
     ```

   - **Use built-in commands in pipes**:
     ```bash
     echo "Hello World" | grep "Hello"
     ```

   - **Count items with pipes**:
     ```bash
     ls | wc -l
     ```

5. **Tilde Expansion Examples**:

   - **Navigate to home directory**:
     ```bash
     cd ~
     ```

   - **List files in home subdirectory**:
     ```bash
     ls ~/Documents
     ```

   - **Create file in home directory**:
     ```bash
     echo "test" > ~/testfile.txt
     ```

6. **Help Examples**:

   - **View available commands**:
     ```bash
     help
     ```

   - **Get help on specific command**:
     ```bash
     help cd
     help export
     ```

   - **Save command help to file**:
     ```bash
     help echo > echo_help.txt
     ```

   - **Search through command help**:
     ```bash
     help | grep directory
     ```