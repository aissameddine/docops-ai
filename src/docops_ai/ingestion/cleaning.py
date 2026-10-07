import re
import unicodedata

# Zero-width space/joiners, BOM, soft hyphen: invisible and useless for retrieval
_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00ad"))

# Typographic ligatures that PDFs store as single characters: "fi" is searched as "fi"
_LIGATURES = {
    0xFB00: "ff",
    0xFB01: "fi",
    0xFB02: "fl",
    0xFB03: "ffi",
    0xFB04: "ffl",
    0xFB05: "st",
    0xFB06: "st",
}
_TRANSLATION = {**_INVISIBLE, **_LIGATURES}

# A word cut by a hyphen at the end of a line: "structu-\nrelles" -> "structurelles".
# Only joined when both sides are lowercase letters, so "Jean-\nPaul" is left alone.
_LOWER = "a-z\u00e0-\u00f6\u00f8-\u00ff\u0153"
_LINE_HYPHEN = re.compile(rf"(?<=[{_LOWER}])-\n(?=[{_LOWER}])")


def clean_text(text: str) -> str:
    """Normalize extracted text without changing its meaning."""
    text = unicodedata.normalize("NFC", text).translate(_TRANSLATION)
    text = text.replace("\u00a0", " ")  # non-breaking space -> normal space
    text = re.sub(r"[ \t]+\n", "\n", text)  # trailing spaces
    text = _LINE_HYPHEN.sub("", text)  # re-join words split across lines
    text = re.sub(r"\n{3,}", "\n\n", text)  # runs of blank lines
    return text.strip()
