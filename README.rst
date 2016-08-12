=========================================
Named Shared Memory and Arrays for Python
=========================================

What is it?
===========

shared_array lets you create named shared memory mappings that can be shared
with other processes. The shared_memory.array module lets you use these
regions as numpy arrays.
SharedMemory and SharedNDArray objects can be pickled. This means they can be
used with the multiprocessing modules.

What is inside it?
==================

named_shmem_unix
 Cython module exposing UNIX's shm_open() and shm_unlink()

named_shmem
 Extension to mmap.mmap that lets you create named shared memory
 mappings.

array
 Numpy arrays based on shared memory.

sync
 Sinchronization utilities

Limitations
===========

* Windows is not yet supported. It should be easy, since Windows lets you
  assign tags to mappings.
* If the program fails too catastrophically, and SharedMemory objects are not
  cleanly deleted, the shared memory file will not be cleared.
* LockedNDArray, with it default constructor, uses multiprocessing.Lock.
  Therefore, it cannot be used with multiprocessing.Pool (unless one makes
  it global in each worker process).
* SharedNDArray.from_slice maps the whole memory region, not just the region
  used by the slice. It is not clear to me whether this may be a problem.
* Be careful with ´unlink_on_close´ and ´unlink´ in general. If the shared
  memory file is unlinked, and a multiprocessing process tries to load
  the SharedMemory object it will hang.
