"""Support for named shared memory regions under Unix

Uses shm_open and shm_unlink.
"""

from __future__ import division, print_function, unicode_literals

import os

cimport posix.mman
cimport posix.fcntl as _pf
cimport cpython.exc

__author__ = [  "Juan Carrano <jc@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

def shm_open(path, flags, mode=0o777):
    """Make posix.mman.shm_open compatible with python's os.open"""
    fd = posix.mman.shm_open(path.encode(), flags, mode)

    if fd == -1:
        cpython.exc.PyErr_SetFromErrno(OSError)
    else:
        return fd

def shm_unlink(path):
    return posix.mman.shm_unlink(path.encode())

