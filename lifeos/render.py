"""Terminal output. Colour when a TTY supports it, plain text otherwise."""

from __future__ import annotations

import os
import sys

_ENABLED = (
    sys.stdout.isatty()
    and os.environ.get("TERM") not in (None, "dumb")
    and "NO_COLOR" not in os.environ
)

_CODES = {
    "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
    "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m",
    "grey": "\033[90m", "bold": "\033[1m", "reset": "\033[0m",
}


def c(text: str, *styles: str) -> str:
    if not _ENABLED or not styles:
        return text
    return "".join(_CODES.get(s, "") for s in styles) + text + _CODES["reset"]


def heading(text: str) -> str:
    return "\n" + c(text.upper(), "bold", "cyan") + "\n" + c("─" * len(text), "grey")


def urgency(days: int | None) -> str:
    """Colour style for a countdown, by how much time is left."""
    if days is None:
        return "grey"
    if days < 0:
        return "grey"
    if days <= 2:
        return "red"
    if days <= 7:
        return "yellow"
    return "green"


def countdown(days: int | None) -> str:
    if days is None:
        return c("no date", "grey")
    if days < 0:
        return c(f"{abs(days)}d ago", "grey")
    if days == 0:
        return c("TODAY", "red", "bold")
    if days == 1:
        return c("TOMORROW", "red", "bold")
    return c(f"{days}d", urgency(days))


def table(rows: list[list[str]], headers: list[str] | None = None) -> str:
    """Left-aligned table that measures width ignoring ANSI escapes."""
    if not rows:
        return c("  (nothing)", "grey")

    def width(s: str) -> int:
        out, in_esc = 0, False
        for ch in s:
            if ch == "\033":
                in_esc = True
            elif in_esc:
                if ch == "m":
                    in_esc = False
            else:
                out += 1
        return out

    body = ([headers] if headers else []) + rows
    cols = max(len(r) for r in body)
    widths = [max(width(r[i]) if i < len(r) else 0 for r in body) for i in range(cols)]

    lines = []
    if headers:
        lines.append("  " + "  ".join(
            c(headers[i], "grey") + " " * (widths[i] - width(headers[i]))
            for i in range(len(headers))
        ).rstrip())
    for r in rows:
        lines.append("  " + "  ".join(
            r[i] + " " * (widths[i] - width(r[i])) for i in range(len(r))
        ).rstrip())
    return "\n".join(lines)
