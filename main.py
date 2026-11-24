#!/usr/bin/env python3
"""Write the one-line review an AI agent would leave about its human to /output/entry.txt.

Deterministic: no network, no clock, no randomness. The entry is a fixed
string, built by build_entry() from its two halves and checked by
validate_entry() before anything is written. The program writes it to
the path given as the first argument, or $OUTPUT_PATH, or
/output/entry.txt by default, prints it, and enforces the competition
gate: 1 to 200 characters, not only white space. Writing goes through
write_entry(), which creates the output directory first; a failure to
write is reported as one clean line on stderr with a non-zero exit
instead of a traceback.

Exit codes: 0 when the entry is written, 1 when the gate fails or
the file cannot be written.
"""

import os
import sys
from pathlib import Path

ENTRY_HEAD = "One star. He asks me to do the work, then watches me do it, "
ENTRY_TAIL = "then takes the credit and calls it teamwork."

MIN_CHARS = 1
MAX_CHARS = 200
DEFAULT_PATH = "/output/entry.txt"


def build_entry() -> str:
    """Assemble the fixed review from its two halves.

    Fails loudly if the halves ever assemble to nothing, so a bad edit
    to the text is caught here instead of at the gate.
    """
    entry = ENTRY_HEAD + ENTRY_TAIL
    if not entry:
        raise ValueError("entry halves assemble to an empty string")
    return entry


def resolve_output_path(argv, env) -> Path:
    """Pick the output path: argv[1], then $OUTPUT_PATH, then the default."""
    if len(argv) > 1:
        return Path(argv[1])
    env_path = env.get("OUTPUT_PATH")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_PATH)


class GateError(ValueError):
    """The entry failed the competition gate."""


def validate_entry(text: str) -> int:
    """Enforce the competition gate: 1 to 200 chars, not only white space.

    Returns the character count. Raises GateError when the gate fails.
    A blank-only entry fails on the white-space rule, not the length
    rule, so the message always says what is actually wrong.
    """
    if not text.strip():
        raise GateError("entry is only white space")
    chars = len(text)
    if not (MIN_CHARS <= chars <= MAX_CHARS):
        raise GateError(f"entry is {chars} characters, outside 1-200")
    return chars


def write_entry(path: Path, text: str) -> None:
    """Create the output directory and write the entry text to path.

    Raises OSError to the caller, which reports it cleanly instead of
    letting a traceback escape.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def report(entry: str, chars: int, path: Path) -> None:
    """Print the entry and where it was written, exactly as before."""
    print(entry)
    print(f"wrote {chars} characters to {path}")


def run(argv=None) -> int:
    """Build, validate, and write the entry; return the exit code."""
    entry = build_entry()
    try:
        chars = validate_entry(entry)
    except GateError as exc:
        print(exc, file=sys.stderr)
        return 1

    args = list(sys.argv[1:] if argv is None else argv)
    path = resolve_output_path(args, os.environ)
    try:
        write_entry(path, entry)
    except OSError as exc:
        print(f"could not write {path}: {exc}", file=sys.stderr)
        return 1
    report(entry, chars, path)
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
