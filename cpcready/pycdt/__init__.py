
# Copyright (C) 2025 David CH.F (destroyer)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
PyCDT - Python CDT/TZX Tape Image Manager for Amstrad CPC
=========================================================

A Python implementation of CDT/TZX tape image file management for Amstrad CPC.
Based on the original work by Javier Garcia (Dwayne Hicks).

Author: CPCReady Team
License: GPL
"""

from .cdt import CDT
from .structures import DataHeader, AMSDOS_BAS_TYPE, AMSDOS_BIN_TYPE, AMSDOS_PROTECTED_TYPE
from .exceptions import (
    CDTError,
    CDTFormatError,
    CDTFileNotFoundError,
    CDTReadError,
    CDTWriteError
)

__version__ = "0.1.0"
__all__ = [
    "CDT",
    "DataHeader",
    "AMSDOS_BAS_TYPE",
    "AMSDOS_BIN_TYPE",
    "AMSDOS_PROTECTED_TYPE",
    "CDTError",
    "CDTFormatError", 
    "CDTFileNotFoundError",
    "CDTReadError",
    "CDTWriteError"
]
