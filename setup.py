#!/usr/bin/env python
from distutils.core import setup
setup(name="lala",
        version="0.1.5",
        author="Wieland Hoffmann",
        author_email="themineo@gmail.com",
        scripts=["run-lala.py"],
        packages=["lala", "lala.plugins"],
        package_dir = {"lala": "lala"},
        requires=["lurklib(>=0.8)"],
        download_url=["https://github.com/mineo/lala/tarball/master"],
        url=["http://github.com/mineo/lala"],
        license="MIT",
        classifiers=["Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7"],
        data_files=[("/usr/share/doc/lala", ["config.example"])]
        )
