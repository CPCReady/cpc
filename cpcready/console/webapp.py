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
CPCReady Web Console - Warp-style IDE in browser
"""

import asyncio
import subprocess
import shlex
import os
import webbrowser
from pathlib import Path
from datetime import datetime
import click
from aiohttp import web
import aiohttp_cors

from cpcready.utils.click_custom import CustomCommand


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPCReady Interactive Console</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        #status-bar {
            background: #007acc;
            color: white;
            padding: 4px 20px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .connected {
            color: #89d185;
        }
        
        .disconnected {
            color: #f48771;
        }
        
        #output-container {
            flex: 1;
            overflow-y: auto;
            padding: 10px 20px 20px 20px;
            background: #1e1e1e;
            scrollbar-width: thin;
            scrollbar-color: #4a4a4a #2d2d2d;
        }
        
        #output-container::-webkit-scrollbar {
            width: 12px;
        }
        
        #output-container::-webkit-scrollbar-track {
            background: #2d2d2d;
        }
        
        #output-container::-webkit-scrollbar-thumb {
            background: #4a4a4a;
            border-radius: 6px;
        }
        
        #output-container::-webkit-scrollbar-thumb:hover {
            background: #5a5a5a;
        }
        
        .output-line {
            margin: 2px 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            user-select: text;
            cursor: text;
            line-height: 1.5;
        }
        
        .output-line:first-child {
            margin-top: 10px;
        }
        
        .timestamp {
            color: #666;
            margin-right: 10px;
            user-select: none;
        }
        
        .command {
            color: #4ec9b0;
            font-weight: bold;
        }
        
        .error {
            color: #f48771;
        }
        
        .success {
            color: #89d185;
        }
        
        .info {
            color: #569cd6;
        }
        
        .warning {
            color: #dcdcaa;
        }
        
        #prompt-container {
            background: #252526;
            border-top: 2px solid #3c3c3c;
            padding: 15px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        #current-dir {
            color: #4ec9b0;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        #current-dir::before {
            content: "📁";
        }
        
        #input-line {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        #prompt {
            color: #dcdcaa;
            font-weight: bold;
            font-size: 16px;
        }
        
        #command-input {
            flex: 1;
            background: #3c3c3c;
            border: 1px solid #4a4a4a;
            border-radius: 4px;
            padding: 8px 12px;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            outline: none;
        }
        
        #command-input:focus {
            border-color: #007acc;
            box-shadow: 0 0 0 1px #007acc;
        }
        
        .welcome {
            color: #4ec9b0;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .help-text {
            color: #888;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div id="status-bar">
        <div class="status-item">
            <span id="connection-status" class="connected">● Connected</span>
        </div>
        <div class="status-item">
            <span>CPCReady Web Console v1.0</span>
        </div>
    </div>
    
    <div id="output-container"></div>
    
    <div id="prompt-container">
        <div id="current-dir"></div>
        <div id="input-line">
            <span id="prompt">$</span>
            <input type="text" id="command-input" placeholder="Enter command..." autocomplete="off">
        </div>
    </div>
    
    <script>
        const output = document.getElementById('output-container');
        const input = document.getElementById('command-input');
        const currentDirEl = document.getElementById('current-dir');
        const statusEl = document.getElementById('connection-status');
        
        let ws = null;
        let commandHistory = [];
        let historyIndex = -1;
        
        function connect() {
            ws = new WebSocket('ws://localhost:8765/ws');
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                statusEl.textContent = '● Connected';
                statusEl.className = 'connected';
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                statusEl.textContent = '● Disconnected';
                statusEl.className = 'disconnected';
                setTimeout(connect, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'output') {
                addOutput(data.text, data.style);
            } else if (data.type === 'dir') {
                currentDirEl.textContent = data.path;
            } else if (data.type === 'clear') {
                output.innerHTML = '';
            }
        }
        
        function addOutput(text, style = '') {
            const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
            const line = document.createElement('div');
            line.className = 'output-line ' + style;
            
            const ts = document.createElement('span');
            ts.className = 'timestamp';
            ts.textContent = timestamp;
            
            const content = document.createElement('span');
            content.textContent = text;
            
            line.appendChild(ts);
            line.appendChild(content);
            output.appendChild(line);
            
            // Auto scroll to bottom
            output.scrollTop = output.scrollHeight;
        }
        
        function sendCommand(cmd) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                addOutput('Not connected to server', 'error');
                return;
            }
            
            if (!cmd.trim()) return;
            
            // Add to history
            commandHistory.push(cmd);
            historyIndex = -1;
            
            // Send command
            ws.send(JSON.stringify({
                type: 'command',
                command: cmd
            }));
            
            // Clear input
            input.value = '';
        }
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendCommand(input.value);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (commandHistory.length > 0) {
                    if (historyIndex === -1) {
                        historyIndex = commandHistory.length - 1;
                    } else if (historyIndex > 0) {
                        historyIndex--;
                    }
                    input.value = commandHistory[historyIndex];
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex !== -1) {
                    historyIndex++;
                    if (historyIndex >= commandHistory.length) {
                        historyIndex = -1;
                        input.value = '';
                    } else {
                        input.value = commandHistory[historyIndex];
                    }
                }
            }
        });
        
        // Auto focus input
        input.focus();
        
        // Connect on load
        connect();
        
        // Welcome message
        addOutput('Welcome to CPCReady Interactive Web Console!', 'welcome');
        addOutput('Type "help" for assistance, "exit" to quit', 'help-text');
        addOutput('You can select and copy any text with your mouse', 'help-text');
        addOutput('', '');
    </script>
</body>
</html>
"""


