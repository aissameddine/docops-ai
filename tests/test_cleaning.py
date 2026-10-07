from docops_ai.ingestion.cleaning import clean_text


def test_removes_zero_width_space():
    assert clean_text("pr\u00e9visionnelle\u200b") == "pr\u00e9visionnelle"


def test_keeps_accents_and_apostrophes():
    assert clean_text("l\u2019a\u00e9ronautique") == "l\u2019a\u00e9ronautique"


def test_collapses_blank_lines_and_trailing_spaces():
    assert clean_text("a  \n\n\n\nb") == "a\n\nb"


def test_nbsp_becomes_space():
    assert clean_text("a\u00a0b") == "a b"


def test_ligatures_are_expanded():
    assert clean_text("\ufb01ltrage et \ufb02ux") == "filtrage et flux"
    assert clean_text("o\ufb03ce") == "office"


def test_hyphenated_line_break_is_rejoined():
    assert clean_text("donn\u00e9es structu-\nrelles") == "donn\u00e9es structurelles"
    assert clean_text("collabo- \nratif") == "collaboratif"


def test_hyphen_before_capital_or_digit_is_kept():
    assert clean_text("Jean-\nPaul") == "Jean-\nPaul"
    assert clean_text("pages 3-\n4") == "pages 3-\n4"


def test_normal_hyphens_are_untouched():
    assert clean_text("socio-\u00e9conomique, c'est-\u00e0-dire") == (
        "socio-\u00e9conomique, c'est-\u00e0-dire"
    )
