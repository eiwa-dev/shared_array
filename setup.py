from setuptools import setup
from distutils.extension import Extension
import Cython.Distutils

extensions = [
    Extension("shared_array.named_shmem_unix",
	["shared_array/named_shmem_unix.pyx"],
        libraries = ['rt'])
]

setup(name='shared_array',
      version='0.1',
      description='Named Shared Memory and numpy Arrays',
      url='https://bitbucket.org/eiwa_dev/shared_array',
      author='Juan Carrano',
      author_email='jc@eiwa.ag',
      license='Propietary',
      packages=['shared_array'],
      install_requires=[
          'numpy',
      ],
      setup_requires=[
          'cython',
      ],
      ext_modules = extensions,
      cmdclass={'build_ext': Cython.Distutils.build_ext},
      zip_safe=True)
