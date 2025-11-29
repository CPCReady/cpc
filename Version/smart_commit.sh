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
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   CPCReady Smart Commit                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Verificar que se pasó un mensaje de commit
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: No commit message provided${NC}"
    echo -e "${YELLOW}Usage: ./smart_commit.sh \"your commit message\"${NC}"
    exit 1
fi

COMMIT_MSG="$1"

# Obtener el directorio actual
CURRENT_DIR=$(pwd)

# Determinar si estamos en el proyecto principal o en el submódulo docs
if [[ "$CURRENT_DIR" == *"/docs"* ]] || [[ "$(basename $(git rev-parse --show-toplevel 2>/dev/null))" == "docs" ]]; then
    # Estamos en el submódulo docs
    REPO_TYPE="docs"
    REPO_COLOR="${MAGENTA}"
    
    # Ir al directorio raíz del submódulo si no estamos ahí
    cd "$(git rev-parse --show-toplevel)"
    
else
    # Estamos en el proyecto principal
    REPO_TYPE="main"
    REPO_COLOR="${BLUE}"
    
    # Ir al directorio raíz del proyecto principal
    cd "$(git rev-parse --show-toplevel)"
fi

echo -e "${REPO_COLOR}📂 Repository: ${REPO_TYPE}${NC}"
echo -e "${BLUE}📍 Working directory: ${YELLOW}$(pwd)${NC}"
echo ""

# Verificar si hay cambios
if [[ -z $(git status -s) ]]; then
    echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
    exit 0
fi

echo -e "${BLUE}📋 Changes detected:${NC}"
git status -s
echo ""

# Hacer commit y push
echo -e "${BLUE}🔄 Adding all changes...${NC}"
git add .

echo -e "${BLUE}📝 Creating commit...${NC}"
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✅ Commit created${NC}"

echo ""
echo -e "${BLUE}📤 Pushing to remote...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
git push origin "$CURRENT_BRANCH"
echo -e "${GREEN}✅ Pushed to origin/${CURRENT_BRANCH}${NC}"

# Si estamos en docs, actualizar también el proyecto principal
if [ "$REPO_TYPE" == "docs" ]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔄 Updating main project submodule reference...${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Ir al proyecto principal
    cd ..
    
    # Verificar que estamos en el proyecto principal
    if [ -d ".git" ]; then
        echo -e "${BLUE}📍 Main project: ${YELLOW}$(pwd)${NC}"
        
        # Actualizar la referencia del submódulo
        git add docs
        
        if [[ -n $(git status -s docs) ]]; then
            git commit -m "chore: update docs submodule"
            echo -e "${GREEN}✅ Main project commit created${NC}"
            
            echo ""
            echo -e "${BLUE}📤 Pushing main project...${NC}"
            MAIN_BRANCH=$(git branch --show-current)
            git push origin "$MAIN_BRANCH"
            echo -e "${GREEN}✅ Pushed main project to origin/${MAIN_BRANCH}${NC}"
        else
            echo -e "${YELLOW}ℹ️  Submodule reference already up to date${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Warning: Could not find main project${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 All done!                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

if [ "$REPO_TYPE" == "docs" ]; then
    echo -e "${CYAN}📦 Summary:${NC}"
    echo -e "   ✅ Committed and pushed to ${MAGENTA}docs${NC} repository"
    echo -e "   ✅ Updated ${BLUE}main${NC} project submodule reference"
    echo -e "   ✅ Pushed ${BLUE}main${NC} project"
else
    echo -e "${CYAN}📦 Summary:${NC}"
    echo -e "   ✅ Committed and pushed to ${BLUE}main${NC} repository"
fi
echo ""
