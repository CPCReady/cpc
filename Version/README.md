# 📦 Version Management & Release System

This directory contains tools for managing versions and creating releases for CPCReady.

## 📁 Files

- `sync_version.py` - Synchronizes version between `__init__.py` and `pyproject.toml`
- `create_release.sh` - Interactive script to create new releases
- `VERSION_SYSTEM.md` - Documentation about the version system

## 🚀 Creating a New Release

### Quick Start

```bash
cd Version
./create_release.sh
```

### What it does

1. **Checks current state**
   - Verifies you're on the right branch
   - Ensures no uncommitted changes
   - Reads the last git tag

2. **Interactive menu**
   - Shows current version (e.g., `v0.1.0`)
   - Offers version bump options:
     - **Major** (1.0.0) - Breaking changes
     - **Minor** (0.2.0) - New features
     - **Patch** (0.1.1) - Bug fixes
     - **Custom** - Specify any version

3. **Updates version files**
   - Runs `sync_version.py` to update:
     - `cpcready/__init__.py`
     - `pyproject.toml`

4. **Creates commit and tag**
   - Commits version changes
   - Creates annotated git tag (e.g., `v0.2.0`)

5. **Pushes to GitHub**
   - Pushes commit to current branch
   - Pushes tag to trigger GitHub Actions

6. **GitHub Actions takes over**
   - Workflow detects new tag
   - Builds package with Poetry
   - Creates GitHub Release
   - Uploads `.whl` and `.tar.gz` files

## 🛠️ Manual Version Update

If you only want to update the version without creating a release:

```bash
# Update to specific version
python3 sync_version.py 0.2.0

# Or manually edit cpcready/__init__.py and sync
# 1. Edit cpcready/__init__.py: __version__ = "0.2.0"
# 2. Run: python3 sync_version.py
```

## 📋 GitHub Actions Workflow

Located at: `.github/workflows/release.yml`

### Triggers

The workflow runs when you push a tag matching `v*` (e.g., `v0.1.0`, `v1.2.3`)

### Steps

1. **Checkout code** - Gets the repository
2. **Setup Python 3.13** - Installs Python
3. **Install Poetry** - Sets up Poetry package manager
4. **Cache dependencies** - Speeds up future runs
5. **Install dependencies** - Installs project dependencies
6. **Build package** - Creates wheel and source distribution
7. **Create GitHub Release** - Publishes release with artifacts

### Artifacts

Each release includes:
- `cpcready-X.Y.Z-py3-none-any.whl` - Python wheel (recommended)
- `cpcready-X.Y.Z.tar.gz` - Source distribution

## 🔍 Version Flow

```
┌─────────────────────┐
│  create_release.sh  │
└──────────┬──────────┘
           │
           ├─ Reads last tag from git
           ├─ User selects version bump
           ├─ Calls sync_version.py
           │
           ├─ sync_version.py updates:
           │  ├─ cpcready/__init__.py
           │  └─ pyproject.toml
           │
           ├─ Commits changes
           ├─ Creates tag (e.g., v0.2.0)
           └─ Pushes to GitHub
                    │
                    ▼
           ┌────────────────────┐
           │  GitHub Actions     │
           └────────────────────┘
                    │
                    ├─ Detects tag push
                    ├─ poetry build
                    └─ Creates Release
                           │
                           └─ Uploads artifacts
```

## 🎯 Best Practices

### Before Creating a Release

1. **Update CHANGELOG** (if you have one)
2. **Test thoroughly** - Run all tests
3. **Merge to main** - Ensure you're on the main branch
4. **Clean working directory** - Commit all changes

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)** - Breaking changes, incompatible API changes
- **Minor (0.X.0)** - New features, backwards compatible
- **Patch (0.0.X)** - Bug fixes, backwards compatible

### Example Workflow

```bash
# 1. Finish your feature
git add .
git commit -m "feat: add new awesome feature"
git push

# 2. Create release
cd Version
./create_release.sh
# Choose option 2 (Minor) for new feature
# Confirm: y

# 3. Wait for GitHub Actions
# Check: https://github.com/CPCReady/cpc2/actions

# 4. Release is live!
# https://github.com/CPCReady/cpc2/releases
```

## 🐛 Troubleshooting

### Script fails: "You have uncommitted changes"

```bash
# Commit your changes first
git add .
git commit -m "your message"
```

### Script fails: "No such file: cpcready/__init__.py"

```bash
# Run from Version directory
cd Version
./create_release.sh
```

### GitHub Actions fails

Check the workflow logs:
1. Go to GitHub repository
2. Click "Actions" tab
3. Click on the failed run
4. Review error logs

Common issues:
- Poetry dependency conflicts
- Python version mismatch
- Missing permissions

### Tag already exists

```bash
# Delete local tag
git tag -d v0.2.0

# Delete remote tag
git push origin :refs/tags/v0.2.0

# Try release again
./create_release.sh
```

## 📊 Monitoring Releases

### View all releases

```bash
git tag -l
```

### View release on GitHub

Visit: `https://github.com/CPCReady/cpc2/releases`

### Download release artifacts

```bash
# Example for v0.2.0
wget https://github.com/CPCReady/cpc2/releases/download/v0.2.0/cpcready-0.2.0-py3-none-any.whl
```

## 🔐 Permissions

The GitHub Actions workflow requires:
- `contents: write` - To create releases and upload files

This is configured in `.github/workflows/release.yml`

---

**Need help?** Check the main project README or open an issue on GitHub.
