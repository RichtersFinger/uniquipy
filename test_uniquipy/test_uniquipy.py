"""
Test suite for uniquipy.

Tested with pytest==7.4.3.

Run with
pytest -v -s --cov=uniquipy.src
"""

from pathlib import Path
from shutil import rmtree
import hashlib
import pytest
from uniquipy import src

@pytest.fixture(scope="session")
def WORKING_DIR():
    return Path("test_uniquipy/tmp/")

@pytest.fixture(scope="session", autouse=True)
def update_test_case_status(request, WORKING_DIR):
    if WORKING_DIR.is_dir():
        rmtree(WORKING_DIR)
    WORKING_DIR.mkdir(parents=True, exist_ok=False)

    request.addfinalizer(lambda: rmtree(WORKING_DIR))

def test_HASHING_ALGORITHMS():
    """Make sure the default of "md5" is listed in HASHING_ALGORITHMS."""

    assert "md5" in src.HASHING_ALGORITHMS

def test_hash_from_file(WORKING_DIR):
    """
    Test basic functionality of function `hash_from_file`.
    """

    method = "md5"
    data = b"test"
    expected_hash = hashlib.md5(data).hexdigest()

    # write test-file
    test_file = WORKING_DIR / "test.txt"
    test_file.write_bytes(data)

    # execute hash_from_file
    hashed = src.hash_from_file(method, str(test_file))

    assert hashed == expected_hash

def test_hash_from_file_short(WORKING_DIR):
    """
    Test functionality of function `hash_from_file` with `short=True`.
    """

    method = "md5"
    data = b"test"
    unexpected_hash = hashlib.md5(data).hexdigest()
    expected_hash = hashlib.md5(data.decode("utf-8")[0].encode("utf-8")).hexdigest()

    # write test-file
    test_file = WORKING_DIR / "test.txt"
    test_file.write_bytes(data)

    # execute hash_from_file
    hashed = src.hash_from_file(
        method, str(test_file), chunk_size=1, short=True
    )

    assert hashed != unexpected_hash
    assert hashed == expected_hash
