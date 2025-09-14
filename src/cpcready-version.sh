#!/bin/bash

# La variable $0 contiene la ruta del script actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CPCREADY_LIB_DIR="$DIR/../lib"

# Carga la librería de funciones comunes
source "$CPCREADY_LIB_DIR/cpcready-common.sh"

__get_version
