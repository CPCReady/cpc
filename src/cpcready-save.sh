#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

echo "Ejecutando la acción 'SAVE'..."
# Aquí va tu lógica para "guardar" algo.
# Por ejemplo, podrías recibir un nombre de archivo
# y copiarlo a un directorio específico.

# Los argumentos pasados desde 'cpc()' están disponibles aquí
if [ -z "$1" ]; then
  echo "Error: Se necesita un nombre de archivo para 'SAVE'."
  exit 1
fi

FILE_TO_SAVE="$1"
echo "PARAMETRO: $FILE_TO_SAVE"

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"