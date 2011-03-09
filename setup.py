#!/usr/bin/env python
from distutils.core import setup
setup(name="lala",
        version="0.1.1",
        author="Wieland Hoffmann",
        author_email="themineo@gmail.com",
        scripts=["run-lala.py"],
        packages=["lala", "lala.plugins"],
        package_dir = {"lala": "lala"},
        requires=["lurklib"],
        download_url=["https://github.com/mineo/lala/tarball/master"],
        url=["http://github.com/mineo/lala"],
        classifiers=["Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: End Users/Desktop",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7"]
        )
