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


import click
import webbrowser
import time
import threading
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.console import ok, error, blank_line, info2


@click.command(cls=RichCommand)
@click.option('--port', default=6128, help='Puerto del servidor web')
@click.option('--no-browser', is_flag=True, help='No abrir navegador automáticamente')
def webconsole(port, no_browser):
    """Web console interface for CPCReady."""
    try:
        from .server import run_server
        
        blank_line(1)
        ok(f"Starting web console on http://localhost:{port}")
        
        # Abrir navegador después de 1 segundo
        if not no_browser:
            def open_browser():
                time.sleep(1.5)
                webbrowser.open(f"http://localhost:{port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        info2("Press Ctrl+C to stop the server")
        blank_line(1)
        
        # Ejecutar servidor (bloqueante)
        run_server(host="127.0.0.1", port=port)
        
    except ImportError as e:
        blank_line(1)
        error(f"Missing dependencies: {e}")
        error("Install with: pip install fastapi uvicorn websockets")
        blank_line(1)
    except Exception as e:
        blank_line(1)
        error(f"Error starting web console: {e}")
        blank_line(1)
