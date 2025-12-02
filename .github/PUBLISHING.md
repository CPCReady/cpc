# Configuración de Workflows de Publicación

Este documento explica cómo configurar los workflows automáticos para publicar CPCReady en PyPI y Chocolatey.

## Workflows Disponibles

### 1. Publish to PyPI (`publish-pypi.yml`)

Publica automáticamente el paquete en PyPI cuando se crea un release.

**Triggers:**
- `release: published` - Se ejecuta automáticamente cuando publicas un release en GitHub
- `workflow_dispatch` - Ejecución manual desde la pestaña Actions

**Funcionalidades:**
- Construcción del paquete con Poetry
- Verificación del paquete con twine
- Publicación en PyPI o TestPyPI (para pruebas)
- Verificación de la publicación

### 2. Publish to Chocolatey (`publish-chocolatey.yml`)

Publica automáticamente el paquete en Chocolatey Community Repository.

**Triggers:**
- `release: published` - Se ejecuta automáticamente cuando publicas un release en GitHub
- `workflow_dispatch` - Ejecución manual desde la pestaña Actions

**Funcionalidades:**
- Actualización automática del paquete Chocolatey
- Construcción del .nupkg
- Prueba de instalación local antes de publicar
- Publicación en Chocolatey
- Commit y push de cambios al submodulo chocolatey-cpcready

## Configuración de Secretos

Para que los workflows funcionen, necesitas configurar los siguientes secretos en GitHub:

### Para PyPI

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions → New repository secret

**Secretos necesarios:**

#### `PYPI_API_TOKEN`
- **Descripción:** Token de API de PyPI para publicar paquetes
- **Obtención:**
  2. Ve a Account settings → API tokens
  3. Click en "Add API token"
  4. Nombre: `CPCReady GitHub Actions`
  5. Scope: `Project: cpcready` (o "Entire account" si prefieres)
  6. Copia el token (comienza con `pypi-`)
  
#### `TEST_PYPI_API_TOKEN` (Opcional, para pruebas)
- **Descripción:** Token de API de TestPyPI para probar publicaciones
- **Obtención:**
  1. Inicia sesión en https://test.pypi.org/
  2. Sigue los mismos pasos que para PyPI
  3. Copia el token (comienza con `pypi-`)

### Para Chocolatey

#### `CHOCOLATEY_API_KEY`

- **Descripción:** API Key de Chocolatey Community Repository
- **Obtención:**
  1. Inicia sesión en <https://community.chocolatey.org/>
  2. Ve a tu perfil → Account → API Key
  3. Si no tienes una, click en "Generate new API Key"
  4. Copia la key generada

#### `PAT_GITHUB`

- **Descripción:** Personal Access Token para actualizar la fórmula de Homebrew
- **Obtención:**
  1. Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Click en "Generate new token (classic)"
  3. Nombre: `CPCReady Homebrew Formula Update`
  4. Permisos necesarios:
     - ✅ `repo` (full control)
     - ✅ `workflow`
  5. Genera el token y **cópialo** (solo se muestra una vez)
  6. Ve a tu repositorio `CPCReady/cpc` → Settings → Secrets and variables → Actions
  7. Click "New repository secret"
  8. Name: `PAT_GITHUB`
  9. Value: pega el token
  10. Click "Add secret"

## Configuración de Environments (Opcional pero recomendado)

Para mayor seguridad, puedes crear environments en GitHub:

### PyPI Environment

1. Settings → Environments → New environment
2. Nombre: `pypi`
3. Configura:
   - **Deployment branches:** Only selected branches → `main`
   - **Required reviewers:** (opcional) Añade revisores
4. Añade el secret `PYPI_API_TOKEN` al environment

### TestPyPI Environment

1. Settings → Environments → New environment
2. Nombre: `testpypi`
3. Configura igual que PyPI
4. Añade el secret `TEST_PYPI_API_TOKEN` al environment

## Uso de los Workflows

### Publicación Automática

Cuando crees un release en GitHub (usando `./Version/create_release.sh` o manualmente):

1. El workflow `publish-pypi.yml` se ejecutará automáticamente
2. El workflow `publish-chocolatey.yml` se ejecutará automáticamente
3. Ambos publicarán la nueva versión en sus respectivos repositorios

### Publicación Manual

#### PyPI

1. Ve a Actions → Publish to PyPI → Run workflow
2. Selecciona la rama `main`
3. (Opcional) Marca "Publish to TestPyPI" para probar primero
4. Click en "Run workflow"

#### Chocolatey

1. Ve a Actions → Publish to Chocolatey → Run workflow
2. Selecciona la rama `main`
3. Introduce la versión a publicar (ej: `1.1.0`)
4. Click en "Run workflow"

## Verificación de Publicaciones

### PyPI
```bash
# Espera unos minutos después de la publicación
pip install --upgrade cpcready

# Verifica la versión
cpc --version
```

### Chocolatey
```powershell
# Espera 30-60 minutos (proceso de moderación)
choco install cpc

# Verifica la versión
cpc --version
```

## Troubleshooting

### Error: "Invalid API token"
- Verifica que el token esté correctamente copiado (sin espacios)
- Verifica que el token tenga los permisos correctos
- Regenera el token si es necesario

### Error: "Package already exists"
- No puedes sobrescribir versiones ya publicadas
- Incrementa el número de versión en `pyproject.toml`
- Crea un nuevo release con la nueva versión

### Chocolatey: "Package validation failed"
- Revisa los logs del workflow
- Verifica que el .nuspec tenga todos los campos requeridos
- Asegúrate de que las URLs sean accesibles

### Chocolatey: "Moderation review pending"
- Es normal, los paquetes nuevos requieren aprobación manual
- Puede tomar 24-48 horas
- Las actualizaciones de paquetes existentes son automáticas después de la primera aprobación

## Checklist de Primera Configuración

- [ ] Crear cuenta en PyPI
- [ ] Generar API token de PyPI
- [ ] Añadir `PYPI_API_TOKEN` a GitHub Secrets
- [ ] (Opcional) Crear cuenta en TestPyPI
- [ ] (Opcional) Añadir `TEST_PYPI_API_TOKEN` a GitHub Secrets
- [ ] Crear cuenta en Chocolatey Community
- [ ] Generar API Key de Chocolatey
- [ ] Añadir `CHOCOLATEY_API_KEY` a GitHub Secrets
- [ ] Probar publicación manual en TestPyPI
- [ ] Verificar que los workflows se ejecutan correctamente

## Referencias

- [PyPI Documentation](https://pypi.org/help/)
- [Poetry Publishing](https://python-poetry.org/docs/cli/#publish)
- [Chocolatey Package Creation](https://docs.chocolatey.org/en-us/create/create-packages)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
