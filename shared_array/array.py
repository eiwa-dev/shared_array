"""Shared memory numpy arrays"""

from __future__ import division, print_function, unicode_literals

import multiprocessing
import ctypes

import numpy as np

from . import named_shmem
from . import sync

__author__ = [  "Juan Carrano <jc@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

def _toshape(x):
    try:
        return tuple(x)
    except TypeError:
        return (int(x),)

def _find_ultimate_base(a):
    base = a
    while True:
        try:
            new_base = base.base
        except AttributeError:
            break
        if new_base is not None:
            base = new_base
        else:
            break

    return base

def _byte_offset(a, b):
    """Offset of a wrt b"""
    ptr = ctypes.c_uint8.from_buffer(b)
    return np.byte_bounds(a)[0] - ptr.__array_interface__['data'][0]

class SharedNDArray:
    """Shared Numpy Array.

    To get the array, use the ´array()´ method. This class also supports
    a context manager that closes the shared memory on exit.

    Example: create a 3x4 array of single-precision floats.

    >>> array = SharedNDArray.empty((3,4), np.float32)
    >>> with array as x:
    ...     x[:] = 9
    ...     print(repr(x))
    array([[ 9.,  9.,  9.,  9.],
           [ 9.,  9.,  9.,  9.],
           [ 9.,  9.,  9.,  9.]], dtype=float32)
    """
    def __init__(self, shared_memory, shape, dtype, offset = 0, **kwargs):
        """Create empty uninitialized array"""
        self.shape = _toshape(shape)
        self.dtype = np.dtype(dtype)
        self._shmem = shared_memory
        self._offset = offset

        super().__init__(**kwargs)

    @property
    def nbytes(self):
        return len(self._shmem)

    @property
    def length(self):
        return np.prod(self.shape)

    def array(self):
        return np.frombuffer(self._shmem, self.dtype, count = self.length,
                             offset = self._offset).reshape(self.shape)

    def __enter__(self):
        return self.array()

    def __exit__(self, *args):
        return self.close()

    def close(self):
        return self._shmem.close()

    @classmethod
    def empty(cls, shape, dtype, path = None, unlink_on_close = True,
                                                        **kwargs):
        """Create a new uninitialized shared array"""
        dt = np.dtype(dtype)

        length = max(dt.alignment, dt.itemsize) * np.prod(shape)

        if path is None:
            shmem = named_shmem.mktemp(length,
                                unlink_on_close = unlink_on_close)
        else:
            shmem = named_shmem.SharedMemory(path, length, create = True,
                        unlink_on_close = unlink_on_close, **kwargs)

        return cls(shmem, shape, dt)

    @classmethod
    def from_slice(cls, array_slice):
        """Convert a slice of a SharedNDArray to a SharedNDArray"""
        if not array_slice.flags['C_CONTIGUOUS']:
            raise ValueError("Slice mut be c-contiguous")

        base_mem = _find_ultimate_base(array_slice)
        memory_offset = _byte_offset(array_slice, base_mem)
        total_offset = memory_offset + base_mem.offset

        new_shmem = named_shmem.SharedMemory(base_mem.name)

        return cls(new_shmem, array_slice.shape, array_slice.dtype,
                                            offset = total_offset)

class LockedNDArray(SharedNDArray):
    """Synchronized version of SharedNDArray

    The ´array()´ method returns an array wrapped with a LockedCM object.

    >>> array = LockedNDArray.empty((3,4), np.float32)
    >>> with array.array() as x:
    ...     x[:] = 9
    ...     print(repr(x))
    array([[ 9.,  9.,  9.,  9.],
           [ 9.,  9.,  9.,  9.],
           [ 9.,  9.,  9.,  9.]], dtype=float32)
    """

    def __init__(self, *args, lock = None, lock_factory = multiprocessing.Lock, **kwargs):
        self._lock = lock or lock_factory()

        super().__init__(*args, **kwargs)

    def raw_array(self):
        """Retrieve the array without locking"""
        return super().array()

    def array(self):
        a = self.raw_array()
        return sync.LockedCM(a, self._lock)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
