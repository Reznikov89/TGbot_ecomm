"""
Setup script for TGecomm
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tgecomm",
    version="1.0.0",
    author="TGecomm Team",
    description="Telegram client application built with Telethon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tgecomm",
    packages=find_packages(exclude=["tests", "venv", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tgecomm=tgecomm.main:main",
        ],
    },
)

