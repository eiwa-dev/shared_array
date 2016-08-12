"""Pythonic wrapper around shm_open, shm_unlink and mmap"""

from __future__ import division, print_function, unicode_literals

import os
import mmap
import uuid

# 3rd party imports

# own package imports

from . import named_shmem_unix

__author__ = [  "Juan Carrano <jc@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

class SharedMemory(mmap.mmap):
    """Named shared memory object

    This class has been made picklable so that it can be used with
    multiprocessing. It must NOT be pickled to disk or any persistent
    storage.

    When it is pickled, the ´unlink_on_close´ property
    is set to false.
    """
    def __new__(cls, path, length = None, create = False,
                unlink_on_close = False, **kwargs):

        creat_flag = os.O_CREAT if create else 0
        flags = os.O_RDWR | creat_flag
        fileno = named_shmem_unix.shm_open(path, flags)

        if length is not None:
            if create:
                os.ftruncate(fileno, length)
            _length = length
        else:
            _length = os.stat(fileno).st_size

        obj = super().__new__(cls, fileno, _length, **kwargs)
        obj._fileno = fileno
        obj._length = _length

        return obj


    def __init__(self, path, length = None, create = False,
                 unlink_on_close = False, **kwargs):
        """Open an existing named shared memory object or create a new
        one.

        If ´create´ is False, the object must already exist. If this is
        the case, ´length´ may be ommited. In that case the full length
        of the object (as given by os.stat) is memory-mapped.

        If ´create´ is True, the object is created and truncated /
        extended to the specified length.

        If ´unlink_on_close´ is True, then the object is unlinked (i.e.
        deleted) upon closing).
        """

        self.name = path
        self._unlink_on_close = unlink_on_close

        self._orig_kwargs = kwargs
        self.offset = kwargs.get("offset", 0)

        super().__init__()

    def fileno(self):
        return self._fileno

    def close(self):
        if not self.closed:
            super().close()
            if self._unlink_on_close:
                self.unlink()

    def unlink(self):
        """Remove the named memmory maped object"""
        named_shmem_unix.shm_unlink(self.name)

    def __getnewargs_ex__(self):
        return ((self.name, self._length, False, False),
                self._orig_kwargs)

    def __setstate__(self, state):
        """force _unlink_on_close to false upon unpickling"""
        self.__dict__.update(state)
        self._unlink_on_close = False

    def __del__(self):
        self.close()

def mktemp(length, unlink_on_close = True, **kwargs):
    """Temporary memory mapped buffer"""
    name = "/%s"%str(uuid.uuid1())

    return SharedMemory(name, length, create = True,
                    unlink_on_close = unlink_on_close, **kwargs)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
