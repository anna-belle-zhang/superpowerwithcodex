from src.string_utils import truncate, slugify, count_words


def test_truncate_shortens_long_text():
    assert truncate("hello world", 5) == "hello"


def test_truncate_returns_text_unchanged_when_within_limit():
    assert truncate("hi", 10) == "hi"


def test_truncate_at_exact_limit():
    assert truncate("hello", 5) == "hello"


def test_slugify_lowercases_and_replaces_spaces():
    assert slugify("Hello World") == "hello-world"


def test_slugify_removes_special_characters():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_handles_multiple_spaces():
    assert slugify("hello   world") == "hello-world"


def test_count_words_counts_space_separated_words():
    assert count_words("hello world") == 2


def test_count_words_single_word():
    assert count_words("hello") == 1


def test_count_words_empty_string():
    assert count_words("") == 0
