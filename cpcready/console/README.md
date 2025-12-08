# CPCReady Interactive Console

Módulos de consola interactiva para CPCReady con dos variantes:

## Comandos Disponibles

### `cpc console`

Consola interactiva con barra de estado inferior (estilo clásico).

**Características:**
- Prompt con información del directorio actual
- Barra de estado inferior con información del sistema
- Historial de comandos persistente
- Autocompletado de comandos
- Ejecución de comandos CPC y del sistema

**Uso:**
```bash
cpc console
```

**Dentro de la consola:**
```
CPCReady ~/projects
> disc info
> drive status
> ls -la
> help
> exit
```

---

### `cpc interactive`

Consola interactiva con panel de salida con scroll (estilo moderno).

**Características:**
- Panel de salida superior con scroll vertical (últimas 1000 líneas)
- Panel de prompt inferior fijo
- Barra de estado con información del sistema
- Timestamps en cada línea de salida
- Historial de comandos persistente
- Autocompletado de comandos
- Colores y estilos con Rich

**Uso:**
```bash
cpc interactive
```

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Output (scrollable)                                 │
│                                                     │
│ 10:30:45 $ disc info                                │
│ 10:30:45 Disc: juego.dsk                           │
│ 10:30:45 Format: Data                               │
│ 10:30:45 Files: 12                                  │
│                                                     │
│ (últimas N líneas según altura de terminal)        │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ ●●● CPC 6128 128K │ A:● ✓ juego.dsk │ ...          │
└─────────────────────────────────────────────────────┘
CPCReady ~/projects $
```

---

## Información de la Barra de Estado

Ambas consolas muestran:

1. **Modelo CPC**: Modelo actual (464/664/6128) y memoria
2. **Drive A**: Estado del disco en drive A
   - `●` = Drive seleccionado
   - `○` = Drive no seleccionado
   - `✓` = Disco insertado
   - `○` = Drive vacío
3. **Drive B**: Estado del disco en drive B
4. **Emulador**: Emulador configurado (RVM, M4Board, etc.)
5. **Mode**: Modo de video actual (0, 1, 2)

**Ejemplo:**
```
●●● CPC 6128 128K │ A:● ✓ juego.dsk │ B:○ ○ Empty │ EMU: RVM │ Mode: 1
```

---

## Comandos Disponibles

### Comandos CPC

Todos los comandos de CPCReady están disponibles:

```bash
save <file>           # Guardar archivo en disco virtual
cat                   # Listar archivos del disco
disc info             # Información del disco
drive status          # Estado de los drives
run <file>            # Ejecutar archivo en emulador
list <file>           # Listar archivo BASIC
era <file>            # Borrar archivo
ren <old> <new>       # Renombrar archivo
model [464|664|6128]  # Ver/cambiar modelo CPC
mode [0|1|2]          # Ver/cambiar modo de video
user [0-15]           # Cambiar número de usuario
emu <emulator>        # Configurar emulador
rvm                   # Comandos de RetroVirtualMachine
version               # Información de versión
```

### Comandos del Sistema

Comandos Unix/Linux estándar:

```bash
ls                    # Listar archivos
cd <dir>              # Cambiar directorio
pwd                   # Mostrar directorio actual
cat <file>            # Mostrar contenido de archivo
grep <pattern>        # Buscar en archivos
find <path>           # Buscar archivos
echo <text>           # Imprimir texto
mkdir <dir>           # Crear directorio
rm <file>             # Eliminar archivo
cp <src> <dst>        # Copiar archivo
mv <src> <dst>        # Mover/renombrar archivo
```

### Comandos Especiales

```bash
help, ?               # Mostrar ayuda
clear                 # Limpiar salida (solo interactive)
exit, quit, q         # Salir de la consola
```

---

## Atajos de Teclado

- **Ctrl+C**: Cancelar entrada actual (no sale de la consola)
- **Ctrl+D**: Salir de la consola
- **↑ / ↓**: Navegar por el historial de comandos
- **Tab**: Autocompletar comandos

---

## Historial de Comandos

El historial se guarda de forma persistente en:

- **console**: `~/.config/cpcready/console_history.txt`
- **interactive**: `~/.config/cpcready/interactive_history.txt`

El historial persiste entre sesiones.

---

## Ejemplos de Uso

### Workflow de Desarrollo

```bash
# Iniciar consola interactiva
cpc interactive

# Dentro de la consola:
> cd ~/proyectos/mi_juego
> disc create juego.dsk
> save main.bas
> save sprites.bin
> disc info
> run main.bas
> exit
```

### Gestión de Discos

```bash
cpc interactive

> drive status
> disc info
> cat
> era temp.tmp
> ren old.bas new.bas
> save nuevo.bas
```

### Testing Rápido

```bash
cpc console

> model 6128
> mode 1
> disc create test.dsk
> save test.bas
> run test.bas
```

---

## Diferencias entre Console e Interactive

| Característica | `console` | `interactive` |
|----------------|-----------|---------------|
| Barra de estado | ✅ Inferior | ✅ Inferior |
| Panel de salida | ❌ Scroll del terminal | ✅ Panel con scroll |
| Timestamps | ❌ | ✅ |
| Buffer de salida | Terminal | 1000 líneas |
| Comando clear | Limpia terminal | Limpia buffer |
| Layout | Simple | Panel + Status |
| Actualización | Al ejecutar comando | Tiempo real |

---

## Implementación Técnica

### Console (Clásico)

- **Tecnología**: `prompt_toolkit`
- **UI**: Barra inferior con `bottom_toolbar`
- **Historial**: `FileHistory`
- **Autocompletado**: `WordCompleter`

### Interactive (Moderno)

- **Tecnología**: `rich` + `prompt_toolkit`
- **UI**: `Panel`, `Table`, `Layout`
- **Buffer**: `deque` con max 1000 líneas
- **Output**: Renderizado con Rich
- **Status**: Tabla con información del sistema

---

## Troubleshooting

### La consola no muestra colores

Asegúrate de que tu terminal soporte colores ANSI:

```bash
echo $TERM
# Debe mostrar algo como: xterm-256color
```

### El historial no funciona

Verifica permisos en:

```bash
ls -la ~/.config/cpcready/
```

### Comandos CPC no se ejecutan

Verifica que CPCReady esté instalado correctamente:

```bash
cpc version
```

---

## Ver También

- [CLI Principal](../cli.py) - Comandos principales de CPCReady
- [Utils](../utils/) - Utilidades compartidas
- [Rich Documentation](https://rich.readthedocs.io/) - Documentación de Rich
- [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) - Documentación de prompt_toolkit
