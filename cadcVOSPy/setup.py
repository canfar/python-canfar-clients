# Use "distribute"
from cadcvos.__version__ import version
import os
from setuptools import setup, find_packages
import sys


if sys.version_info[0] > 2:
    print 'The cadcvos package is only compatible with Python version 2.n'
    sys.exit(-1)

# Build the list of scripts to be installed.
script_dir = 'scripts'
scripts = []
for script in os.listdir(script_dir):
    if script[-1] in ["~", "#"]:
        continue
    scripts.append(os.path.join(script_dir, script))

setup(name='cadcvos',
      version=version,
      description='CADC VOS Python library',
      url='This is a Home-page.',
      author='Canadian Astronomy Data Centre',
      author_email='cadc@nrc.ca',
      license='GPLv3',
      long_description='Python library for the CADC VOS service',
      packages=find_packages(),
      scripts=scripts,
      provides=['cadcvos'],
      zip_safe=False,
      requires=['mock', 'lxml', 'requests'])

