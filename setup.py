#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="loca-loca-localize",
    version="0.1.0",
    author="Gur Geron",
    author_email="your.email@example.com",
    description="A tool for finding localization issues in web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/LocaLocaLocalize",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "loca-loca-localize=src.main:main",
        ],
    },
) 