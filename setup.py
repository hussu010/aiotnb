# type: ignore

import re
from pathlib import Path

from setuptools import setup

requires = Path("requirements.txt")

readme = Path("README.md")

with Path("aiotnb/__init__.py").open("r") as f:
    version = re.search(r"^__version__ = \"([^\"]+)\"", f.read(), re.M).group(1)

requires_optional = {
    "docs": [
        "sphinx",  # documentation
    ]
}

setup(
    name="aiotnb",
    author="AnonymousDapper",
    url="https://github.com/AnonymousDapper/aiotnb",
    project_urls={},
    version=version,
    packages=[],
    license="MIT",
    description="A coroutine-based client for the TNB Network API",
    long_description=readme.read_text().splitlines(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requires.read_text().splitlines(),
    extras_require=requires_optional,
    python_requires=">=3.8.0",
    classifiers=[],
)
