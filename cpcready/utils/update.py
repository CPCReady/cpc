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

import requests
import packaging.version
import os
import time
from pathlib import Path
from cpcready.utils.version import __version__
from cpcready.utils.console import warn
from rich.console import Console
console = Console()

# Cache file para evitar consultas frecuentes a PyPI
CACHE_FILE = Path.home() / ".config" / "cpcready" / "update_cache"
CACHE_DURATION = 3600 * 6  # 6 horas en segundos


def get_latest_version_from_pypi():
    """Obtiene la última versión disponible en PyPI."""
    try:
        response = requests.get(
            "https://pypi.org/pypi/cpcready/json",
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except (requests.RequestException, KeyError, ValueError):
        # Si falla la consulta, no hacer nada
        pass
    return None


def is_cache_valid():
    """Verifica si el cache de actualización sigue siendo válido."""
    if not CACHE_FILE.exists():
        return False
    
    try:
        cache_time = CACHE_FILE.stat().st_mtime
        return (time.time() - cache_time) < CACHE_DURATION
    except OSError:
        return False


def read_cached_version():
    """Lee la versión cacheada del archivo."""
    try:
        if CACHE_FILE.exists():
            return CACHE_FILE.read_text().strip()
    except OSError:
        pass
    return None


def write_cached_version(version):
    """Escribe la versión al cache."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(version)
    except OSError:
        pass


def check_for_updates():
    """
    Verifica si hay actualizaciones disponibles.
    Usa cache para evitar consultas frecuentes a PyPI.
    """
    # Si el cache es válido, usar la versión cacheada
    if is_cache_valid():
        latest_version = read_cached_version()
    else:
        # Consultar PyPI y actualizar cache
        latest_version = get_latest_version_from_pypi()
        if latest_version:
            write_cached_version(latest_version)
    
    if not latest_version:
        return False
    
    try:
        current = packaging.version.parse(__version__)
        latest = packaging.version.parse(latest_version)
        return latest > current, latest_version
    except packaging.version.InvalidVersion:
        return False, None


def show_update_notification():
    """Shows update notification if available."""
    try:
        has_update, latest_version = check_for_updates()
        if has_update:
            from rich.panel import Panel
            msg = (
                f"[yellow]New version available: v{latest_version} (current: v{__version__})[/yellow]\n"
                f"[yellow]Update with: pipx upgrade cpcready[/yellow]"
            )
            panel = Panel(msg, border_style="red", style="yellow", width=60)
            console.print(panel)
    except Exception:
        # In case of any error, silently do nothing
        pass