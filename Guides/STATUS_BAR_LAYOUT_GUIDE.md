# 📊 Status Bar con Texto Izquierda y Derecha

## ✅ Implementación Completada

El `StatusBar` en `warp.py` ahora soporta texto alineado a la izquierda y derecha usando dos `Label` separados dentro de un contenedor `Horizontal`.

## 🏗️ Estructura

```
StatusBar (Static)
└── Horizontal (#status-content)
    ├── Label (#status-left)   ← Texto a la IZQUIERDA
    └── Label (#status-right)  ← Texto a la DERECHA
```

## 📝 Código Implementado

### 1. **Compose del StatusBar**

```python
def compose(self) -> ComposeResult:
    with Horizontal(id="status-content"):
        yield Label(id="status-left")
        yield Label(id="status-right")
```

### 2. **Update Status**

```python
def update_status(self):
    # TEXTO IZQUIERDO
    left_text = Text()
    left_text.append(" AMSTRAD 128K ORDENADOR PERSONAL ", style="bright_white")
    
    # TEXTO DERECHO
    right_text = Text()
    right_text.append("🟥🟩🟦 ", style="bold red")
    right_text.append(f"{a_status} A{a_selected} ", style="cyan")
    right_text.append(f"{b_status} B{b_selected} ", style="cyan")
    
    # Actualizar
    label_left = self.query_one("#status-left", Label)
    label_right = self.query_one("#status-right", Label)
    label_left.update(left_text)
    label_right.update(right_text)
```

### 3. **CSS**

```css
#status-content {
    width: 100%;
    height: 1;
    layout: horizontal;
}

#status-left {
    width: 1fr;              /* Ocupa todo el espacio disponible */
    height: 1;
    content-align: left middle;  /* Alineado a la izquierda */
}

#status-right {
    width: auto;             /* Solo el ancho necesario */
    height: 1;
    content-align: right middle; /* Alineado a la derecha */
}
```

## 🎨 Resultado Visual

```
╭─────────────────────────────────────────────────────────────╮
│  AMSTRAD 128K ORDENADOR PERSONAL     🟥🟩🟦 ● A▲ ● B         │
│  ← izquierda                                  derecha →     │
╰─────────────────────────────────────────────────────────────╯
```

## 💡 Cómo Usar

### Ejemplo 1: Cambiar el texto izquierdo

```python
left_text = Text()
left_text.append("Mi Texto Personalizado ", style="bold yellow")
left_text.append("Más info", style="cyan")

label_left = self.query_one("#status-left", Label)
label_left.update(left_text)
```

### Ejemplo 2: Cambiar el texto derecho

```python
right_text = Text()
right_text.append("🎮 ", style="bold")
right_text.append("Estado: OK", style="green")

label_right = self.query_one("#status-right", Label)
label_right.update(right_text)
```

### Ejemplo 3: Actualizar desde cualquier parte de WarpConsole

```python
def mi_funcion(self):
    status_bar = self.query_one("#status-bar", StatusBar)
    
    # Actualizar izquierda
    label_left = status_bar.query_one("#status-left", Label)
    label_left.update(Text("Nuevo texto", style="bright_white"))
    
    # Actualizar derecha
    label_right = status_bar.query_one("#status-right", Label)
    label_right.update(Text("Info", style="cyan"))
```

## 🎯 Ventajas de esta Implementación

1. ✅ **Separación clara** entre contenido izquierdo y derecho
2. ✅ **Alineación automática** gracias al layout de Textual
3. ✅ **Flexible**: Puedes poner cualquier texto o estilo en cada lado
4. ✅ **Responsive**: Se adapta automáticamente al ancho de la terminal
5. ✅ **Fácil de mantener**: Cada lado tiene su propio Label

## 🔧 Personalización Avanzada

### Cambiar colores según estado

```python
def update_status(self):
    # Cambiar color según alguna condición
    if self.algo_activo:
        style = "bold green"
    else:
        style = "dim red"
    
    left_text = Text()
    left_text.append("Estado", style=style)
    
    label_left = self.query_one("#status-left", Label)
    label_left.update(left_text)
```

### Añadir iconos o emojis

```python
left_text = Text()
left_text.append("💾 ", style="bold")
left_text.append("Guardando...", style="yellow")

right_text = Text()
right_text.append("⏱️ 12:30", style="cyan")
```

### Texto dinámico

```python
import datetime

def update_status(self):
    # Texto izquierdo
    left_text = Text()
    left_text.append(f" {self.current_project} ", style="bright_white")
    
    # Texto derecho con hora actual
    right_text = Text()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    right_text.append(f"⏰ {now}", style="cyan")
    
    # Actualizar
    self.query_one("#status-left", Label).update(left_text)
    self.query_one("#status-right", Label).update(right_text)
```

## 📊 Estados del Demo

El demo muestra 3 estados diferentes:

**Estado 1**: CPC 6128, Drive A seleccionado, ambos drives con disco
```
AMSTRAD 128K ORDENADOR PERSONAL     🟥🟩🟦 ● A▲ ● B
```

**Estado 2**: CPC 464, Drive B seleccionado, solo B con disco
```
AMSTRAD 64k COLOUR PERSONAL COMPUTER     🟥🟩🟦 ○ A  ● B▲
```

**Estado 3**: CPC 6128, Drive A seleccionado, solo A con disco
```
AMSTRAD 128K ORDENADOR PERSONAL     🟥🟩🟦 ● A▲ ○ B
```

## 🎓 Conceptos Clave

- `#status-left` usa `width: 1fr` → Toma todo el espacio disponible
- `#status-right` usa `width: auto` → Solo toma el espacio necesario
- El espacio sobrante queda entre ambos labels automáticamente
- `content-align: left middle` alinea el contenido a la izquierda verticalmente centrado
- `content-align: right middle` alinea el contenido a la derecha verticalmente centrado

## ✨ Resultado Final

Ahora tienes un status bar profesional con:
- ✅ Información del modelo CPC a la izquierda
- ✅ Estado de drives e indicadores a la derecha
- ✅ Código limpio y mantenible
- ✅ Fácil de personalizar

