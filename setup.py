#!/usr/bin/env python3
"""
Setup script for codebase-context tool
Makes it installable via pip and adds a global command
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="codebase-context",
    version="1.0.0",
    author="MacePh",
    description="Generate intelligent codebase context for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MacePh/codebase-context",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "codebase-context=codebase_context.main:main",
        ],
    },
)