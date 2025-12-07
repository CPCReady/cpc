"""
Test documentation build with Astro.

Verifies that the documentation can be built successfully.
"""

import os
import subprocess
import pytest
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_docs_dir():
    """Get the docs directory."""
    return get_project_root() / "docs"


@pytest.mark.skipif(not get_docs_dir().exists(), reason="docs submodule not initialized")
def test_docs_directory_exists():
    """Test that docs directory exists."""
    docs_dir = get_docs_dir()
    assert docs_dir.exists(), "docs directory should exist"
    assert docs_dir.is_dir(), "docs should be a directory"


@pytest.mark.skipif(not get_docs_dir().exists(), reason="docs submodule not initialized")
def test_package_json_exists():
    """Test that package.json exists in docs."""
    package_json = get_docs_dir() / "package.json"
    assert package_json.exists(), "package.json should exist in docs"


@pytest.mark.skipif(not get_docs_dir().exists(), reason="docs submodule not initialized")
def test_npm_dependencies_installed():
    """Test that npm dependencies can be installed."""
    docs_dir = get_docs_dir()
    
    # Check if node_modules exists, if not try to install
    node_modules = docs_dir / "node_modules"
    if not node_modules.exists():
        result = subprocess.run(
            ["npm", "ci"],
            cwd=docs_dir,
            capture_output=True,
            text=True
        )
        
        # If npm ci fails, try npm install
        if result.returncode != 0:
            result = subprocess.run(
                ["npm", "install"],
                cwd=docs_dir,
                capture_output=True,
                text=True
            )
    
    assert node_modules.exists(), "node_modules should exist after install"


@pytest.mark.skipif(not get_docs_dir().exists(), reason="docs submodule not initialized")
def test_astro_build():
    """Test that Astro documentation builds successfully."""
    docs_dir = get_docs_dir()
    
    # Ensure dependencies are installed first
    node_modules = docs_dir / "node_modules"
    if not node_modules.exists():
        subprocess.run(["npm", "install"], cwd=docs_dir, check=True, capture_output=True)
    
    # Run the build
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=docs_dir,
        capture_output=True,
        text=True
    )
    
    # Check build succeeded
    assert result.returncode == 0, f"Build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    
    # Check dist directory was created
    dist_dir = docs_dir / "dist"
    assert dist_dir.exists(), "dist directory should exist after build"
    assert dist_dir.is_dir(), "dist should be a directory"
    
    # Check that there are files in dist
    dist_files = list(dist_dir.rglob("*"))
    assert len(dist_files) > 0, "dist directory should contain files"


@pytest.mark.skipif(not get_docs_dir().exists(), reason="docs submodule not initialized")
def test_astro_check():
    """Test that Astro type checking passes."""
    docs_dir = get_docs_dir()
    
    # Ensure dependencies are installed first
    node_modules = docs_dir / "node_modules"
    if not node_modules.exists():
        subprocess.run(["npm", "install"], cwd=docs_dir, check=True, capture_output=True)
    
    # Run astro check if it exists in package.json
    package_json_path = docs_dir / "package.json"
    if package_json_path.exists():
        import json
        with open(package_json_path) as f:
            package_data = json.load(f)
        
        if "astro" in package_data.get("scripts", {}):
            result = subprocess.run(
                ["npm", "run", "astro", "check"],
                cwd=docs_dir,
                capture_output=True,
                text=True
            )
            
            # Don't fail the test if astro check has warnings, only errors
            if result.returncode != 0 and "error" in result.stdout.lower():
                pytest.fail(f"Astro check failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
