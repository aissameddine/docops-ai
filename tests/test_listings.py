from docops_ai.ingestion.listings import strip_listing_numbers

LISTING = "\n".join(
    [
        "Piege a eviter : ne jamais modifier le buffer.",
        "1",
        "void exchange(int steps)",
        "2 {",
        "3",
        'printf("Initial value of process rank %d is %d\\n", my_rank ,',
        "my_value);",
        "4",
        "5",
        "for (int step = 0; step < steps; ++ step) {",
        "6",
        "MPI_Request reqs [2];",
        "7",
        "int num_reqs = 0;",
        "8",
    ]
)


def test_listing_numbers_are_removed():
    out = strip_listing_numbers(LISTING).split("\n")
    assert out[0] == "Piege a eviter : ne jamais modifier le buffer."
    assert "void exchange(int steps)" in out
    assert "{" in out  # "2 {" keeps its code
    assert not any(line.isdigit() for line in out)


def test_code_is_not_altered():
    out = strip_listing_numbers(LISTING)
    assert 'printf("Initial value of process rank %d is %d\\n", my_rank ,' in out
    assert "for (int step = 0; step < steps; ++ step) {" in out


def test_section_numbers_are_kept():
    text = "1\nIntroduction\nTexte du rapport.\n2\nMethode\nAutre texte.\n3\nResultats"
    assert strip_listing_numbers(text) == text


def test_lone_numeric_column_is_kept():
    text = "rang\n0\n1\n2\n3\n4\n5"
    assert strip_listing_numbers(text) == text


def test_numbered_prose_list_is_kept():
    text = "1. premier point\n2. deuxieme point\n3. troisieme point\n4. quatrieme point"
    assert strip_listing_numbers(text) == text


def test_short_run_is_kept():
    text = "1\nint x;\n2\nint y;\n3\nint z;"
    assert strip_listing_numbers(text) == text


def test_text_without_numbers_is_unchanged():
    assert strip_listing_numbers("Bonjour\nle monde") == "Bonjour\nle monde"
