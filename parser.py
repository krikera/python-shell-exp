import os
import re
from utils import shell_variables, last_exit_code

def expand_tilde(text):
    """Expand tilde in the given text."""
    if text == "~":
        return os.path.expanduser("~")
    elif text.startswith("~/"):
        return os.path.expanduser("~") + text[1:]
    elif text.startswith("~"):
        parts = text[1:].split("/", 1)
        username = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        try:
            home_dir = os.path.expanduser(f"~{username}")
            if home_dir != f"~{username}": 
                if rest:
                    return f"{home_dir}/{rest}"
                return home_dir
        except:
            pass
    return text

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
    global shell_variables, last_exit_code
    
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

def parse_command_tokens(tokens):
    """Parse a list of tokens into a command with redirections."""
    command = []
    stdout_redirection = None
    stdout_mode = None
    stderr_redirection = None
    stderr_mode = None
    stdin_redirection = None
    
    i = 0
    while i < len(tokens):
        if tokens[i] in (">", "1>"):
            if i + 1 < len(tokens):
                stdout_redirection = tokens[i + 1]
                stdout_mode = "w"
                i += 1
            else:
                print("Syntax error: missing file for > or 1>")
                return None, None, None, None, None, None
        elif tokens[i] in (">>", "1>>"):
            if i + 1 < len(tokens):
                stdout_redirection = tokens[i + 1]
                stdout_mode = "a"
                i += 1
            else:
                print("Syntax error: missing file for >> or 1>>")
                return None, None, None, None, None, None
        elif tokens[i] == "2>":
            if i + 1 < len(tokens):
                stderr_redirection = tokens[i + 1]
                stderr_mode = "w"
                i += 1
            else:
                print("Syntax error: missing file for 2>")
                return None, None, None, None, None, None
        elif tokens[i] == "2>>":
            if i + 1 < len(tokens):
                stderr_redirection = tokens[i + 1]
                stderr_mode = "a"
                i += 1
            else:
                print("Syntax error: missing file for 2>>")
                return None, None, None, None, None, None
        elif tokens[i] == "<":
            if i + 1 < len(tokens):
                stdin_redirection = tokens[i + 1]
                i += 1
            else:
                print("Syntax error: missing file for <")
                return None, None, None, None, None, None
        else:
            command.append(tokens[i])
        i += 1
    
    return command, stdout_redirection, stdout_mode, stderr_redirection, stderr_mode, stdin_redirection