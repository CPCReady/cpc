#!/bin/bash

# Agrega el directorio 'bin' a tu PATH para que el comando 'cpc' funcione
export PATH="$CPCREADY_DIR/bin:$PATH"

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

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
      source "$CPCREADY_DIR/etc/logo.sh"
      source "$CPCREADY_DIR/src/cpcready-save.sh" "$@"
      ;;
    "run")
      source "$CPCREADY_DIR/etc/logo.sh"
      "$CPCREADY_DIR/src/cpcready-run.sh" "$@"
      ;;
    "disc")
      source "$CPCREADY_DIR/src/cpcready-disc.sh" "$@"
      ;;
    "version")
      source "$CPCREADY_DIR/etc/logo.sh"
      ;;
    "help")
      source "$CPCREADY_DIR/etc/logo.sh"
      source "$CPCREADY_DIR/src/cpcready-help.sh" "$@"
      ;;
    "commands")
      source "$CPCREADY_DIR/etc/logo.sh"
      source "$CPCREADY_DIR/src/cpcready-commands.sh" "$@"
      ;;  
    *)
      if [ -z "$cmd" ]; then
        # Si no se proporciona ningún comando, muestra la ayuda
        source "$CPCREADY_DIR/etc/logo.sh"
        source "$CPCREADY_DIR/src/cpcready-help.sh"
        return 0
      fi
      # Muestra un mensaje de error si el comando no es válido

      source "$CPCREADY_DIR/etc/logo.sh"
      echo
      __cpcready_echo_red "Error: Unknown command $cmd"
      "$CPCREADY_DIR/src/cpcready-help.sh"
      return 1
      ;;
  esac
}