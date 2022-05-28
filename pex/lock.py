# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, print_function

import os

from pex.enum import Enum
from pex.typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import IO


class FileLockStyle(Enum["FileLockStyle.Value"]):
    """The locking mechanism to use on POSIX systems. Ignored on Windows."""

    class Value(Enum.Value):
        pass

    BSD = Value("bsd")
    POSIX = Value("posix")


class FileLocker:
    def __init__(
        self,
        style,  # type: FileLockStyle.Value
    ):
        # type: (...) -> None
        if os.name == 'nt' or style == FileLockStyle.BSD:
            from pex.third_party import portalocker

            def lock_exclusive(lock_fd):
                # type: (IO) -> None
                portalocker.lock(lock_fd, portalocker.LockFlags.EXCLUSIVE)

            def unlock(lock_fd):
                # type: (IO) -> None
                portalocker.unlock(lock_fd)

        else:
            # TODO: Switch this to portalocker as well. Will require adding support to portalocker
            #  for choosing betweeen lockf and flock (it currently always uses flock).
            #  We could then get rid of this class entirely and use the portalocker API directly.
            import fcntl

            def lock_exclusive(lock_fd):
                # type: (IO) -> None
                fcntl.lockf(lock_fd, fcntl.LOCK_EX)  # A blocking write lock.

            def unlock(lock_fd):
                # type: (IO) -> None
                fcntl.lockf(lock_fd, fcntl.LOCK_UN)

        self.lock_exclusive = lock_exclusive
        self.unlock = unlock
