#!/bin/bash

# La variable $0 contiene la ruta del script actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CPCREADY_LIB_DIR="$DIR/../lib"

# Carga la librería de funciones comunes
source "$CPCREADY_LIB_DIR/cpcready-common.sh"


echo "Ejecutando la acción 'DISC'..."
# Aquí va tu lógica para "guardar" algo.
# Por ejemplo, podrías recibir un nombre de archivo
# y copiarlo a un directorio específico.

# Los argumentos pasados desde 'cpc()' están disponibles aquí
if [ -z "$1" ]; then
  echo "Error: Se necesita un nombre de archivo para 'DISC'."
  exit 1
fi

FILE_TO_SAVE="$1"
echo "PARAMETRO: $FILE_TO_SAVE"
__cpcready_echo_red "Este es un mensaje de error"

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"