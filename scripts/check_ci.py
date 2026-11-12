#!/usr/bin/env python3
"""
Run lint and tests on every Emacs listed in BEADS_EMACSEN.

BEADS_EMACSEN is a whitespace-separated list of Emacs binaries, which should
cover the Package-Requires floor, the latest release, and a snapshot.  Every
entry is run; the exit code is non-zero if any of them fails.
"""
import argparse
import os
import subprocess
import sys

import elisp_env


def run(script, emacs, extra_args=()):
    """Run SCRIPT with EMACS, returning True on success."""
    env = dict(os.environ, EMACS=emacs)
    result = subprocess.run(
        [sys.executable, str(elisp_env.ROOT_DIR / "scripts" / script), *extra_args],
        env=env)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integration", action="store_true",
                        help="Also run the CLI integration tests (needs bd)")
    args = parser.parse_args()

    emacsen = os.environ.get("BEADS_EMACSEN", "").split()
    if not emacsen:
        sys.exit("BEADS_EMACSEN is not set: list the Emacs binaries to check, e.g.\n"
                 "  BEADS_EMACSEN='/path/to/emacs-28.1 /path/to/emacs-30.2' "
                 "mise run check-ci")

    steps = [("lint", "lint.py", ()), ("test", "test.py", ())]
    if args.integration:
        steps.append(("integration", "test.py", ("--integration",)))

    results = [(emacs, name, run(script, emacs, extra))
               for emacs in emacsen
               for name, script, extra in steps]

    print()
    print("Summary:")
    for emacs, name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name:<12} {emacs}")

    return 0 if all(ok for _, _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
