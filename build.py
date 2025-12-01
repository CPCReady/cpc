import os
import shutil
import subprocess
import sys
import platform
import hashlib
from pathlib import Path

# Comandos soportados
COMMANDS = [
    "cpc", "disc", "drive", "catcpc", "A", "B", "user", "save", "era", "list"
]

# Recursos
ICON_WIN = Path("resources/cpcready.ico")
ICON_MAC = Path("resources/cpcready.icns")
EULA_FILE = Path("resources/EULA.txt")
SPLASH_IMAGE = Path("resources/splash.bmp")  # Windows

# --------------------------------------------------------------------
# 1. COMPILAR BINARIOS
# --------------------------------------------------------------------
def build_binaries():
    build_root = Path("build/all")
    bin_dir = build_root / "bin"
    libs_dir = build_root / "libs"

    if build_root.exists():
        shutil.rmtree(build_root)
    bin_dir.mkdir(parents=True)
    libs_dir.mkdir(parents=True)

    project_root = Path(__file__).resolve().parent
    print(f"\n🔨 Compilando cpc (standalone)")
    module = project_root / "cpcready/cli.py"
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--follow-imports",
        "--remove-output",
        "--assume-yes-for-downloads",
        "--python-flag=-OO",
        "--output-dir=build/tmp",
        str(module)
    ]
    subprocess.run(cmd, check=True)
    dist_folder = Path("build/tmp") / "cli.dist"
    # Mover el binario principal
    for f in dist_folder.iterdir():
        if f.is_file() and f.name.startswith("cli"):
            shutil.move(f, bin_dir / "cpc.bin")
    # Mover las librerías
    for f in dist_folder.iterdir():
        shutil.move(str(f), libs_dir / f.name)
    shutil.rmtree("build/tmp")

    # Crear alias/symlinks para los comandos
    for cmd_name in COMMANDS:
        target = bin_dir / cmd_name
        try:
            if platform.system() == "Windows":
                # Crear .bat para Windows
                with open(str(target) + ".bat", "w") as bat:
                    bat.write(f'@echo off\n"%~dp0cpc.bin" %*\n')
            else:
                # Crear symlink para Unix
                if not target.exists():
                    os.symlink("cpc.bin", target)
        except Exception as e:
            print(f"No se pudo crear alias para {cmd_name}: {e}")
    print("\n✔ Binario principal y alias/symlinks creados en build/all/bin/")

# --------------------------------------------------------------------
# 2. HASH SHA256
# --------------------------------------------------------------------
def hash_binaries():
    print("🔒 Calculando hashes SHA256 de binarios...")
    bin_dir = Path("build/all/bin")
    for f in bin_dir.iterdir():
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        print(f"{f.name}: {h}")

# --------------------------------------------------------------------
# 3. INSTALADOR WINDOWS PROFESIONAL
# --------------------------------------------------------------------
def _installer_windows():
    if platform.system() != "Windows":
        return
    nsis_dir = Path("dist/installer/windows")
    nsis_dir.mkdir(parents=True, exist_ok=True)
    installer_file = nsis_dir / "cpcready_setup.exe"
    script_file = nsis_dir / "cpcready.nsi"

    with open(script_file, "w") as f:
        f.write(rf'''
!include MUI2.nsh
!define MUI_ICON "{ICON_WIN}"
!define MUI_LAUNCHER_ICON "{ICON_WIN}"
!define MUI_HEADERIMAGE_BITMAP "{SPLASH_IMAGE}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{EULA_FILE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

OutFile "{installer_file}"
InstallDir "$PROGRAMFILES\CPReady"
RequestExecutionLevel admin

Section "Install"
    SetOutPath "$INSTDIR\bin"
    File /r "build\all\bin\*.*"
    SetOutPath "$INSTDIR\libs"
    File /r "build\all\libs\*.*"

''')
        for name in COMMANDS:
            f.write(f'    CreateShortCut "$DESKTOP\\{name}.lnk" "$INSTDIR\\bin\\cpc.bin"\n')
        f.write(r'''
    ; Añadir al PATH
    ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
    StrCpy $0 "$0;$INSTDIR\bin"
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\bin\*.*"
    Delete "$INSTDIR\libs\*.*"
    RMDir "$INSTDIR\bin"
    RMDir "$INSTDIR\libs"
    RMDir "$INSTDIR"
SectionEnd
''')
    subprocess.run(["makensis", str(script_file)], check=True)

    # Firma digital opcional (requiere certificado)
    # subprocess.run(["signtool", "sign", "/f", "cert.pfx", "/p", "pass", str(installer_file)])
    print(f"🖥 Instalador Windows creado: {installer_file}")

