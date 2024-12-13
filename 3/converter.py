import argparse
import toml
import re
import sys
from typing import Any

class SyntaxError(Exception):
    pass

def parse_toml(input_text: str) -> dict:
    try:
        return toml.loads(input_text)
    except toml.TomlDecodeError as e:
        raise SyntaxError(f"TOML Syntax Error: {str(e)}")

def convert_to_custom_language(data: Any, depth: int = 0) -> str:
    result = []
    indent = "  " * depth

    if isinstance(data, dict):
        for key, value in data.items():
            if not re.match(r'^[A-Z]+$', key):
                raise SyntaxError(f"Invalid key name '{key}'. Must match [A-Z]+.")
            if isinstance(value, (dict, list)):
                result.append(f"{indent}{key} =")
                result.append(convert_to_custom_language(value, depth + 1))
            else:
                result.append(f"{indent}{key} = {convert_to_custom_language(value, depth).strip()}")
    elif isinstance(data, list):
        result.append(f"#( {' '.join(convert_to_custom_language(v, depth).strip() for v in data)} )")
    elif isinstance(data, str):
        result.append(f'"{data}"')
    elif isinstance(data, (int, float)):
        result.append(str(data))
    else:
        raise SyntaxError(f"Unsupported data type: {type(data)}")

    return '\n'.join(result)

def evaluate_expression(expr: str, constants: dict) -> Any:
    match = re.match(r'\{([+\-*/]|max) ([^\s]+) ([^\s]+)\}', expr)
    if not match:
        raise SyntaxError(f"Invalid expression: {expr}")

    op, left, right = match.groups()
    left_val = constants.get(left, None) if left in constants else float(left)
    right_val = constants.get(right, None) if right in constants else float(right)

    if op == '+':
        return left_val + right_val
    elif op == '-':
        return left_val - right_val
    elif op == '*':
        return left_val * right_val
    elif op == '/':
        return left_val / right_val
    elif op == 'max':
        return max(left_val, right_val)
    else:
        raise SyntaxError(f"Unsupported operation: {op}")

def process_constants(data: str) -> dict:
    constants = {}
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%'):
            continue
        if '=' in line:
            name, value = line.split('=', 1)
            name, value = name.strip(), value.strip()
            if not re.match(r'^[A-Z]+$', name):
                raise SyntaxError(f"Invalid constant name: {name}")
            constants[name] = float(value) if re.match(r'^\d+(\.\d+)?$', value) else value
        elif line.startswith('{') and line.endswith('}'):
            expr_result = evaluate_expression(line, constants)
            constants[line] = expr_result
    return constants

def main():
    parser = argparse.ArgumentParser(description="Convert TOML to Custom Language")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--print", action="store_true", help="Print the output to console instead of writing to a file")
    args = parser.parse_args()

    input_text = sys.stdin.read()
    try:
        parsed_data = parse_toml(input_text)
        converted_data = convert_to_custom_language(parsed_data)
        if args.print:
            print(converted_data)
        else:
            with open(args.output, 'w') as f:
                f.write(converted_data)
    except SyntaxError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
