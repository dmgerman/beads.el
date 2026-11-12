# Development Guide

This document describes the development workflow for beads.el.

## Prerequisites

- Emacs 30.2+ (installed at `/opt/homebrew/bin/emacs`)
- Python 3 (for build scripts)
- mise (for task running)
- [vui.el](https://github.com/d12frosted/vui.el), cloned into `vendor/vui.el`
  (git-ignored) or anywhere else with `BEADS_VUI_DIR` pointing at it

## Environment

The lint, test, and build scripts take their environment only from these
variables, and print the versions they use at the start of every run:

| Variable | Default | Meaning |
|----------|---------|---------|
| `EMACS` | `emacs` on `PATH` | Emacs binary |
| `BEADS_VUI_DIR` | `vendor/vui.el` | Directory containing `vui.el` |
| `BEADS_EMACSEN` | (none) | Emacs binaries for `check-ci` |

The scripts fail if `vui.el` is missing; nothing else is added to the
`load-path`.

## Development Tasks

### Linting

Check syntax, parentheses, and byte-compile warnings:

```bash
mise run lint
```

This will:
- Check for balanced parentheses using `check-parens`
- Byte-compile files to catch warnings and errors
- Report any syntax issues

Byte-compilation warnings fail the lint.

### Testing

Run ERT (Emacs Lisp Regression Testing) tests:

```bash
mise run test
```

Test files should:
- Be placed in `test/` directory
- End with `-test.el` suffix
- Use `(require 'ert)` and define tests with `ert-deftest`

See `test/README.md` for more details on writing tests.

### Building

Byte-compile all `.el` files:

```bash
mise run build
```

This creates `.elc` files alongside the source files. Compiled files are ignored by git.

### Combined Check

Run both lint and test:

```bash
mise run check
```

### Checking Several Emacs Versions

`mise run check` uses a single Emacs.  Before pushing, run lint and tests on
every Emacs that matters: the `Package-Requires` floor, the latest release, and
a snapshot:

```bash
BEADS_EMACSEN="/path/to/emacs-28.1 /path/to/emacs-30.2 /path/to/emacs-snapshot" \
  mise run check-ci
```

Every entry runs even after a failure, and a summary lists each result.  Add
`--integration` (`python3 scripts/check_ci.py --integration`) to also run the
CLI integration tests, which need `bd`.

## File Structure

```
beads.el/
├── scripts/          # Python build/test scripts
│   ├── lint.py      # Syntax and style checker
│   ├── test.py      # ERT test runner
│   └── build.py     # Byte-compiler
├── test/            # ERT test files (*-test.el)
│   ├── README.md
│   └── example-test.el
├── mise.toml        # Task definitions
└── .gitignore       # Excludes *.elc, etc.
```

## Workflow

1. Write code in `.el` files
2. Write tests in `test/*-test.el`
3. Run `mise run check` to verify
4. Fix any issues reported
5. Commit when all checks pass

## ERT Testing Quick Reference

```elisp
(require 'ert)

(ert-deftest my-feature-test ()
  "Test description."
  (should (equal (my-function) expected-value))
  (should-not (null something))
  (should-error (broken-function) :type 'wrong-type-argument))
```

Run interactively in Emacs:
- `M-x ert RET t RET` - Run all tests
- `M-x ert RET my-feature-test RET` - Run specific test

## Common Issues

### Parenthesis Mismatch

If `mise run lint` reports unbalanced parens:
- Open the file in Emacs
- Run `M-x check-parens` to find the location
- Use `M-x show-paren-mode` for highlighting

### Byte-Compilation Warnings

Common warnings:
- `reference to free variable` - Missing `defvar` or `require`
- `function X not known to be defined` - Missing `require` or `declare-function`
- `obsolete function` - Update to modern API

### Test Failures

If tests fail:
- Run `M-x ert RET t RET` in Emacs for interactive debugging
- Use `edebug-defun` (C-u C-M-x) on test to step through
- Check test expectations match actual behavior

## Adding New Tests

1. Create `test/feature-test.el`
2. Add `(require 'ert)` at top
3. Write tests using `ert-deftest`
4. Run `mise run test` to verify
5. Tests automatically discovered by test runner

## Continuous Integration

The `mise run check` task is designed for CI:
- Exit code 0 on success
- Exit code 1 on failure
- Clear output indicating pass/fail

Example GitHub Actions workflow:

```yaml
- name: Check code
  run: |
    mise install
    mise run check
```