class ConsoleServer:
    """Web console server"""
    
    def __init__(self):
        self.app = web.Application()
        self.clients = set()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/ws', self.handle_websocket)
        
        # Enable CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def handle_index(self, request):
        """Serve HTML page"""
        return web.Response(text=HTML_TEMPLATE, content_type='text/html')
    
    async def handle_websocket(self, request):
        """Handle WebSocket connection"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.clients.add(ws)
        
        # Send initial directory
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]
        
        await ws.send_json({
            'type': 'dir',
            'path': current_dir
        })
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = msg.json()
                    await self.handle_command(ws, data)
                elif msg.type == web.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        finally:
            self.clients.discard(ws)
        
        return ws
    
    async def handle_command(self, ws, data):
        """Handle command from client"""
        if data.get('type') != 'command':
            return
        
        command_line = data.get('command', '').strip()
        if not command_line:
            return
        
        # Echo command
        await ws.send_json({
            'type': 'output',
            'text': f'$ {command_line}',
            'style': 'command'
        })
        
        try:
            parts = shlex.split(command_line)
        except ValueError as e:
            await ws.send_json({
                'type': 'output',
                'text': f'Error: {e}',
                'style': 'error'
            })
            return
        
        if not parts:
            return
        
        cmd = parts[0]
        
        # Exit command
        if cmd in ('exit', 'quit', 'q'):
            await ws.send_json({
                'type': 'output',
                'text': 'Goodbye! 👋',
                'style': 'success'
            })
            await ws.close()
            return
        
        # Help command
        if cmd in ('help', '?'):
            await self.show_help(ws)
            return
        
        # Clear command
        if cmd == 'clear':
            await ws.send_json({'type': 'clear'})
            return
        
        # CD command
        if cmd == 'cd':
            await self.execute_cd(ws, parts)
            return
        
        # CPC commands
        cpc_commands = ['save', 'cat', 'disc', 'drive', 'run', 'version', 'rvm', 
                       'emu', 'm4', 'list', 'era', 'user', 'ren', 'model', 'mode', 'filextr']
        
        if cmd in cpc_commands:
            await self.execute_cpc(ws, parts)
            return
        
        # System command
        await self.execute_system(ws, parts)
    
    async def show_help(self, ws):
        """Show help"""
        await ws.send_json({'type': 'output', 'text': '', 'style': ''})
        await ws.send_json({'type': 'output', 'text': 'CPCReady Interactive Console Help', 'style': 'info'})
        await ws.send_json({'type': 'output', 'text': '', 'style': ''})
        await ws.send_json({'type': 'output', 'text': 'CPC Commands:', 'style': 'warning'})
        await ws.send_json({'type': 'output', 'text': '  save, cat, disc, drive, run, version, rvm, emu, m4', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '  list, era, user, ren, model, mode, filextr', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '', 'style': ''})
        await ws.send_json({'type': 'output', 'text': 'System Commands:', 'style': 'warning'})
        await ws.send_json({'type': 'output', 'text': '  cd <dir>  - Change directory', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '  <cmd>     - Execute any system command', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '', 'style': ''})
        await ws.send_json({'type': 'output', 'text': 'Console Commands:', 'style': 'warning'})
        await ws.send_json({'type': 'output', 'text': '  help      - Show this help', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '  clear     - Clear output', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '  exit/quit - Exit console', 'style': ''})
        await ws.send_json({'type': 'output', 'text': '', 'style': ''})
    
    async def execute_cd(self, ws, args):
        """Execute cd command"""
        try:
            if len(args) > 1:
                path = os.path.expanduser(args[1])
                os.chdir(path)
            else:
                os.chdir(os.path.expanduser("~"))
            
            # Update directory display
            current_dir = os.getcwd()
            home = os.path.expanduser("~")
            if current_dir.startswith(home):
                current_dir = "~" + current_dir[len(home):]
            
            await ws.send_json({'type': 'dir', 'path': current_dir})
            await ws.send_json({
                'type': 'output',
                'text': f'Changed to: {os.getcwd()}',
                'style': 'success'
            })
        except FileNotFoundError:
            await ws.send_json({
                'type': 'output',
                'text': f'Directory not found: {args[1] if len(args) > 1 else "~"}',
                'style': 'error'
            })
        except Exception as e:
            await ws.send_json({
                'type': 'output',
                'text': f'Error: {e}',
                'style': 'error'
            })
    
    async def execute_cpc(self, ws, args):
        """Execute CPC command"""
        try:
            result = subprocess.run(
                ['cpc'] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.rstrip().split('\n'):
                    await ws.send_json({
                        'type': 'output',
                        'text': line,
                        'style': ''
                    })
            
            if result.stderr:
                for line in result.stderr.rstrip().split('\n'):
                    await ws.send_json({
                        'type': 'output',
                        'text': line,
                        'style': 'error'
                    })
            
            if result.returncode != 0:
                await ws.send_json({
                    'type': 'output',
                    'text': f'Command failed with exit code {result.returncode}',
                    'style': 'error'
                })
        
        except subprocess.TimeoutExpired:
            await ws.send_json({
                'type': 'output',
                'text': 'Command timed out (30s limit)',
                'style': 'error'
            })
        except FileNotFoundError:
            await ws.send_json({
                'type': 'output',
                'text': "Error: 'cpc' command not found",
                'style': 'error'
            })
        except Exception as e:
            await ws.send_json({
                'type': 'output',
                'text': f'Error: {e}',
                'style': 'error'
            })
    
    async def execute_system(self, ws, args):
        """Execute system command"""
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.rstrip().split('\n'):
                    await ws.send_json({
                        'type': 'output',
                        'text': line,
                        'style': ''
                    })
            
            if result.stderr:
                for line in result.stderr.rstrip().split('\n'):
                    await ws.send_json({
                        'type': 'output',
                        'text': line,
                        'style': 'warning'
                    })
            
            if result.returncode != 0:
                await ws.send_json({
                    'type': 'output',
                    'text': f'Command failed with exit code {result.returncode}',
                    'style': 'error'
                })
        
        except subprocess.TimeoutExpired:
            await ws.send_json({
                'type': 'output',
                'text': 'Command timed out (30s limit)',
                'style': 'error'
            })
        except FileNotFoundError:
            await ws.send_json({
                'type': 'output',
                'text': f'Command not found: {args[0]}',
                'style': 'error'
            })
        except Exception as e:
            await ws.send_json({
                'type': 'output',
                'text': f'Error: {e}',
                'style': 'error'
            })


@click.command(cls=CustomCommand, name='web')
def webconsole():
    """
    Launch CPCReady Web Console in browser
    
    Opens a web-based interactive console with full text selection,
    copy/paste support, and a modern Warp-style interface.
    """
    async def run_server():
        server = ConsoleServer()
        runner = web.AppRunner(server.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8765)
        await site.start()
        
        print("🚀 CPCReady Web Console starting...")
        print("📡 Server: http://localhost:8765")
        print("🌐 Opening browser...")
        
        # Open browser
        webbrowser.open('http://localhost:8765')
        
        print("\n✅ Console ready!")
        print("Press Ctrl+C to stop the server\n")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
            await runner.cleanup()
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
    
    print("Goodbye! 👋")


if __name__ == "__main__":
    webconsole()
