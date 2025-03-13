import os

SHELL_BUILTINS = [
    "alias", "bg", "bind", "break", "cd", "command", "continue", "declare",
    "dirs", "echo", "enable", "eval", "exec", "exit", "export", "fg",
    "getopts", "hash", "help", "history", "jobs", "kill", "let", "local",
    "logout", "popd", "pushd", "pwd", "read", "readonly", "return", "set",
    "shift", "shopt", "source", "test", "times", "trap", "type", "ulimit",
    "umask", "unalias", "unset", "wait"
]

HELP_TEXT = {
    "cd": "cd [directory]\n\nChange the current directory to the specified directory.\nIf no directory is specified, change to the home directory.",
    
    "echo": "echo [arguments...]\n\nWrite arguments to standard output.\nDisplays the arguments separated by a single space and followed by a newline.",
    
    "exit": "exit [n]\n\nExit the shell with status n. If n is omitted, the exit status is that of the last command executed.",
    
    "export": "export [name[=value] ...]\n\nSet environment variables and mark them for export to child processes.\n\nWithout arguments, lists all exported variables in the format 'name=value'.",
    
    "help": "help [command]\n\nDisplay information about built-in commands.\n\nIf command is specified, gives detailed help on that command.\nOtherwise, lists available help topics.",
    
    "history": "history [n]\n\nDisplay the command history list with line numbers.\n\nAn argument of n lists only the last n lines.",
    
    "pwd": "pwd\n\nPrint the absolute pathname of the current working directory.",
    
    "type": "type [command]\n\nDisplay information about command type.\n\nIndicate how the command would be interpreted if used as a command name."
}

# Global state variables 
shell_variables = dict(os.environ)
last_exit_code = 0
history_file = os.path.expanduser("~/.python_shell_history")
history_size = 1024