import psutil
import subprocess
import os
import sys
import time

# Nombres posibles del ejecutable
NOMBRES_OBJETIVO = [
    "Retro Virtual Machine",
    "retrovirtualmachine",
    "RetroVirtualMachine.exe",
    "retrovirtualmachine.exe"
]

def matar_rvm():
    print("Buscando instancias previas de RetroVirtualMachine...")

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            nombre = proc.info["name"] or ""
            ruta = proc.info["exe"] or ""
            cmd = " ".join(proc.info["cmdline"] or [])

            if any(t.lower() in nombre.lower() for t in NOMBRES_OBJETIVO) or \
               any(t.lower() in ruta.lower() for t in NOMBRES_OBJETIVO) or \
               any(t.lower() in cmd.lower() for t in NOMBRES_OBJETIVO):

                print(f"Matando: PID {proc.pid} ({nombre})")
                proc.kill()
                proc.wait()

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def lanzar_nueva_instancia(ruta_ejecutable, parametros):
    print("Lanzando RetroVirtualMachine con parámetros...")

    comando = [ruta_ejecutable] + parametros

    if sys.platform.startswith("win"):
        subprocess.Popen(
            comando, 
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
    else:
        subprocess.Popen(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    print("Nueva instancia ejecutada.")


if __name__ == "__main__":

    # ❗ CAMBIA ESTA RUTA SEGÚN TU SISTEMA
    ruta_rvm = r"/Applications/Retro Virtual Machine 2.app/Contents/MacOS/Retro Virtual Machine 2"        # Linux / macOS
    # ruta_rvm = r"C:\Ruta\RetroVirtualMachine.exe"  # Windows

    # ❗ ESPECIFICA AQUÍ LOS PARÁMETROS QUE QUIERAS PASAR
    parametros = [
        "-b=cpc664"    ]

    matar_rvm()
    time.sleep(0.5)  # asegurar cierre
    lanzar_nueva_instancia(ruta_rvm, parametros)