from docops_ai.ingestion.cleaning import clean_text


def test_removes_zero_width_space():
    assert clean_text("pr\u00e9visionnelle\u200b") == "pr\u00e9visionnelle"


def test_keeps_accents_and_apostrophes():
    assert clean_text("l\u2019a\u00e9ronautique") == "l\u2019a\u00e9ronautique"


def test_collapses_blank_lines_and_trailing_spaces():
    assert clean_text("a  \n\n\n\nb") == "a\n\nb"


def test_nbsp_becomes_space():
    assert clean_text("a\u00a0b") == "a b"
