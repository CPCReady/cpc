# Copyright 2025 David CH.F (destroyer)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

import click
import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.console import ok, error, blank_line, info2

@click.command(cls=RichCommand)
def configweb():
    """Configure CPCReady options via web interface (Streamlit)."""
    try:
        # Ruta al script de Streamlit
        script_path = Path(__file__).parent / "streamlit_app.py"
        
        if not script_path.exists():
            blank_line(1)
            error(f"Streamlit app not found at: {script_path}")
            blank_line(1)
            return
        
        blank_line(1)
        ok("Starting CPCReady configuration interface...")
        
        # Abrir navegador en un thread separado
        url = "http://localhost:8501"
        
        def open_browser():
            time.sleep(2)
            webbrowser.open(url)
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        ok(f"Web interface will open at: {url}")
        info2("Press Ctrl+C to stop the server")
        blank_line(1)
        
        # Ejecutar Streamlit usando os.execvp para reemplazar el proceso actual
        # Esto evita problemas de fork en macOS
        import os
        os.execvp(
            sys.executable,
            [sys.executable, "-m", "streamlit", "run", str(script_path),
             "--server.headless", "true",
             "--browser.gatherUsageStats", "false"]
        )
        
    except FileNotFoundError:
        blank_line(1)
        error("Streamlit is not installed. Install it with: pip install streamlit")
        blank_line(1)
    except KeyboardInterrupt:
        blank_line(1)
        ok("Server stopped")
        blank_line(1)
    except Exception as e:
        blank_line(1)
        error(f"Error running web interface: {e}")
        blank_line(1)
