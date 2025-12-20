
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
