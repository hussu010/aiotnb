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

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.micro}{self.releaselevel[0]}{self.serial if self.serial != 0 else ''}"


__title__ = "aiotnb"
__author__ = "AnonymousDapper"
__license__ = "MIT"
__copyright__ = "Copyright 2021 - present AnonymousDapper"
version_info: VersionInfo = VersionInfo(0, 0, 1, "alpha")
__version__ = "0.0.1a0"

from .bank import *
from .common import *
from .confirmation_validator import *
from .core import *
from .enums import *
from .errors import *
from .validator import *
