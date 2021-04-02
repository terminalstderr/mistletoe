from setuptools import setup, find_packages
import mistletoe

setup(name='mistletoe-tcopy',
      packages=find_packages(),
      version=mistletoe.__version__,
      license='MIT',
      description='A fast, extensible Markdown parser in pure Python. Supports a copy() method on all tokens.',
      url='https://github.com/terminalstderr/mistletoe',
      author='Ryan Leonard',
      author_email='rleonar7@uoregon.edu',
      entry_points={'console_scripts': ['mistletoe = mistletoe.__main__:main']},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Markup',
          ],
      keywords='markdown lexer parser development',
      python_requires='~=3.3',
      zip_safe=False)
