#!/usr/bin/env python3
"""
Lint Emacs Lisp files - check syntax, parentheses, and byte-compile.
Byte-compilation warnings fail the lint.
"""
import subprocess
import sys
from pathlib import Path

import elisp_env


def find_el_files(root_dir):
    """Find all .el files in the project, excluding hidden, dev, and vendor dirs."""
    root = Path(root_dir)
    return [
        f for f in root.rglob("*.el")
        if not any(part.startswith('.') for part in f.relative_to(root).parts)
        and 'dev' not in f.relative_to(root).parts
        and 'vendor' not in f.relative_to(root).parts
    ]


def check_parens(el_file):
    """Check for balanced parentheses using Emacs."""
    elisp_code = f"""
(condition-case err
    (progn
      (find-file "{el_file}")
      (check-parens)
      (message "OK: %s" "{el_file}")
      (kill-emacs 0))
  (error
    (message "ERROR in %s: %s" "{el_file}" (error-message-string err))
    (kill-emacs 1)))
"""

    result = subprocess.run(
        [elisp_env.emacs_program(), "-Q", "--batch", "--eval", elisp_code],
        capture_output=True,
        text=True
    )

    return result.returncode == 0, result.stderr + result.stdout


def byte_compile(el_file):
    """Byte-compile the file to catch warnings and errors."""
    result = subprocess.run(
        [elisp_env.emacs_program(), "-Q", "--batch"] + elisp_env.load_path_args() +
        ["--eval", "(setq load-prefer-newer t)", "-f", "batch-byte-compile", str(el_file)],
        capture_output=True,
        text=True
    )

    output = result.stderr + result.stdout
    has_warnings = "Warning:" in output
    has_errors = "Error:" in output or result.returncode != 0

    return not has_errors, has_warnings, output


def main():
    root_dir = Path(__file__).parent.parent
    el_files = find_el_files(root_dir)

    if not el_files:
        print("No .el files found")
        return 0

    elisp_env.print_environment()
    print(f"Linting {len(el_files)} Emacs Lisp file(s)...")
    print()

    all_passed = True
    total_warnings = 0

    for el_file in sorted(el_files):
        rel_path = el_file.relative_to(root_dir)
        print(f"Checking {rel_path}...")

        paren_ok, paren_output = check_parens(el_file)
        if not paren_ok:
            print(f"  ✗ Parenthesis check failed")
            print(f"    {paren_output}")
            all_passed = False
            continue

        compile_ok, has_warnings, compile_output = byte_compile(el_file)

        if not compile_ok:
            print(f"  ✗ Byte-compilation failed")
            print(f"    {compile_output}")
            all_passed = False
        elif has_warnings:
            print(f"  ✗ Warnings during byte-compilation")
            print(f"    {compile_output}")
            total_warnings += compile_output.count("Warning:")
            all_passed = False
        else:
            print(f"  ✓ Passed")

        print()

    if all_passed:
        print("✓ All checks passed")
        return 0
    else:
        if total_warnings > 0:
            print(f"✗ Some checks failed ({total_warnings} warning(s))")
        else:
            print("✗ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
