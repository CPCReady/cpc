# Copyright 2025 David CH.F (destroyer)
#
# Licensed under the Apache License, Version 2.0 (the "License")

import subprocess
import os
import re
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from rich.console import Console
from io import StringIO


def ansi_to_html(text: str) -> str:
    """Convierte códigos ANSI a HTML con estilos CSS"""
    # Mapeo de códigos ANSI a clases CSS
    ansi_colors = {
        '30': 'ansi-black', '31': 'ansi-red', '32': 'ansi-green',
        '33': 'ansi-yellow', '34': 'ansi-blue', '35': 'ansi-magenta',
        '36': 'ansi-cyan', '37': 'ansi-white', '90': 'ansi-bright-black',
        '91': 'ansi-bright-red', '92': 'ansi-bright-green',
        '93': 'ansi-bright-yellow', '94': 'ansi-bright-blue',
        '95': 'ansi-bright-magenta', '96': 'ansi-bright-cyan',
        '97': 'ansi-bright-white',
    }
    
    # Escapar HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Procesar códigos ANSI
    result = []
    open_spans = 0
    
    # Regex para códigos ANSI
    ansi_pattern = re.compile(r'\033\[(\d+(?:;\d+)*)m')
    last_pos = 0
    
    for match in ansi_pattern.finditer(text):
        # Añadir texto antes del código
        if match.start() > last_pos:
            result.append(text[last_pos:match.start()])
        
        codes = match.group(1).split(';')
        
        for code in codes:
            if code == '0' or code == '':  # Reset
                while open_spans > 0:
                    result.append('</span>')
                    open_spans -= 1
            elif code == '1':  # Bold
                result.append('<span class="ansi-bold">')
                open_spans += 1
            elif code == '2':  # Dim
                result.append('<span class="ansi-dim">')
                open_spans += 1
            elif code in ansi_colors:
                result.append(f'<span class="{ansi_colors[code]}">')
                open_spans += 1
        
        last_pos = match.end()
    
    # Añadir texto restante
    if last_pos < len(text):
        result.append(text[last_pos:])
    
    # Cerrar spans abiertos
    while open_spans > 0:
        result.append('</span>')
        open_spans -= 1
    
    return ''.join(result)

app = FastAPI(title="CPCReady Web Console")

# Servir archivos estáticos
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def get_console():
    """Página principal de la consola"""
    html_file = static_dir / "index.html"
    return HTMLResponse(content=html_file.read_text(), status_code=200)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para ejecución de comandos en tiempo real"""
    await websocket.accept()
    current_dir = Path.cwd()
    
    # Enviar mensaje de bienvenida
    await websocket.send_json({
        "type": "welcome",
        "html": """<div class="welcome">
  <div class="logo">
    ██████╗██████╗  ██████╗██████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗
   ██╔════╝██╔══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝
   ██║     ██████╔╝██║     ██████╔╝█████╗  ███████║██║  ██║ ╚████╔╝ 
   ██║     ██╔═══╝ ██║     ██╔══██╗██╔══╝  ██╔══██║██║  ██║  ╚██╔╝  
   ╚██████╗██║     ╚██████╗██║  ██║███████╗██║  ██║██████╔╝   ██║   
    ╚═════╝╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝   
  </div>
  <div class="subtitle">Web Console - Escribe <span class="cmd">help</span> para ver comandos</div>
</div>""",
        "cwd": str(current_dir)
    })
    
    try:
        while True:
            # Recibir comando del cliente
            data = await websocket.receive_json()
            command = data.get("command", "").strip()
            
            if not command:
                continue
            
            # Comandos especiales
            if command.lower() in ['exit', 'quit']:
                await websocket.send_json({
                    "type": "exit",
                    "html": '<div class="success">¡Hasta luego! 👋</div>'
                })
                break
            
            if command.lower() in ['clear', 'cls']:
                await websocket.send_json({"type": "clear"})
                continue
            
            if command.lower() == 'pwd':
                await websocket.send_json({
                    "type": "output",
                    "html": f'<div class="path">{current_dir}</div>'
                })
                continue
            
            if command.lower().startswith('cd '):
                path = command[3:].strip()
                try:
                    if path == '~':
                        new_dir = Path.home()
                    else:
                        new_dir = (current_dir / path).resolve()
                    
                    if new_dir.exists() and new_dir.is_dir():
                        os.chdir(new_dir)
                        current_dir = new_dir
                        await websocket.send_json({
                            "type": "output",
                            "html": f'<div class="success">📁 {current_dir}</div>',
                            "cwd": str(current_dir)
                        })
                    else:
                        await websocket.send_json({
                            "type": "output",
                            "html": f'<div class="error">cd: no such file or directory: {path}</div>'
                        })
                except Exception as e:
                    await websocket.send_json({
                        "type": "output",
                        "html": f'<div class="error">cd: {str(e)}</div>'
                    })
                continue
            
            # Ejecutar comando CPC
            try:
                full_command = f"cpc {command}"
                
                # Forzar colores
                env = os.environ.copy()
                env['FORCE_COLOR'] = '1'
                env['CLICOLOR_FORCE'] = '1'
                
                result = subprocess.run(
                    full_command,
                    shell=True,
                    cwd=current_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Convertir output a HTML (procesar códigos ANSI)
                output_html = ""
                
                if result.stdout:
                    # Convertir ANSI a HTML con colores
                    stdout_html = ansi_to_html(result.stdout)
                    output_html += f'<div class="stdout">{stdout_html}</div>'
                
                if result.stderr:
                    stderr_html = ansi_to_html(result.stderr)
                    output_html += f'<div class="stderr">{stderr_html}</div>'
                
                if result.returncode != 0 and not result.stdout and not result.stderr:
                    output_html = f'<div class="warning">⚠ Command exited with code {result.returncode}</div>'
                elif result.returncode == 0 and not result.stdout and not result.stderr:
                    output_html = '<div class="success">✓ OK</div>'
                
                await websocket.send_json({
                    "type": "output",
                    "html": output_html
                })
                
            except subprocess.TimeoutExpired:
                await websocket.send_json({
                    "type": "output",
                    "html": '<div class="error">✗ Command timeout (30s)</div>'
                })
            except FileNotFoundError:
                await websocket.send_json({
                    "type": "output",
                    "html": '<div class="error">✗ Error: \'cpc\' command not found</div>'
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "output",
                    "html": f'<div class="error">✗ Error: {str(e)}</div>'
                })
    
    except WebSocketDisconnect:
        pass


def run_server(host: str = "127.0.0.1", port: int = 6128):
    """Ejecuta el servidor FastAPI"""
    uvicorn.run(app, host=host, port=port, log_level="info")