# --------------------------------------------------------------------
# 4. INSTALADOR LINUX (.deb)
# --------------------------------------------------------------------
def _installer_linux():
    if platform.system() != "Linux":
        return
    root = Path("dist/installer/linux/cpcready_pkg")
    shutil.rmtree(root, ignore_errors=True)
    bin_dir = root / "usr/bin"
    lib_dir = root / "usr/lib/cpcready"
    debian = root / "DEBIAN"
    bin_dir.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    debian.mkdir(parents=True)
    for exe in Path("build/all/bin").iterdir():
        shutil.copy(exe, bin_dir / exe.name)
    for f in Path("build/all/libs").iterdir():
        dest = lib_dir / f.name
        if f.is_dir():
            shutil.copytree(f, dest, dirs_exist_ok=True)
        else:
            shutil.copy(f, dest)
    version = globals().get("VERSION", "1.0")
    (debian / "control").write_text(f"""
Package: cpcready
Version: {version}
Architecture: amd64
Maintainer: Unknown
Description: CPReady Suite
""")
    (debian / "postinst").write_text("""#!/bin/bash
chmod +x /usr/bin/*
""")
    subprocess.run(["chmod", "+x", str(debian / "postinst")])
    subprocess.run(["dpkg-deb", "--build", root, "dist/installer/linux/cpcready.deb"], check=True)
    print("🐧 Instalador Linux creado: dist/installer/linux/cpcready.deb")

# --------------------------------------------------------------------
# 5. INSTALADOR macOS (.pkg)
# --------------------------------------------------------------------
def _installer_macos():
    if platform.system() != "Darwin":
        return
    pkg_root = Path("dist/installer/macos/root")
    shutil.rmtree(pkg_root, ignore_errors=True)
    bin_dir = pkg_root / "usr/local/bin"
    lib_dir = pkg_root / "usr/local/lib/cpcready"
    bin_dir.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    for exe in Path("build/all/bin").iterdir():
        shutil.copy(exe, bin_dir / exe.name)
    for f in Path("build/all/libs").iterdir():
        dest = lib_dir / f.name
        if f.is_dir():
            shutil.copytree(f, dest, dirs_exist_ok=True)
        else:
            shutil.copy(f, dest)
    version = globals().get("VERSION", "1.0")
    import platform
    arch = platform.machine()
    pkgfile = Path(f"dist/installer/macos/cpcready-{version}-{arch}.pkg")
    subprocess.run([
        "pkgbuild",
        "--root", str(pkg_root),
        "--identifier", "com.cpcready",
        "--version", version,
        "--install-location", "/",
        str(pkgfile)
    ], check=True)
    # Firma digital opcional: subprocess.run(["codesign", "--sign", "DeveloperID", str(pkgfile)])
    print(f"🍏 Instalador macOS creado: {pkgfile}")


# --------------------------------------------------------------------
# 6. UTILIDAD: LEER VERSION
# --------------------------------------------------------------------
def get_version():
    pyproject = Path("pyproject.toml")
    for line in pyproject.read_text().splitlines():
        if line.strip().startswith("version ="):
            return line.split("=")[1].strip().replace('"','')
    return "1.0"

# --------------------------------------------------------------------
# 7. COMANDO GENERAL
# --------------------------------------------------------------------
def build_installer():
    print("\n📦 Creando instalador profesional único...")
    build_binaries()
    version = get_version()
    global VERSION
    VERSION = version
    _installer_windows()
    _installer_linux()
    _installer_macos()
    hash_binaries()
    print(f"\n🎉 Instalador único finalizado para todas las plataformas. Versión: {version}")

# --------------------------------------------------------------------
# 8. MAIN
# --------------------------------------------------------------------
if __name__ == "__main__":
    build_installer()