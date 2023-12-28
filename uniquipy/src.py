"""
This module contains definitions implementing the uniquipy-logic.
"""

import hashlib

HASHING_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512
}

def hash_from_file(
    algorithm: str,
    path: str,
    chunk_size: int = 65536,
    short: bool = False
) -> str:
    """
    Returns the file hash as string.

    The method is specified via string-identifier (see definition of
    `HASHING_ALGORITHMS`).

    Keyword arguments:
    algorithm -- string identifier for hashing method
                 (see definition of `HASHING_ALGORITHMS`)
    path -- path to the file intended for hashing
    chunk_size -- size of chunks
                  (default 65536)
    short -- whether to use entire file for hashing or exit after first chunk
             (default False)
    """

    # https://stackoverflow.com/a/22058673
    hashed = HASHING_ALGORITHMS[algorithm]()

    with open(path, "rb") as file:
        while (data := file.read(chunk_size)):
            hashed.update(data)
            if short:
                break

    return hashed.hexdigest()
