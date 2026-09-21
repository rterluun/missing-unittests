from pytest import raises


def sample_function():
    return "This is a sample function."


def test_function():
    with raises(AssertionError):
        assert sample_function() == "This is not the expected output."
