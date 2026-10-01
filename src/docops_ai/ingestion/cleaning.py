import re
import unicodedata

# Zero-width space/joiners, BOM, soft hyphen: invisible and useless for retrieval
_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00ad"))


def clean_text(text: str) -> str:
    """Normalize extracted text without changing its meaning."""
    text = unicodedata.normalize("NFC", text).translate(_INVISIBLE)
    text = text.replace("\u00a0", " ")  # non-breaking space -> normal space
    text = re.sub(r"[ \t]+\n", "\n", text)  # trailing spaces
    text = re.sub(r"\n{3,}", "\n\n", text)  # runs of blank lines
    return text.strip()
