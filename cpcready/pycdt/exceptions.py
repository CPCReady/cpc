
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
