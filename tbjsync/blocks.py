"""Managed blocks: the only parts of a README the sync bot is allowed to rewrite.

A managed block looks like:

    <!-- tbj:footer:start · managed by tbj-brand — edits inside are overwritten -->
    ...content...
    <!-- tbj:footer:end -->

Everything outside these markers belongs to the repo and is never touched.
The first sync migrates the legacy hand-written header/footer/licence text
(from the Sept 2026 bulk pass) into blocks, so later syncs are a clean swap.
"""
from __future__ import annotations

import re

NOTE = "managed by tbj-brand — edits inside are overwritten"


def start(name: str) -> str:
    return f"<!-- tbj:{name}:start · {NOTE} -->"


def end(name: str) -> str:
    return f"<!-- tbj:{name}:end -->"


def _pattern(name: str) -> re.Pattern:
    return re.compile(
        rf"<!--\s*tbj:{re.escape(name)}:start[^>]*-->.*?<!--\s*tbj:{re.escape(name)}:end\s*-->",
        re.S,
    )


def wrap(name: str, body: str) -> str:
    return f"{start(name)}\n{body.strip(chr(10))}\n{end(name)}"


def has(text: str, name: str) -> bool:
    return bool(_pattern(name).search(text))


def get(text: str, name: str) -> str | None:
    m = _pattern(name).search(text)
    if not m:
        return None
    inner = m.group(0)
    inner = inner[inner.index("-->") + 3:]
    inner = inner[: inner.rindex("<!--")]
    return inner.strip("\n")


def replace(text: str, name: str, body: str) -> str:
    return _pattern(name).sub(lambda _: wrap(name, body), text, count=1)


def remove(text: str, name: str) -> str:
    return _pattern(name).sub("", text, count=1)


# ── Legacy migration helpers ────────────────────────────────────────────────
# Footer variants seen across the repos:
#   ---\n\n<div align="center">\n<sub>Built by <a ...>@TheBooleanJulian</a></sub>\n</div>
#   Built by [@TheBooleanJulian](https://github.com/TheBooleanJulian)
_LEGACY_FOOTER = re.compile(
    r"""
    (?:\n[ \t]*(?:---|\*\*\*|___)[ \t]*\n\s*)?        # optional rule before it
    (?:<div[^>]*>\s*)?                               # optional centring div
    (?:<p[^>]*>\s*)?
    (?:<sub>)?\s*
    (?:Built|Made|Crafted)\s+(?:with\s+\S+\s+)?by\s+
    (?:\[@?TheBooleanJulian\]\([^)]*\)|<a[^>]*>@?TheBooleanJulian</a>|@?TheBooleanJulian)
    [^\n]*?
    (?:</sub>)?\s*
    (?:</p>\s*)?
    (?:</div>)?
    \s*\Z
    """,
    re.X | re.I,
)


def strip_legacy_footer(text: str) -> tuple[str, bool]:
    m = _LEGACY_FOOTER.search(text)
    if not m:
        return text, False
    return text[: m.start()].rstrip() + "\n", True


_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)


def find_section(text: str, title_regex: str, level: int = 2) -> tuple[int, int] | None:
    """Span of a section (heading line through to the next heading of the same or
    higher level, a managed block, or EOF)."""
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in _HEADING.finditer(text)]
    # Ignore headings inside fenced code blocks.
    fences = [m.span() for m in re.finditer(r"^```.*?^```", text, re.M | re.S)]
    heads = [h for h in heads if not any(a <= h[0] < b for a, b in fences)]
    for i, (pos, lvl, title) in enumerate(heads):
        if lvl == level and re.fullmatch(title_regex, normalise_heading(title), re.I):
            stop = len(text)
            for pos2, lvl2, _ in heads[i + 1:]:
                if lvl2 <= level:
                    stop = pos2
                    break
            m = re.search(r"<!--\s*tbj:\w+:start", text[pos:stop])
            if m:
                stop = pos + m.start()
            # Don't swallow a trailing horizontal rule that belongs to the footer.
            chunk = text[pos:stop]
            rule = re.search(r"\n[ \t]*---[ \t]*\n\s*\Z", chunk)
            if rule:
                stop = pos + rule.start() + 1
            return pos, stop
    return None


def headings(text: str, level: int = 2) -> list[str]:
    fences = [m.span() for m in re.finditer(r"^```.*?^```", text, re.M | re.S)]
    out = []
    for m in _HEADING.finditer(text):
        if len(m.group(1)) == level and not any(a <= m.start() < b for a, b in fences):
            out.append(m.group(2).strip())
    return out


def normalise_heading(h: str) -> str:
    h = re.sub(r"[^\w\s&/]", " ", h)   # drop emoji and punctuation
    h = h.replace("&", " and ").replace("/", " and ")
    h = re.sub(r"^\s*\d+(\s|$)", "", h)  # "10 · License" → "License"
    return re.sub(r"\s+", " ", h).strip().lower()


_SHIELD = re.compile(r"!\[[^\]]*\]\(https://img\.shields\.io/[^)]*\)")


def header_insert_point(text: str) -> int:
    """Where the brand badge row goes: after the last shields.io badge in the
    header area, else after the H1's tagline paragraph, else at the top."""
    cut = len(text)
    for pat in (r"^\s*---\s*$", r"^##\s"):
        m = re.search(pat, text, re.M)
        if m:
            cut = min(cut, m.start())
    header = text[:cut]
    last = None
    for m in _SHIELD.finditer(header):
        last = m
    if last:
        eol = text.find("\n", last.end())
        return len(text) if eol == -1 else eol + 1
    h1 = re.search(r"^#[ \t]+[^\n]*$|(?s:<h1[^>]*>.*?</h1>)", header, re.M)
    if h1:
        rest = text[h1.end():]
        # skip blank lines then one paragraph (tagline)
        m = re.match(r"\n*(?:(?!#|<|---)[^\n]+\n)+", rest)
        return h1.end() + (m.end() if m else 0) + (0 if m else 1)
    return 0


def remove_license_badges(text: str, outside_block: str = "badges") -> str:
    """Drop hand-written license badges so the managed row is the only one."""
    managed = get(text, outside_block)
    lic = re.compile(r"^[ \t]*!\[[Ll]icen[cs]e\]\(https://img\.shields\.io/badge/licen[cs]e[^)]*\)[ \t]*\n", re.M)
    if managed is None:
        return lic.sub("", text)
    s = _pattern(outside_block).search(text)
    return lic.sub("", text[: s.start()]) + text[s.start(): s.end()] + lic.sub("", text[s.end():])
