#!/bin/bash

# Copyright (C) 2025 David CH.F (destroyer)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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

# Preguntar si actualizar la fórmula de Homebrew
echo -e "${BLUE}🍺 Update Homebrew formula?${NC}"
read -p "Do you want to update the Homebrew formula? (y/N) " -n 1 -r
echo
UPDATE_FORMULA=false
if [[ $REPLY =~ ^[Yy]$ ]]; then
    UPDATE_FORMULA=true
fi
echo ""

# Verificar si el tag ya existe
TAG_EXISTS_LOCAL=$(git tag -l "v${NEW_VERSION}")
TAG_EXISTS_REMOTE=$(git ls-remote --tags origin "refs/tags/v${NEW_VERSION}" 2>/dev/null)

if [[ -n "$TAG_EXISTS_LOCAL" ]] || [[ -n "$TAG_EXISTS_REMOTE" ]]; then
    echo -e "${YELLOW}⚠️  Tag v${NEW_VERSION} already exists!${NC}"
    
    if [[ -n "$TAG_EXISTS_LOCAL" ]]; then
        echo -e "   ${YELLOW}• Found locally${NC}"
    fi
    
    if [[ -n "$TAG_EXISTS_REMOTE" ]]; then
        echo -e "   ${YELLOW}• Found on remote${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Do you want to:${NC}"
    echo -e "  ${GREEN}1)${NC} Delete existing tag and recreate"
    echo -e "  ${RED}2)${NC} Cancel"
    echo ""
    
    read -p "Choose [1-2]: " delete_choice
    
    if [[ $delete_choice != "1" ]]; then
        echo -e "${YELLOW}Cancelled${NC}"
        exit 0
    fi
    
    echo ""
    echo -e "${BLUE}🗑️  Deleting existing tags...${NC}"
    
    # Eliminar tag local si existe
    if [[ -n "$TAG_EXISTS_LOCAL" ]]; then
        git tag -d "v${NEW_VERSION}"
        echo -e "${GREEN}✅ Deleted local tag${NC}"
    fi
    
    # Eliminar tag remoto si existe
    if [[ -n "$TAG_EXISTS_REMOTE" ]]; then
        git push origin --delete "v${NEW_VERSION}" 2>/dev/null || true
        echo -e "${GREEN}✅ Deleted remote tag${NC}"
    fi
    
    echo ""
fi

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

# Verificar la versión actual antes del cambio
CURRENT_VERSION=$(grep -E "^__version__" cpcready/__init__.py | cut -d'"' -f2)

# Actualizar versión usando sync_version.py
if python3 Version/sync_version.py "$NEW_VERSION"; then
    echo -e "${GREEN}✅ Version files updated${NC}"
else
    echo -e "${RED}❌ Failed to update version files${NC}"
    exit 1
fi

# Verificar si realmente hubo cambios
if [[ -z $(git status -s cpcready/__init__.py pyproject.toml) ]]; then
    echo -e "${YELLOW}ℹ️  Version is already ${NEW_VERSION}, no changes needed${NC}"
    echo ""
    echo -e "${BLUE}🏷️  Checking if tag exists...${NC}"
    
    TAG_EXISTS_LOCAL=$(git tag -l "v${NEW_VERSION}")
    
    if [[ -z "$TAG_EXISTS_LOCAL" ]]; then
        # El tag no existe, solo crearlo sin commit
        echo -e "${BLUE}🏷️  Creating tag...${NC}"
        git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
        echo -e "${GREEN}✅ Tag v${NEW_VERSION} created${NC}"
        
        echo ""
        echo -e "${BLUE}📤 Pushing tag to remote...${NC}"
        git push origin "v${NEW_VERSION}"
        echo -e "${GREEN}✅ Pushed to remote${NC}"
    else
        echo -e "${YELLOW}ℹ️  Tag v${NEW_VERSION} already exists locally${NC}"
        echo -e "${YELLOW}Use the tag deletion option if you need to recreate it${NC}"
        exit 0
    fi
else
    # Hubo cambios, hacer commit normal
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
fi

# Actualizar fórmula de Homebrew si se solicitó
if [ "$UPDATE_FORMULA" = true ]; then
    echo ""
    echo -e "${BLUE}🍺 Updating Homebrew formula...${NC}"
    
    FORMULA_PATH="Installer/homebrew-cpcready/Formula/cpc.rb"
    
    if [ ! -f "$FORMULA_PATH" ]; then
        echo -e "${YELLOW}⚠️  Formula not found at ${FORMULA_PATH}${NC}"
    else
        # Calcular SHA256 del tarball
        echo -e "${BLUE}📥 Downloading release tarball...${NC}"
        TARBALL_URL="https://github.com/CPCReady/cpc/archive/refs/tags/v${NEW_VERSION}.tar.gz"
        SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | cut -d' ' -f1)
        
        if [ -z "$SHA256" ]; then
            echo -e "${RED}❌ Failed to calculate SHA256${NC}"
        else
            echo -e "${GREEN}✅ SHA256: ${SHA256}${NC}"
            
            # Actualizar URL y SHA256 en la fórmula
            sed -i.bak "s|url \"https://github.com/CPCReady/cpc/archive/refs/tags/v.*\.tar\.gz\"|url \"${TARBALL_URL}\"|" "$FORMULA_PATH"
            sed -i.bak "s|sha256 \".*\"|sha256 \"${SHA256}\"|" "$FORMULA_PATH"
            rm -f "${FORMULA_PATH}.bak"
            
            echo -e "${GREEN}✅ Formula updated${NC}"
            
            # Commit y push de la fórmula
            cd Installer/homebrew-cpcready
            
            if [[ -n $(git status -s Formula/cpc.rb) ]]; then
                git add Formula/cpc.rb
                git commit -m "chore: update cpc formula to v${NEW_VERSION}"
                git push
                echo -e "${GREEN}✅ Formula pushed to homebrew tap${NC}"
            else
                echo -e "${YELLOW}ℹ️  Formula already up to date${NC}"
            fi
            
            cd ../..
        fi
    fi
fi

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
