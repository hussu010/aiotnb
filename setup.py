# type: ignore

import re
from pathlib import Path
from sys import version_info

from setuptools import setup

requires = Path("requirements.txt").read_text().splitlines()

readme = Path("README.md").read_text()

with Path("aiotnb/__init__.py").open("r") as f:
    version = re.search(r"^__version__ = \"([^\"]+)\"", f.read(), re.M).group(1)

requires_optional = {
    "docs": ["sphinx>=3.5.4", "sphinxcontrib_trio>=1.1.2", "furo>=2021.4.11b34", "sphinx-copybutton>=0.3.1"]
}

# type annotation support for Python versions 3.6.1+
is_py36 = (version_info.major, version_info.minor) == (3, 6)
py36_compatible = is_py36 and (version_info.micro >= 1)
if py36_compatible:
    requires.append("future-annotations>=1.0.0")
    # Non-standard environments (ex. AWS Lambda, iOS_Python/Stash)
    # See: https://github.com/asottile/future-annotations#when-you-arent-using-normal-site-registration

setup(
    name="aiotnb",
    author="AnonymousDapper",
    url="https://github.com/AnonymousDapper/aiotnb",
    project_urls={},
    version=version,
    packages=["aiotnb"],
    package_data={"aiotnb": ["py.typed"]},
    license="MIT",
    description="A coroutine-based client for the TNB Network API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requires,
    extras_require=requires_optional,
    python_requires=">=3.6.1",
    classifiers=[],
)
