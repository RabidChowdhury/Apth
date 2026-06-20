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


VERSION = "1.0.0 (Beta Version)"

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
        return str(p)

    candidates = []

    parent = p.parent

    candidates.extend([
        parent.parent / "Code.exe",
        parent.parent / "Cursor.exe",
        parent.parent / "GitHubDesktop.exe",
        parent.parent / f"{p.stem}.exe",
        parent / f"{p.stem}.exe"
    ])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return str(p)


def find_application(name):
    app_path = find_in_app_paths(name)

    if app_path:
        return app_path

    path = shutil.which(name)

    if path:
        return resolve_real_executable(path)

    return None


def main():
    parser = argparse.ArgumentParser(
        add_help=False
    )

    parser.add_argument("name", nargs="?")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"\n{YELLOW}Apth Version {VERSION}{RESET}\n")
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

    path = find_application(name)

    if path:
        print(
            f"\n{YELLOW}{name} is located in this directory:{RESET}\n"
        )
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