from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path

def show_readme(path="README.md"):
    console = Console()

    readme_path = Path(path)
    if not readme_path.exists():
        console.print(f"[red]No se encontró el archivo {path}[/red]")
        return

    markdown_text = readme_path.read_text(encoding="utf-8")
    md = Markdown(markdown_text)

    console.print(md)

if __name__ == "__main__":
    show_readme()