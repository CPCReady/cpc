# Copyright 2025 David CH.F (destroyer)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

import os
import re
import yaml
import jsonschema
from pathlib import Path
from cpcready.utils import console

# Regex para variables de entorno: ${VAR} o ${VAR:default}
ENV_VAR_PATTERN = re.compile(r"\$\{([^}:\s]+)(?::([^}]*))?\}")


def _expand_env_vars(value):
    """Expande variables de entorno dentro de un string."""
    def replacer(match):
        var_name, default = match.groups()
        return os.getenv(var_name, default or "")
    if isinstance(value, str):
        return ENV_VAR_PATTERN.sub(replacer, value)
    return value


def _expand_env_recursive(data):
    """Expande variables de entorno recursivamente en dicts y listas."""
    if isinstance(data, dict):
        return {k: _expand_env_recursive(_expand_env_vars(v)) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_env_recursive(_expand_env_vars(v)) for v in data]
    else:
        return _expand_env_vars(data)


def load_yaml(path, schema=None):
    """
    Carga un archivo YAML y valida su estructura si se pasa un schema.
    Expande variables de entorno (${VAR} o ${VAR:default}).
    """
    path = Path(path)
    if not path.exists():
        console.warn(f"[WARN] No se encontró {path}, devolviendo configuración vacía.")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
            data = _expand_env_recursive(data)
            console.debug(f"[DEBUG] Config cargada desde {path} con variables expandidas.")

            if schema:
                validate_yaml(data, schema)

            return data
        except yaml.YAMLError as e:
            console.error(f"[ERROR] Error al leer YAML: {e}")
            return {}


def save_yaml(path, data):
    """Guarda un diccionario como archivo YAML."""
    path = Path(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        console.ok(f"[OK] Config guardada en {path}")
    except Exception as e:
        console.error(f"[ERROR] No se pudo guardar {path}: {e}")
        raise


def update_yaml(path, updates, schema=None):
    """
    Actualiza un YAML existente con nuevos valores.
    Si hay un esquema, valida antes de guardar.
    """
    config = load_yaml(path)
    config.update(updates)

    if schema:
        validate_yaml(config, schema)

    save_yaml(path, config)
    console.info(f"[INFO] {path} actualizado correctamente.")
    return config


def validate_yaml(data, schema):
    """Valida un YAML contra un esquema JSON Schema."""
    try:
        jsonschema.validate(instance=data, schema=schema)
        console.ok("[OK] Configuración válida según el esquema.")
    except jsonschema.ValidationError as e:
        console.error(f"[ERROR] Configuración inválida: {e.message}")
        raise
