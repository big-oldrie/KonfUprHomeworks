import subprocess
import os
import sys
import toml
from datetime import datetime

def get_git_log(repo_path, date_cutoff):
    """Extract commit hashes and their parents before a specified date."""
    os.chdir(repo_path)
    print(f"Changing directory to repository: {repo_path}")
    try:
        log_output = subprocess.check_output([
            'git', 'log', '--pretty=format:%H %P', f'--before={date_cutoff}'
        ], text=True)
        print("Git log command executed successfully.")
        return log_output.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e}")
        sys.exit(1)

def parse_git_log(log_lines):
    """Parse the git log output into a dictionary of dependencies."""
    dependencies = {}
    print("Parsing git log output.")
    for line in log_lines:
        parts = line.split()
        commit = parts[0]
        parents = parts[1:]
        dependencies[commit] = parents
        print(f"Parsed commit: {commit} with parents: {parents}")
    return dependencies

def generate_graphviz_code(dependencies):
    """Generate Graphviz DOT code from the dependencies dictionary."""
    lines = ["digraph G {"]
    print("Generating Graphviz code.")
    for commit, parents in dependencies.items():
        for parent in parents:
            lines.append(f'    "{parent}" -> "{commit}";')
            print(f"Added edge: {parent} -> {commit}")
    lines.append("}")
    return '\n'.join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python graph_visualizer.py <config.toml>")
        sys.exit(1)

    config_path = sys.argv[1]
    print(f"Loading configuration from: {config_path}")
    with open(config_path, 'r') as config_file:
        config = toml.load(config_file)

    repo_path = config.get("repository_path")
    output_path = config.get("output_path")
    date_cutoff = config.get("date_cutoff")

    if not repo_path or not os.path.exists(repo_path):
        print("Error: Repository path not specified or does not exist.")
        sys.exit(1)

    if not output_path:
        print("Error: Output path not specified.")
        sys.exit(1)

    if not date_cutoff:
        print("Error: Date cutoff not specified.")
        sys.exit(1)

    try:
        datetime.strptime(date_cutoff, "%Y-%m-%d")
        print(f"Date cutoff is valid: {date_cutoff}")
    except ValueError:
        print("Error: Date cutoff must be in YYYY-MM-DD format.")
        sys.exit(1)

    # Get git log and parse dependencies
    print("Fetching git log.")
    log_lines = get_git_log(repo_path, date_cutoff)
    print("Git log fetched successfully.")

    dependencies = parse_git_log(log_lines)
    print("Dependencies parsed successfully.")

    # Generate Graphviz code
    graphviz_code = generate_graphviz_code(dependencies)
    print("Graphviz code generated successfully.")

    # Output Graphviz code
    if output_path == "screen":
        print("\nGenerated Graphviz Code:")
        print(graphviz_code)
    else:
        with open(output_path, 'w') as output_file:
            output_file.write(graphviz_code)
        print(f"Dependency graph written to {output_path}")

if __name__ == "__main__":
    main()
