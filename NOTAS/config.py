"""
Selector sencillo de emulador usando questionary.

Al ejecutarlo preguntará al usuario si quiere usar
"RetroVirtualMachine" o "M4Board" y guardará la elección
en `emulator_choice.json` junto al archivo.

Uso:
	python3 NOTAS/config.py

Si `questionary` no está instalado, usa un fallback por consola.
"""

from pathlib import Path
import json

import sys
import re
from pathlib import Path

CHOICES = ["RetroVirtualMachine", "M4Board"]
DEFAULT = "M4Board"




def ask_with_questionary():
	try:
		import questionary
	except Exception:
		return None

	return questionary.select(
		"Selecciona el emulador:",
		choices=CHOICES,
		default=DEFAULT
	).ask()



def ask_with_fallback():
	print("questionary no disponible; usando modo texto.")
	for i, c in enumerate(CHOICES, start=1):
		sel = " (por defecto)" if c == DEFAULT else ""
		print(f"{i}. {c}{sel}")

	while True:
		choice = input(f"Elige número (1-2) o escribe el nombre [Enter={DEFAULT}]: ").strip()
		if not choice:
			return DEFAULT
		if choice.isdigit():
			idx = int(choice) - 1
			if 0 <= idx < len(CHOICES):
				return CHOICES[idx]
		else:
			# permitir coincidencia insensible a mayúsculas
			for c in CHOICES:
				if choice.lower() == c.lower():
					return c
		print("Opción inválida, inténtalo de nuevo.")




def save_choice(choice: str, path: Path, file_path: str = None, ip: str = None):
	data = {"emulator": choice}
	if file_path:
		data["file_path"] = file_path
	if ip:
		data["ip"] = ip
	try:
		path.write_text(json.dumps(data, indent=2), encoding="utf-8")
		print(f"Elección guardada en: {path}")
	except Exception as e:
		print(f"Error guardando la elección: {e}")


def validar_ip(ip):
	# IPv4 simple
	patron = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
	if not patron.match(ip):
		return False
	partes = ip.split('.')
	return all(0 <= int(p) <= 255 for p in partes)




def main():
	out_file = Path(__file__).parent / "emulator_choice.json"

	# Intentar questionary primero
	choice = ask_with_questionary()
	if choice is None:
		choice = ask_with_fallback()

	if choice not in CHOICES:
		print("Elección inválida; abortando.")
		sys.exit(1)

	file_path = None
	ip = None
	if choice == "RetroVirtualMachine":
		while True:
			try:
				import questionary
				file_path = questionary.path(
					"Introduce el path del archivo para RetroVirtualMachine:"
				).ask()
			except Exception:
				file_path = input("Introduce el path del archivo para RetroVirtualMachine: ").strip()
			if not file_path:
				print("Path vacío, inténtalo de nuevo.")
				continue
			p = Path(file_path)
			# Aceptar .app (macOS) o archivo
			if p.is_file() or (p.is_dir() and p.suffix == ".app"):
				break
			print(f"El archivo o paquete '{file_path}' no existe o no es válido. Inténtalo de nuevo.")
	elif choice == "M4Board":
		while True:
			try:
				import questionary
				ip = questionary.text(
					"Introduce la IP para M4Board:"
				).ask()
			except Exception:
				ip = input("Introduce la IP para M4Board: ").strip()
			if ip and validar_ip(ip):
				break
			print("IP inválida, inténtalo de nuevo.")

	save_choice(choice, out_file, file_path, ip)


if __name__ == "__main__":
	main()

