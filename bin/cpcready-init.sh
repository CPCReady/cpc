#!/bin/bash

# Agrega el directorio 'bin' a tu PATH para que el comando 'cpc' funcione
export PATH="$CPCREADY_DIR/bin:$PATH"

# Carga la librería de funciones comunes
source ="$CPCREADY_DIR/lib/cpcready-common.sh"

# Define una función principal para el comando 'cpc'
cpc() {
  # Obtiene el primer argumento (la opción: save, run, disc)
  local cmd="$1"
    # Remueve el primer argumento para pasar el resto solo si hay argumentos
    if [ "$#" -gt 0 ]; then
      shift
    fi

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
    "help")
      "$CPCREADY_DIR/src/cpcready-help.sh" "$@"
      ;;
    *)
      # Muestra un mensaje de error si el comando no es válido
      echo "Comando no reconocido: $cmd"
      echo "Uso: cpc [save|run|disc|version]s"
      return 1
      ;;
  esac
}