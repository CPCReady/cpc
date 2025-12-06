#!/bin/bash
# Script para generar un bloque de changelog bonito desde los commits entre main y HEAD

set -e

CHANGELOG_FILE="CHANGELOG.md"
BRANCH="main"

# Obtener los mensajes de commit entre main y HEAD
COMMITS=$(git log $BRANCH..HEAD --pretty=format:"%s" --reverse)

if [ -z "$COMMITS" ]; then
    echo "No hay commits nuevos entre $BRANCH y HEAD."
    exit 0
fi

# Formato bonito para changelog
CHANGELOG_BLOCK=""
CHANGELOG_BLOCK+="\n## Cambios en la nueva release ($(date +'%Y-%m-%d'))\n"
CHANGELOG_BLOCK+="\n"
CHANGELOG_BLOCK+="### Commits incluidos:\n"
CHANGELOG_BLOCK+="\n"

while IFS= read -r line; do
    # Ignorar commits vacíos
    if [ -n "$line" ]; then
        CHANGELOG_BLOCK+="- $line\n"
    fi
done <<< "$COMMITS"

# Mostrar el bloque generado
printf "%s" "$CHANGELOG_BLOCK"

# Si quieres añadirlo automáticamente al changelog, descomenta:
printf "%s" "$CHANGELOG_BLOCK" >> "$CHANGELOG_FILE"
echo "\nChangelog actualizado en $CHANGELOG_FILE"
