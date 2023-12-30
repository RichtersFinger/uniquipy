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
from click.testing import CliRunner
from uniquipy import src, analyze, pack

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


def test_analyze_verbose(WORKING_DIR):
    """
    Test functionality of the cli command `analyze`.
    """

    this_working_dir = WORKING_DIR / "test_analyze"
    this_working_dir.mkdir(parents=True, exist_ok=False)

    # write test-files
    (this_working_dir / "test.txt").write_bytes(b"test1")
    (this_working_dir / "test_.txt").write_bytes(b"test1")
    (this_working_dir / "test2.txt").write_bytes(b"test2")

    runner = CliRunner()
    result = runner.invoke(
        analyze.analyze, ["-i", str(this_working_dir), "-v"]
    )

    assert result.exit_code == 0
    assert "number of unique files: 2" in result.output
    assert f"file '{str(this_working_dir / 'test.txt')}' has duplicate(s) at" in result.output \
        or f"file '{str(this_working_dir / 'test_.txt')}' has duplicate(s) at" in result.output


def test_analyze(WORKING_DIR):
    """
    Test functionality of the cli command `analyze`.
    """

    this_working_dir = WORKING_DIR / "test_analyze"
    if this_working_dir.is_dir():
        rmtree(this_working_dir)
    this_working_dir.mkdir(parents=True, exist_ok=False)

    # write test-files
    (this_working_dir / "test.txt").write_bytes(b"test1")
    (this_working_dir / "test_.txt").write_bytes(b"test1")
    (this_working_dir / "test2.txt").write_bytes(b"test2")

    runner = CliRunner()
    result = runner.invoke(
        analyze.analyze, ["-i", str(this_working_dir)]
    )

    assert result.exit_code == 0
    blocks = result.output.split("\n\n")
    assert len(blocks) == 2
    for block in blocks:
        if len(block.split("\n")) == 1:
            assert str(this_working_dir / "test2.txt") == block
        else:
            assert str(this_working_dir / "test.txt") in block \
                and str(this_working_dir / "test_.txt") in block


def test_pack_fail(WORKING_DIR):
    """
    Test functionality of the cli command `pack`.
    """

    this_working_dir_in = WORKING_DIR / "test_pack"
    this_working_dir_out = WORKING_DIR / "test_packed"
    if this_working_dir_in.is_dir():
        rmtree(this_working_dir_in)
    if this_working_dir_out.is_dir():
        rmtree(this_working_dir_out)
    this_working_dir_in.mkdir(parents=True, exist_ok=False)
    this_working_dir_out.mkdir(parents=True, exist_ok=False)

    runner = CliRunner()
    result = runner.invoke(
        pack.pack,
        ["-i", str(this_working_dir_in), "-o", str(this_working_dir_out), "-v"]
    )

    assert result.exit_code == 1


def test_pack(WORKING_DIR):
    """
    Test functionality of the cli command `pack`.
    """

    this_working_dir_in = WORKING_DIR / "test_pack"
    this_working_dir_out = WORKING_DIR / "test_packed"
    if this_working_dir_in.is_dir():
        rmtree(this_working_dir_in)
    if this_working_dir_out.is_dir():
        rmtree(this_working_dir_out)
    this_working_dir_in.mkdir(parents=True, exist_ok=False)

    # write test-files
    (this_working_dir_in / "test.txt").write_bytes(b"test1")
    (this_working_dir_in / "test_.txt").write_bytes(b"test1")
    (this_working_dir_in / "test2.txt").write_bytes(b"test2")

    runner = CliRunner()
    result = runner.invoke(
        pack.pack,
        ["-i", str(this_working_dir_in), "-o", str(this_working_dir_out), "-v"]
    )

    assert result.exit_code == 0
    assert (this_working_dir_out / "index.txt").is_file()
    assert (this_working_dir_out / "data").is_dir()
    assert (this_working_dir_out / "data" / "test.txt").is_file()
    assert (this_working_dir_out / "data" / "test.txt").read_bytes() == b"test1"
    assert not (this_working_dir_out / "data" / "test_.txt").is_file()
    assert (this_working_dir_out / "data" / "test2.txt").is_file()
    assert (this_working_dir_out / "data" / "test2.txt").read_bytes() == b"test2"

    blocks = (this_working_dir_out / "index.txt").read_text(encoding="utf-8").split("\n\n")
    assert len(blocks) == 2
    for block in blocks:
        if len(block.split("\n")) == 1:
            assert "test2.txt" == block
        else:
            assert "test.txt" in block and "test_.txt" in block


def test_unpack_fail(WORKING_DIR):
    """
    Test functionality of the cli command `unpack`.
    """

    this_working_dir_in = WORKING_DIR / "test_packunpack"
    this_working_dir_intermediate = WORKING_DIR / "test_packed"
    this_working_dir_out = WORKING_DIR / "test_unpacked"
    if this_working_dir_in.is_dir():
        rmtree(this_working_dir_in)
    if this_working_dir_intermediate.is_dir():
        rmtree(this_working_dir_intermediate)
    if this_working_dir_out.is_dir():
        rmtree(this_working_dir_out)
    this_working_dir_in.mkdir(parents=True, exist_ok=False)
    this_working_dir_out.mkdir(parents=True, exist_ok=False)

    runner = CliRunner()
    result = runner.invoke(
        pack.pack,
        ["-i", str(this_working_dir_in), "-o", str(this_working_dir_intermediate), "-v"]
    )

    assert result.exit_code == 0

    result = runner.invoke(
        pack.unpack,
        ["-i", str(this_working_dir_intermediate), "-o", str(this_working_dir_out), "-v"]
    )

    assert result.exit_code == 1


def test_unpack(WORKING_DIR):
    """
    Test functionality of the cli command `unpack`.
    """

    this_working_dir_in = WORKING_DIR / "test_packunpack"
    this_working_dir_intermediate = WORKING_DIR / "test_packed"
    this_working_dir_out = WORKING_DIR / "test_unpacked"
    if this_working_dir_in.is_dir():
        rmtree(this_working_dir_in)
    if this_working_dir_intermediate.is_dir():
        rmtree(this_working_dir_intermediate)
    if this_working_dir_out.is_dir():
        rmtree(this_working_dir_out)
    this_working_dir_in.mkdir(parents=True, exist_ok=False)

    # write test-files
    (this_working_dir_in / "test.txt").write_bytes(b"test1")
    (this_working_dir_in / "test_.txt").write_bytes(b"test1")
    (this_working_dir_in / "test2.txt").write_bytes(b"test2")

    runner = CliRunner()
    result = runner.invoke(
        pack.pack,
        ["-i", str(this_working_dir_in), "-o", str(this_working_dir_intermediate), "-v"]
    )

    assert result.exit_code == 0

    result = runner.invoke(
        pack.unpack,
        ["-i", str(this_working_dir_intermediate), "-o", str(this_working_dir_out), "-v"]
    )

    assert (this_working_dir_out / "test.txt").is_file()
    assert (this_working_dir_out / "test.txt").read_bytes() == b"test1"
    assert (this_working_dir_out / "test_.txt").is_file()
    assert (this_working_dir_out / "test_.txt").read_bytes() == b"test1"
    assert (this_working_dir_out / "test2.txt").is_file()
    assert (this_working_dir_out / "test2.txt").read_bytes() == b"test2"
