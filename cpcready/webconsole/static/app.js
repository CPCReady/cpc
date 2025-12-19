// WebSocket connection
let ws = null;
let commandHistory = [];
let historyIndex = -1;
let currentPath = '~';

const output = document.getElementById('output');
const input = document.getElementById('command-input');
const promptPath = document.getElementById('prompt-path');
const status = document.getElementById('status');

// Conectar al WebSocket
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        updateStatus('connected', 'Connected');
        input.focus();
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'welcome':
                appendOutput(data.html);
                if (data.cwd) {
                    updatePath(data.cwd);
                }
                break;
            
            case 'output':
                appendOutput(data.html);
                if (data.cwd) {
                    updatePath(data.cwd);
                }
                break;
            
            case 'clear':
                output.innerHTML = '';
                break;
            
            case 'exit':
                appendOutput(data.html);
                setTimeout(() => {
                    ws.close();
                    updateStatus('disconnected', 'Disconnected');
                }, 1000);
                break;
        }
        
        scrollToBottom();
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('disconnected', 'Error');
    };
    
    ws.onclose = () => {
        updateStatus('disconnected', 'Disconnected');
        setTimeout(() => {
            if (confirm('Connection lost. Reconnect?')) {
                connect();
            }
        }, 1000);
    };
}

// Actualizar estado de conexión
function updateStatus(state, text) {
    status.className = `status-indicator ${state}`;
    status.querySelector('.status-text').textContent = text;
}

// Actualizar path en el prompt
function updatePath(path) {
    currentPath = path;
    // Mostrar solo el directorio relativo al home
    const home = '/Users/' + (path.split('/')[2] || '');
    const relative = path.replace(home, '~');
    promptPath.textContent = relative || '~';
}

// Añadir output al panel
function appendOutput(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    output.appendChild(div);
}

// Scroll automático al final
function scrollToBottom() {
    output.scrollTop = output.scrollHeight;
}

// Enviar comando
function sendCommand(command) {
    if (!command.trim()) return;
    
    // Mostrar comando enviado
    appendOutput(`<div class="command-echo">$ ${command}</div>`);
    
    // Agregar al historial
    commandHistory.push(command);
    historyIndex = commandHistory.length;
    
    // Enviar por WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ command: command }));
    }
    
    // Limpiar input
    input.value = '';
}

// Event listeners
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendCommand(input.value);
    }
    
    // Navegación por historial
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (historyIndex > 0) {
            historyIndex--;
            input.value = commandHistory[historyIndex];
        }
    }
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            input.value = commandHistory[historyIndex];
        } else {
            historyIndex = commandHistory.length;
            input.value = '';
        }
    }
    
    // Ctrl+L para limpiar
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        output.innerHTML = '';
    }
    
    // Ctrl+C para cancelar (limpiar input)
    if (e.ctrlKey && e.key === 'c') {
        e.preventDefault();
        input.value = '';
        appendOutput('<div class="warning">^C</div>');
    }
});

// Auto-focus en el input cuando se hace click en cualquier parte
document.addEventListener('click', () => {
    input.focus();
});

// Prevenir pérdida de foco
input.addEventListener('blur', () => {
    setTimeout(() => input.focus(), 0);
});

// Iniciar conexión
connect();
