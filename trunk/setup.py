#!/usr/bin/env python

from distutils.core import setup

setup(name='guisaft',
      version='0.1',
      description='a simple GUI client for SAFT',
      author='Jan Huelsbergen, Stephan Dingenskirchen',
      author_email='afoo42@gmail.com',
      url='http://code.google.com/p/guisaft',
      packages=['saft', 'guisaft'],
      package_dir={'saft': 'src/saft', 'guisaft': 'src/guisaft'},
      package_data={'guisaft': ['data/guisaft.glade']},
      scripts=['src/guisaft.py'])
