# 📦 Sistema de Versiones cpcready

## 🎯 Resumen
Todos los comandos de cpcready comparten una **versión centralizada** definida en `cpcready/__init__.py`. Cambiar la versión en un solo lugar actualiza automáticamente todos los comandos.

## 🔧 Comandos con --version
Todos estos comandos soportan `--version`:

- ✅ `cpc --version` (CLI principal)
- ✅ `disc --version` 
- ✅ `drive --version`
- ✅ `A --version`
- ✅ `B --version` 
- ✅ `init --version`
- ✅ `catl --version`

## 🚀 Cómo cambiar la versión

### ✅ Método recomendado (automático):
```bash
# Cambiar la versión a 0.2.0
python3 sync_version.py 0.2.0

# Verificar que funciona
poetry run cpc --version
```

### ✅ Método manual:
```bash
# 1. Editar manualmente cpcready/__init__.py
# Cambiar: __version__ = "0.1.0" 
# Por:     __version__ = "0.2.0"

# 2. Sincronizar pyproject.toml
python3 sync_version.py
```

### ❌ NO hacer esto:
```bash
# ¡PELIGRO! Esto borra todo el contenido del archivo
echo '__version__ = "0.2.0"' > cpcready/__init__.py
```

## 🔍 Estructura del sistema

```
cpcready/
├── __init__.py              # ← Fuente única de verdad
├── utils/version.py         # ← Decoradores para --version
├── sync_version.py          # ← Script de sincronización  
└── pyproject.toml          # ← Se actualiza automáticamente
```

## 💡 Implementación técnica

- **Decoradores**: `@add_version_option` y `@add_version_option_to_group`
- **Callbacks**: Click callbacks con `is_eager=True` para procesar --version antes que otros argumentos
- **Importación**: Todos los módulos importan desde `cpcready.__version__`
- **Sincronización**: Script Python para mantener pyproject.toml actualizado

¡Un solo cambio, todas las versiones actualizadas! ✨