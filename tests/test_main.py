import pytest

from pullsar.main import main


@pytest.mark.skip(reason="Testing of the workflow is a future task.")
def test_main() -> None:
    # Test the main function
    assert main() is None
