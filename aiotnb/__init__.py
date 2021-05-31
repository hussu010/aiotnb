"""
TNB Network Client
~~~~~~~~~~~~~~~~~~

A coroutine-based client for the TNB Network API.

:copyright: (c) 2021 - present AnonymousDapper
:license: MIT, see LICENSE

"""
from dataclasses import dataclass


@dataclass
class VersionInfo:
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int = 0

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.micro}{self.releaselevel[0]}{self.serial if self.serial != 0 else ''}"


__title__ = "aiotnb"
__author__ = "AnonymousDapper"
__license__ = "MIT"
__copyright__ = "Copyright 2021 - present AnonymousDapper"
version_info = VersionInfo(0, 0, 1, "alpha")
__version__ = "0.0.1a"

from .core import *
from .exceptions import *
from .http import *
from .models import *
