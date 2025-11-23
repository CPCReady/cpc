#!/bin/bash
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


set -e

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   CPCReady Release Manager             ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en la rama correcta
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 Current branch: ${YELLOW}${CURRENT_BRANCH}${NC}"

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo -e "${YELLOW}⚠️  Warning: You're not on main/master branch${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar que no hay cambios sin commit
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}❌ You have uncommitted changes. Please commit or stash them first.${NC}"
    git status -s
    exit 1
fi

# Obtener el último tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo -e "${BLUE}🏷️  Last tag: ${GREEN}${LAST_TAG}${NC}"

# Extraer la versión sin 'v'
LAST_VERSION=${LAST_TAG#v}

# Separar major, minor, patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$LAST_VERSION"

echo ""
echo -e "${BLUE}📊 Current version breakdown:${NC}"
echo -e "   Major: ${GREEN}${MAJOR}${NC}"
echo -e "   Minor: ${GREEN}${MINOR}${NC}"
echo -e "   Patch: ${GREEN}${PATCH}${NC}"
echo ""

# Calcular las siguientes versiones
NEXT_MAJOR="$((MAJOR + 1)).0.0"
NEXT_MINOR="${MAJOR}.$((MINOR + 1)).0"
NEXT_PATCH="${MAJOR}.${MINOR}.$((PATCH + 1))"

# Menú de selección
echo -e "${BLUE}🎯 Select version bump:${NC}"
echo -e "  ${GREEN}1)${NC} Major   (${YELLOW}${NEXT_MAJOR}${NC}) - Breaking changes"
echo -e "  ${GREEN}2)${NC} Minor   (${YELLOW}${NEXT_MINOR}${NC}) - New features"
echo -e "  ${GREEN}3)${NC} Patch   (${YELLOW}${NEXT_PATCH}${NC}) - Bug fixes"
echo -e "  ${GREEN}4)${NC} Custom  - Specify your own version"
echo -e "  ${RED}5)${NC} Cancel"
echo ""

read -p "Choose [1-5]: " choice

case $choice in
    1)
        NEW_VERSION=$NEXT_MAJOR
        VERSION_TYPE="Major"
        ;;
    2)
        NEW_VERSION=$NEXT_MINOR
        VERSION_TYPE="Minor"
        ;;
    3)
        NEW_VERSION=$NEXT_PATCH
        VERSION_TYPE="Patch"
        ;;
    4)
        read -p "Enter custom version (x.y.z): " CUSTOM_VERSION
        if [[ ! $CUSTOM_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo -e "${RED}❌ Invalid version format. Use x.y.z${NC}"
            exit 1
        fi
        NEW_VERSION=$CUSTOM_VERSION
        VERSION_TYPE="Custom"
        ;;
    5)
        echo -e "${YELLOW}Cancelled${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📦 New version: ${YELLOW}v${NEW_VERSION}${NC} (${VERSION_TYPE})"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Proceed with release? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🔄 Updating version files...${NC}"

# Cambiar al directorio raíz del proyecto
cd "$(dirname "$0")/.."

# Actualizar versión usando sync_version.py
if python3 Version/sync_version.py "$NEW_VERSION"; then
    echo -e "${GREEN}✅ Version files updated${NC}"
else
    echo -e "${RED}❌ Failed to update version files${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📝 Creating commit...${NC}"

# Hacer commit de los cambios de versión
git add cpcready/__init__.py pyproject.toml
git commit -m "chore: bump version to ${NEW_VERSION}"

echo -e "${GREEN}✅ Commit created${NC}"

echo ""
echo -e "${BLUE}🏷️  Creating tag...${NC}"

# Crear tag
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo -e "${GREEN}✅ Tag v${NEW_VERSION} created${NC}"

echo ""
echo -e "${BLUE}📤 Pushing to remote...${NC}"

# Push commits y tags
git push origin "${CURRENT_BRANCH}"
git push origin "v${NEW_VERSION}"

echo -e "${GREEN}✅ Pushed to remote${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Release ${NEW_VERSION} completed!     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "   1. GitHub Actions will automatically build and create the release"
echo -e "   2. Check: ${YELLOW}https://github.com/CPCReady/cpc2/actions${NC}"
echo -e "   3. Release will be available at: ${YELLOW}https://github.com/CPCReady/cpc2/releases${NC}"
echo ""
