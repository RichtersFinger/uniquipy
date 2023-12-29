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


def test_find_duplicates(WORKING_DIR):
    """
    Test functionality of function `find_duplicates` with and without
    duplicates.
    """

    this_working_dir = WORKING_DIR / "test_find_duplicates"
    this_working_dir.mkdir(parents=True, exist_ok=False)

    # write test-files
    (this_working_dir / "test.txt").write_bytes(b"test1")
    (this_working_dir / "test_.txt").write_bytes(b"test1")
    (this_working_dir / "test2.txt").write_bytes(b"test2")
    (this_working_dir / "test3.txt").write_bytes(b"test2"*16384 + b"a")
    (this_working_dir / "test4.txt").write_bytes(b"test2"*16384 + b"b")

    # eval
    is_unique, uniques = src.find_duplicates(
        [
            this_working_dir / "test.txt",
            this_working_dir / "test2.txt",
            this_working_dir / "test3.txt",
            this_working_dir / "test4.txt"
        ],
        "md5"
    )

    # check
    assert is_unique
    assert len(uniques) == 4
    for unique in uniques.values():
        assert len(unique) == 1
        assert unique[0] in [
            this_working_dir / "test.txt",
            this_working_dir / "test2.txt",
            this_working_dir / "test3.txt",
            this_working_dir / "test4.txt"
        ]
    for file in [
        this_working_dir / "test.txt",
        this_working_dir / "test2.txt",
        this_working_dir / "test3.txt",
        this_working_dir / "test4.txt"
    ]:
        assert file in [p[0] for p in uniques.values()]

    # eval with duplicate
    is_unique, _ = src.find_duplicates(
        [
            this_working_dir / "test.txt",
            this_working_dir / "test_.txt",
            this_working_dir / "test2.txt",
            this_working_dir / "test3.txt",
            this_working_dir / "test4.txt"
        ],
        "md5"
    )

    # check
    assert not is_unique
