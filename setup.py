#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup


setup(name="lala",
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      description="IRC bot based on the twisted framework",
      long_description=open("README.rst").read(),
      packages=["lala", "lala.plugins", "twisted.plugins"],
      package_dir={"lala": "lala"},
      requires=["Twisted"],
      download_url=["https://github.com/mineo/lala/tarball/master"],
      url=["http://github.com/mineo/lala"],
      license="MIT",
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Framework :: Twisted",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.6"],
      data_files=[("usr/share/doc/lala", ["config.example"])],
      install_requires=["Twisted", "appdirs", "six"],
      setup_requires=["setuptools_scm"],
      use_scm_version={"write_to": "lala/version.py"},
      extras_require={
          "iw": ["ilmwetter"],
          "websocket": ["autobahn"]
      },
      tests_require=["mock", "hypothesis"],
      test_suite="test",
)
