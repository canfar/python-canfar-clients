#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# /*+
# ************************************************************************
# ****  C A N A D I A N   A S T R O N O M Y   D A T A   C E N T R E  *****
# *
# * (c) 2014.                            (c)2014.
# * National Research Council            Conseil national de recherches
# * Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
# * All rights reserved                  Tous droits reserves
# *
# * NRC disclaims any warranties,        Le CNRC denie toute garantie
# * expressed, implied, or statu-        enoncee, implicite ou legale,
# * tory, of any kind with respect       de quelque nature que se soit,
# * to the software, including           concernant le logiciel, y com-
# * without limitation any war-          pris sans restriction toute
# * ranty of merchantability or          garantie de valeur marchande
# * fitness for a particular pur-        ou de pertinence pour un usage
# * pose.  NRC shall not be liable       particulier.  Le CNRC ne
# * in any event for any damages,        pourra en aucun cas etre tenu
# * whether direct or indirect,          responsable de tout dommage,
# * special or general, consequen-       direct ou indirect, particul-
# * tial or incidental, arising          ier ou general, accessoire ou
# * from the use of the software.        fortuit, resultant de l'utili-
# *                                      sation du logiciel.
# *
# ************************************************************************
# *
# *   Script Name:       setup.py
# *
# *   Purpose:
# *      Distutils setup script for GMS Python client
# *
# *   Functions:
# *
# *
# *
# ****  C A N A D I A N   A S T R O N O M Y   D A T A   C E N T R E  *****
# ************************************************************************
# -*/

# Use "distribute"
from gmsclient.__version__ import version
import os
from setuptools import setup, find_packages
import sys


if sys.version_info[0] > 2:
    print 'The GMS package is only compatible with Python version 2.n'
    sys.exit(-1)

# Build the list of scripts to be installed.
script_dir = 'scripts'
scripts = []
for script in os.listdir(script_dir):
    if script[-1] in ["~", "#"]:
        continue
    scripts.append(os.path.join(script_dir, script))

setup(name='cadcgms',
      version=version,
      description='CADC GMS Python client',
      url='This is a Home-page.',
      author='Canadian Astronomy Data Centre',
      author_email='cadc@nrc.ca',
      license='GPLv3',
      long_description='Python client library for the CADC GMS service',
      packages=find_packages(),
      scripts=scripts,
      provides=['gmsclient'],
      zip_safe=False,
      requires=['mock', 'pyOpenSSL', 'lxml', 'requests'])
