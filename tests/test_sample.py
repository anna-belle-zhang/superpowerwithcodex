from src.sample import identity


def test_identity_returns_input_value() -> None:
    assert identity("hello") == "hello"
