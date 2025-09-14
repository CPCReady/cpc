#!/bin/bash

# Función para imprimir texto en color rojo.
# Uso: __cpcready_echo_red "Este es un mensaje de error"
function __cpcready_echo_red() {
  local text="$1"
  echo -e "\033[0;31m${text}\033[0m"
}

# Función para mostrar texto en color amarillo
# Uso: __cpcready_echo_yellow "Este es un mensaje de advertencia"
function __cpcready_echo_yellow() {
  local text="$1"
  echo -e "\033[0;33m${text}\033[0m"
}

# Función para mostrar texto en color azul
# Uso: __cpcready_echo_blue "Este es un mensaje informativo"
function __cpcready_echo_blue() {
  local text="$1"
  echo -e "\033[0;34m${text}\033[0m"
}

# Función para mostrar texto en color verde
# Uso: __cpcready_echo_green "Este es un mensaje de éxito"
function __cpcready_echo_green() {
  local text="$1"
  echo -e "\033[0;32m${text}\033[0m"
}

# Función para mostrar texto en color azul
# Uso: __cpcready_echo_blue "Este es un mensaje informativo"
function __cpcready_echo_command_help() {
  local text="$1"
  local description="$2"
  echo -e "\033[0;34m${text}\033[0m${description}"
}

# Función para mostrar un mensaje de error y salir del script.
# Uso: __error_exit "Mensaje de error"
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

# funcion que devuelve la version del software
# Uso: __get_version
function __get_version(){
  version=$(cat $CPCREADY_DIR/var/VERSION)
  echo ""
  __cpcready_echo_yellow "CPCReady: $version"
  echo ""
}