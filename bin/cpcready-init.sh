#!/bin/bash

# Define la ruta base de tu proyecto
CPCREADY_DIR="$HOME/.cpcready"

# Agrega el directorio 'bin' a tu PATH para que el comando 'cpc' funcione
export PATH="$CPCREADY_DIR/bin:$PATH"

# La variable $0 contiene la ruta del script actual
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CPCREADY_LIB_DIR="$DIR/../lib"

# Carga la librería de funciones comunes
source "$CPCREADY_LIB_DIR/cpcready-common.sh"

# Define una función principal para el comando 'cpc'
cpc() {
  # Obtiene el primer argumento (la opción: save, run, disc)
  local cmd="$1"
  # Remueve el primer argumento para pasar el resto
  shift

  # Usa una estructura 'case' para redirigir a los scripts correctos
  case "$cmd" in
    "save")
      # Ejecuta el script de 'save' y le pasa el resto de los argumentos
      "$CPCREADY_DIR/src/cpcready-save.sh" "$@"
      ;;
    "run")
      "$CPCREADY_DIR/src/cpcready-run.sh" "$@"
      ;;
    "disc")
      "$CPCREADY_DIR/src/cpcready-disc.sh" "$@"
      ;;
    "version")
      "$CPCREADY_DIR/src/cpcready-version.sh" "$@"
      ;;


    *)
      # Muestra un mensaje de error si el comando no es válido
      echo "Comando no reconocido: $cmd"
      echo "Uso: cpc [save|run|disc|version]"
      return 1
      ;;
  esac
}