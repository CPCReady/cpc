#!/bin/bash

# Script para probar compatibilidad con diferentes versiones de Python
# Requiere pyenv instalado

PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12" "3.13")

echo "Testing Python compatibility for CPCReady"
echo "=========================================="
echo ""

for version in "${PYTHON_VERSIONS[@]}"; do
    echo "Testing Python $version..."
    
    # Verificar si la versión está instalada
    if ! pyenv versions | grep -q "$version"; then
        echo "  ⚠️  Python $version not installed, skipping..."
        continue
    fi
    
    # Configurar versión de Python
    pyenv local "$version"
    
    # Intentar instalar dependencias
    if poetry env use "$version" 2>/dev/null && poetry install --no-interaction 2>/dev/null; then
        # Intentar ejecutar tests
        if poetry run pytest 2>/dev/null; then
            echo "  ✅ Python $version: PASSED"
        else
            echo "  ❌ Python $version: Tests FAILED"
        fi
    else
        echo "  ❌ Python $version: Installation FAILED"
    fi
    
    echo ""
done

# Restaurar versión original
pyenv local --unset

echo "Testing complete!"
