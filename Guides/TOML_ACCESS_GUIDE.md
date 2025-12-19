# Acceso a Datos del Archivo TOML

## Resumen

El archivo de configuración TOML se encuentra en: `~/.config/cpcready/cpcready.toml`

## Estructura del Archivo TOML

```toml
[drive]
drive_a = "/ruta/al/disco_a.dsk"
drive_b = "/ruta/al/disco_b.dsk"
selected_drive = "A"  # o "B"

[system]
user = 0
model = "6128"  # o "464", "664"
mode = 1

[emulator]
default = "RetroVirtualMachine"  # o "M4Board"
retro_virtual_machine_path = "/Applications/Retro Virtual Machine 2.app"
m4board_ip = "192.168.1.1"
```

## Cómo Acceder a los Datos

### 1. Importar ConfigManager

```python
from cpcready.utils.toml_config import ConfigManager
```

### 2. Crear Instancia

```python
config = ConfigManager()
```

### 3. Acceder a Valores Individuales

```python
# Método: config.get(seccion, clave, valor_por_defecto)

# Obtener selected_drive
selected_drive = config.get('drive', 'selected_drive', 'A')

# Obtener user
user = config.get('system', 'user', 0)

# Obtener model
model = config.get('system', 'model', '6128')

# Obtener mode
mode = config.get('system', 'mode', 1)
```

### 4. Acceder a Secciones Completas

```python
# Obtener toda la sección drive
drive_config = config.get_section('drive')
drive_a = drive_config.get('drive_a', '')
drive_b = drive_config.get('drive_b', '')
selected_drive = drive_config.get('selected_drive', 'A')

# Obtener toda la sección system
system_config = config.get_section('system')
user = system_config.get('user', 0)
model = system_config.get('model', '6128')
mode = system_config.get('mode', 1)
```

### 5. Modificar Valores

```python
# Establecer un valor individual
config.set('drive', 'selected_drive', 'B')

# Establecer múltiples valores en una sección
config.set_section('system', {
    'user': 1,
    'model': '464',
    'mode': 2
})
```

## Ejemplo Completo en warp.py

El archivo `cpcready/console/warp.py` ya ha sido modificado para acceder a estos datos:

```python
def update_drive_status(self):
    """Actualiza el estado de los drives en la barra de estado"""
    # Recargar configuración desde el archivo
    self.config_manager = ConfigManager()
    
    # Acceder a sección drive
    drive_config = self.config_manager.get_section('drive')
    drive_a = drive_config.get('drive_a', '')
    drive_b = drive_config.get('drive_b', '')
    selected_drive = drive_config.get('selected_drive', 'A')
    
    # Acceder a sección system
    system_config = self.config_manager.get_section('system')
    user = system_config.get('user', 0)
    model = system_config.get('model', '6128')
    mode = system_config.get('mode', 1)
    
    # Usar los datos...
    print(f"Selected Drive: {selected_drive}")
    print(f"User: {user}, Model: {model}, Mode: {mode}")
```

## Valores Actuales en tu Sistema

Según el test ejecutado, estos son los valores actuales:

- **Drive A**: `/Users/destroyer/PROJECTS/CPCReady/cpc/poeoeoeoe.dsk`
- **Drive B**: `/Users/destroyer/PROJECTS/CPCReady/cpc/pepepe.dsk`
- **Selected Drive**: `b`
- **User**: `0`
- **Model**: `6128`
- **Mode**: `1`
- **Emulador Default**: `M4Board`

## Notas Importantes

1. **ConfigManager** gestiona automáticamente la creación del archivo si no existe
2. Los valores por defecto se establecen automáticamente si faltan claves
3. El archivo es legible y editable manualmente
4. Los cambios se persisten inmediatamente al usar `set()` o `set_section()`

