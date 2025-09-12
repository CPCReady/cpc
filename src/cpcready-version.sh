#!/bin/bash

function __cpc_version() {
    local version=$(cat $CPCREADY_DIR/var/VERSION)
	echo ""
	__sdkman_echo_yellow "SDKMAN $version"
}

function __error_exit() {
  echo "Error: $1" >&2
  exit 1
}

# Función para verificar si un archivo o directorio existe.
# Uso: if file_exists "mi_archivo.txt"; then ...
function __file_exists() {
  local path="$1"
  if [[ -e "$path" ]]; then
    return 0  # Verdadero (existe)
  else
    return 1  # Falso (no existe)
  fi
}

