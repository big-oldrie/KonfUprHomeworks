import os
import tarfile
import yaml
import time
import sys
import random

def list_directory(path):
    try:
        entries = os.listdir(path)
        for entry in entries:
            print(entry)
    except FileNotFoundError:
        print(f"ls: cannot access '{path}': No such file or directory")

def change_directory(path):
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"cd: no such file or directory: {path}")
    except NotADirectoryError:
        print(f"cd: not a directory: {path}")

def show_uptime(start_time):
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    current_time = time.strftime("%H:%M:%S", time.localtime())
    user_count = random.randint(1, 5)  # Simulated user count

    load_avg_1 = round(random.uniform(0, 2), 2)
    load_avg_5 = round(random.uniform(0, 2), 2)
    load_avg_15 = round(random.uniform(0, 2), 2)

    print(f" {current_time} up {int(hours)}:{int(minutes):02d}, {user_count} user{'s' if user_count > 1 else ''}, load average: {load_avg_1}, {load_avg_5}, {load_avg_15}")

def word_count(file_path):
    if os.path.isdir(file_path):
        print(f"wc: {file_path}: Is a directory")
        return
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            words = sum(len(line.split()) for line in lines)
            characters = sum(len(line) for line in lines)
            print(f"{len(lines)} {words} {characters} {file_path}")
    except FileNotFoundError:
        print(f"wc: {file_path}: No such file or directory")
    except PermissionError:
        print(f"wc: {file_path}: Permission denied")

def run_shell(vfs_path, start_script):
    # Extract virtual file system
    with tarfile.open(vfs_path, "r") as tar:
        tar.extractall("/tmp/vfs")

    os.chdir("/tmp/vfs")
    start_time = time.time()

    # Execute start script if provided and exists
    if start_script:
        if os.path.exists(start_script):
            with open(start_script, 'r') as script:
                commands = script.readlines()
                for command in commands:
                    execute_command(command.strip(), start_time)
        else:
            print(f"Warning: Start script '{start_script}' not found. Skipping.")

    # Interactive shell
    while True:
        try:
            current_dir = os.getcwd().replace("/tmp/vfs", "")
            command = input(f"shell:{current_dir}$ ").strip()
            if command:
                execute_command(command, start_time)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting shell.")
            break

def execute_command(command, start_time):
    args = command.split()
    if not args:
        return

    cmd = args[0]
    if cmd == "ls":
        path = args[1] if len(args) > 1 else '.'
        list_directory(path)
    elif cmd == "cd":
        path = args[1] if len(args) > 1 else '/'
        change_directory(path)
    elif cmd == "exit":
        sys.exit(0)
    elif cmd == "uptime":
        show_uptime(start_time)
    elif cmd == "wc":
        if len(args) > 1:
            for file in args[1:]:
                word_count(file)
        else:
            print("wc: missing file operand")
    else:
        print(f"{cmd}: command not found")

def main():
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <config.yaml>")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    vfs_path = config.get("vfs_path")
    start_script = config.get("start_script")

    if not vfs_path or not os.path.exists(vfs_path):
        print("Error: Virtual file system archive not found or not specified.")
        sys.exit(1)

    if start_script and not os.path.exists(start_script):
        print("Error: Start script file not found.")
        sys.exit(1)

    run_shell(vfs_path, start_script)

if __name__ == "__main__":
    main()