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
Excepciones para el módulo PyCDT
"""

class CDTError(Exception):
    """Excepción base para errores de PyCDT"""
    pass

class CDTFormatError(CDTError):
    """Error de formato en el archivo CDT"""
    pass

class CDTFileNotFoundError(CDTError):
    """Archivo CDT no encontrado"""
    pass

class CDTReadError(CDTError):
    """Error al leer el archivo CDT"""
    pass

class CDTWriteError(CDTError):
    """Error al escribir el archivo CDT"""
    pass
