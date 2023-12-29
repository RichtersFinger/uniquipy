"""
This module contains definitions implementing the uniquipy-logic.
"""

from typing import Optional, Callable
from pathlib import Path
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


def find_duplicates(
    files: list[Path],
    hash_algorithm: str = "md5",
    progress_hook: Optional[Callable] = None
) -> tuple[bool, dict[str, list[Path]]]:
    """
    Returns a tuple of a boolean summary (whether or not duplicates exist among
    `files`) and a dict containing lists of `Path`-objects keyed by
    identifiers. If a list contains more than one item, the items are
    considered identical.

    Keyword arguments:
    files -- list of `pathlib.Path`s objects
    hash_algorithm -- string identifier for the hashing algorithm used
                      (see definition of `HASHING_ALGORITHMS`)
                      (default 'md5')
    progress_hook -- hook that is executed on progress;
                     the keyword arguments of
                     - `stage`: string-identifier of the current phase
                     - `progress`: a tuple of two integers; completed tasks and
                                   total tasks for the given stage
                     are passed to the hook
                     (default None)
    """

    # define the individual steps in the discrimination hierarchy
    discriminator_hierarchy = [
        lambda file: str(file.stat().st_size),
        lambda file: hash_from_file(
            hash_algorithm,
            str(file),
            short=True
        ),
        lambda file: hash_from_file(
            hash_algorithm,
            str(file)
        ),
    ]

    uniques = {"": files}
    is_unique = False
    for stage, discriminator in enumerate(discriminator_hierarchy):
        progress = 0
        if is_unique:
            break

        # initialize list of keys that are to be deleted in the uniques-dict ..
        delete_keys = []
        # .. and new dict to store next discrimination stage information
        new_uniques = {}

        # loop current dict
        is_unique = True
        for current_value, _files in uniques.items():
            progress = progress + 1
            if len(_files) == 1:
                continue

            # if a duplicate has been detected, mark original for deletion
            # and generate new keys for supposed duplicates
            delete_keys.append(current_value)
            for file in _files:
                new_value = f"{current_value}_{discriminator(file)}"
                if new_value not in new_uniques:
                    new_uniques[new_value] = []
                else:
                    is_unique = False
                new_uniques[new_value].append(file)

            # execute hook
            if progress_hook is not None:
                progress_hook(
                    stage=f"Stage {str(stage + 1)}",
                    progress=(progress, len(uniques))
                )

        # cleanup
        for key in delete_keys:
            uniques.pop(key, None)

        # update
        uniques.update(new_uniques)

    return is_unique, uniques


def default_progress_hook(**kwargs) -> None:
    """
    Default progress-hook that can be used with the function `find_duplicates`.
    """

    p1 = kwargs["progress"][0]
    p2 = kwargs["progress"][1]
    p = p1 / p2
    n = 10
    s = "[" + "#"*int(p * n) + "-"*(n - int(p * n)) + "]"
    print(
        f"[{kwargs['stage']}] {s} ({p1}/{p2})",
        end="\r"
    )
