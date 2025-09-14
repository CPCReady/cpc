#!/bin/bash

# La variable $0 contiene la ruta del script actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CPCREADY_LIB_DIR="$DIR/../lib"

# Carga la librería de funciones comunes
source "$CPCREADY_LIB_DIR/cpcready-common.sh"

__get_version
__cpcready_echo_green "Available commands:"
echo""
__cpcready_echo_blue "  DISC:   " && echo "Crea disco virtual"
__cpcready_echo_blue "  DISC:   " 
__cpcready_echo_blue "  DISC:   " 
__cpcready_echo_blue "  DISC:   " 

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"

