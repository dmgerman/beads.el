#!/usr/bin/env python3
"""
Shared Emacs environment for the build, lint, and test scripts.

Everything that affects a run is explicit and printed at the start:
- EMACS: Emacs binary (default: emacs on PATH)
- BEADS_VUI_DIR: directory containing vui.el (default: vendor/vui.el)
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LISP_DIR = ROOT_DIR / "lisp"


def emacs_program():
    """Return the Emacs binary to run."""
    return os.environ.get("EMACS", "emacs")


def vui_dir():
    """Return the vui.el directory, exiting with a message if it is missing."""
    directory = Path(os.environ.get("BEADS_VUI_DIR",
                                    ROOT_DIR / "vendor" / "vui.el")).expanduser()
    if not (directory / "vui.el").exists():
        sys.exit(f"vui.el not found in {directory}\n"
                 "Clone https://github.com/d12frosted/vui.el into vendor/vui.el "
                 "or set BEADS_VUI_DIR.")
    return directory


def load_path_args():
    """Return -L arguments for the package and its dependencies."""
    return ["-L", str(LISP_DIR), "-L", str(vui_dir())]


def emacs_version():
    """Return the version string of the selected Emacs."""
    result = subprocess.run(
        [emacs_program(), "-Q", "--batch", "--eval", "(princ emacs-version)"],
        capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Cannot run Emacs {emacs_program()}: {result.stderr.strip()}")
    return result.stdout.strip()


def header_version(el_file):
    """Return the Version: header of EL_FILE, or 'unknown'."""
    match = re.search(r"^;; (?:Package-)?Version: *(\S+)",
                      Path(el_file).read_text(), re.MULTILINE)
    return match.group(1) if match else "unknown"


def bd_version():
    """Return the version line of the bd CLI, or 'not found'."""
    if not shutil.which("bd"):
        return "not found"
    result = subprocess.run(["bd", "--version"], capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()


def print_environment(include_bd=False):
    """Print the versions this run uses, so drift is visible."""
    emacs = shutil.which(emacs_program()) or emacs_program()
    print(f"Emacs: {emacs_version()} ({emacs})")
    print(f"vui:   {header_version(vui_dir() / 'vui.el')} ({vui_dir()})")
    if include_bd:
        print(f"bd:    {bd_version()}")
    print()
