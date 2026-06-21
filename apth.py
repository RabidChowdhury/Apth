import argparse
import shutil
import winreg
from pathlib import Path
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Apth")

try:
    from colorama import init
    init()
except ImportError:
    pass


VERSION = "Alpha, not productional."

YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def find_in_app_paths(name):
    locations = [
        winreg.HKEY_CURRENT_USER,
        winreg.HKEY_LOCAL_MACHINE
    ]

    for root in locations:
        try:
            key = winreg.OpenKey(
                root,
                rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{name}.exe"
            )

            value, _ = winreg.QueryValueEx(key, "")
            return value

        except OSError:
            pass

    return None


def resolve_real_executable(path):
    p = Path(path)

    if p.suffix.lower() not in (".cmd", ".bat"):
        return None

    search_dirs = [
        p.parent,
        p.parent.parent,
    ]

    for directory in search_dirs:
        same_name_exe = directory / f"{p.stem}.exe"
        if same_name_exe.exists():
            return str(same_name_exe)

        for app_dir in directory.glob("app-*"):
            nested_exe = app_dir / f"{p.stem}.exe"
            if nested_exe.exists():
                return str(nested_exe)

    return None


def format_path_extension(path_str):
    p = Path(path_str)
    if p.suffix.lower() in (".exe", ".cmd", ".bat"):
        return str(p.with_suffix(p.suffix.lower()))
    return path_str


def find_application_paths(name):
    paths = []
    
    app_path = find_in_app_paths(name)
    if app_path:
        paths.append(format_path_extension(app_path))
        return paths

    system_path = shutil.which(name)
    if system_path:
        real_path = resolve_real_executable(system_path)
        if real_path and real_path.lower() != system_path.lower():
            paths.append(format_path_extension(real_path))
        
        paths.append(format_path_extension(system_path))

    return paths


def main():
    parser = argparse.ArgumentParser(
        add_help=False
    )

    parser.add_argument("name", nargs="?")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"\n{YELLOW}Current version: {VERSION}{RESET}\n")
        return

    if args.help:
        print("""
Apth is a simple script that allows you to find the directory of a program.

Usage:
  apth <name>
  apth --help
  apth --version
""")
        return

    name = args.name

    if not name:
        name = input("\nApplication: ").strip()

    if not name:
        print(
            f"\n{RED}No application name provided. Operation canceled.{RESET}\n"
        )
        return

    paths = find_application_paths(name)

    if paths:
        print(
            f"\n{YELLOW}{name} is located in this directory:{RESET}\n"
        )
        for path in paths:
            print(path)
        print()
    else:
        print(
            "\nThe system couldn't find the directory of "
            f"{YELLOW}{name}{RESET}. "
            "Please check if the application is installed properly.\n"
        )


if __name__ == "__main__":
    main()
