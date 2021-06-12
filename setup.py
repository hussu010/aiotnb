# type: ignore

import re
from pathlib import Path

from setuptools import setup

requires = Path("requirements.txt").read_text().splitlines()

readme = Path("README.md").read_text()

with Path("aiotnb/__init__.py").open("r") as f:
    version = re.search(r"^__version__ = \"([^\"]+)\"", f.read(), re.M).group(1)

requires_optional = {
    "docs": ["sphinx>=3.5.4", "sphinxcontrib_trio>=1.1.2", "furo>=2021.4.11b34", "sphinx-copybutton>=0.3.1"]
}

setup(
    name="aiotnb",
    author="AnonymousDapper",
    url="https://github.com/AnonymousDapper/aiotnb",
    project_urls={},
    version=version,
    packages=["aiotnb", "aiotnb.models", "aiotnb.validation"],
    package_data={"aiotnb": ["py.typed"]},
    license="MIT",
    description="A coroutine-based client for the TNB Network API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requires,
    extras_require=requires_optional,
    python_requires=">=3.8.0",
    classifiers=[],
)
