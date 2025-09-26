#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

echo""

echo "Usage: cpc [command] [args...]"

source "$CPCREADY_DIR/src/cpcready-commands.sh"
echo "" 
echo "For more details on a specific command, use: cpc [command] --help"
echo ""
echo "Example: cpc save myfile.bas"
echo ""

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"

