"""Lock wrapper"""

from __future__ import division, print_function, unicode_literals

import multiprocessing

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

class LockNotAcquired(Exception):
    pass

class LockedCM:
    """Wrap an object with a lock"""
    def __init__(self, obj, lock = None, lock_factory = multiprocessing.Lock):
        self.obj = obj
        self.lock = lock or lock_factory()

    def acquire(self, *args, **kwargs):
        return self.lock.acquire(*args, **kwargs)

    def release(self):
        return self.lock.release()

    def __enter__(self):
        if self.acquire():
            return self.obj
        else:
            raise LockNotAcquired("Could not lock")

    def __exit__(self, *args):
        self.release()
