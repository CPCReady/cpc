#!/usr/bin/env python3
"""
Demo: Status Bar con texto a izquierda y derecha
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout

console = Console()

def demo_status_bar():
    """Demuestra cómo se verá el status bar con texto a izquierda y derecha"""

    console.print("\n" + "="*80)
    console.print("📊 DEMO: Status Bar con Texto Izquierda y Derecha", style="bold yellow")
    console.print("="*80 + "\n")

    # Simular diferentes estados
    states = [
        {
            "model": "6128",
            "selected": "A",
            "drive_a": "game.dsk",
            "drive_b": "tools.dsk"
        },
        {
            "model": "464",
            "selected": "B",
            "drive_a": "",
            "drive_b": "demo.dsk"
        },
        {
            "model": "6128",
            "selected": "A",
            "drive_a": "system.dsk",
            "drive_b": ""
        }
    ]

    for i, state in enumerate(states, 1):
        console.print(f"\n[bold cyan]Estado {i}:[/bold cyan]")

        # TEXTO IZQUIERDO
        left_text = Text()
        if state["model"] == '464':
            left_text.append(" AMSTRAD 64k COLOUR PERSONAL COMPUTER ", style="bright_white")
        elif state["model"] == '664':
            left_text.append(" AMSTRAD 64k COLOUR PERSONAL COMPUTER ", style="bright_white")
        else:
            left_text.append(" AMSTRAD 128K ORDENADOR PERSONAL ", style="bright_white")

        # TEXTO DERECHO
        a_status = "●" if state["drive_a"] else "○"
        b_status = "●" if state["drive_b"] else "○"
        a_selected = "▲" if state["selected"] == "A" else " "
        b_selected = "▲" if state["selected"] == "B" else " "

        right_text = Text()
        right_text.append("🟥🟩🟦 ", style="bold red")
        right_text.append(f"{a_status} A{a_selected} ",
                         style="bold cyan" if state["selected"] == "A" else "cyan")
        right_text.append(f"{b_status} B{b_selected} ",
                         style="bold cyan" if state["selected"] == "B" else "cyan")

        # Crear una línea simulando el layout
        width = 78  # Ancho disponible dentro del panel
        left_str = left_text.plain
        right_str = right_text.plain
        spaces_needed = width - len(left_str) - len(right_str)

        # Combinar textos con espacios
        combined = Text()
        combined.append_text(left_text)
        combined.append(" " * spaces_needed)
        combined.append_text(right_text)

        # Mostrar en panel
        panel = Panel(
            combined,
            border_style="white",
            padding=(0, 1),
            height=3
        )
        console.print(panel)

        # Detalles
        console.print(f"  • Modelo: {state['model']}")
        console.print(f"  • Drive seleccionado: {state['selected']}")
        console.print(f"  • Drive A: {state['drive_a'] or 'vacío'}")
        console.print(f"  • Drive B: {state['drive_b'] or 'vacío'}")

    console.print("\n" + "="*80)
    console.print("✅ En warp.py ahora tienes:", style="bold green")
    console.print("  • #status-left  → Alineado a la IZQUIERDA (modelo CPC)")
    console.print("  • #status-right → Alineado a la DERECHA (drives + indicadores)")
    console.print("="*80 + "\n")

if __name__ == "__main__":
    demo_status_bar()

