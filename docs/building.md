# 🔨 Building Standalone Executables

FossTree uses [PyInstaller](https://pyinstaller.org/) to create standalone executables that run without Python installed.

**Config files**: `fosstree.spec`, `.github/workflows/build.yml`

---

## Local Build

### Prerequisites

```bash
pip install pyinstaller>=6.0
```

### Build

```bash
pyinstaller fosstree.spec
```

Output is in `dist/FossTree/`:

```
dist/FossTree/
├── FossTree          # The executable
└── _internal/        # Bundled Python + all dependencies (~218 MB)
```

> ⚠️ The `FossTree` binary and `_internal/` folder must stay together.

### Build Modes

Edit `fosstree.spec` to toggle between modes:

| Mode | Setting | Size | Startup | Description |
|------|---------|------|---------|-------------|
| **One-dir** (default) | `ONE_FILE = False` | ~250 MB dir | Instant | Directory with executable + libraries |
| **One-file** | `ONE_FILE = True` | ~150 MB file | 3–5 sec | Self-extracting single executable |

### Platform Behavior

| Platform | Console | GUI | macOS .app |
|----------|---------|-----|------------|
| Linux | `console=True` — works from terminal | Launches GUI window | N/A |
| Windows | `console=False` — no terminal window | Double-click to launch | N/A |
| macOS | `console=False` — no terminal window | Double-click to launch | `FossTree.app` bundle created |

---

## Installing the Built Executable

### Linux

```bash
# Copy to a permanent location
cp -r dist/FossTree /opt/fosstree

# Create a symlink on PATH
sudo ln -s /opt/fosstree/FossTree /usr/local/bin/fosstree

# Or for current user only
cp -r dist/FossTree ~/Tools/fosstree
ln -sf ~/Tools/fosstree/FossTree ~/.local/bin/fosstree
```

### Windows

1. Copy the `dist/FossTree/` folder to `C:\Program Files\FossTree\`
2. Create a desktop shortcut to `FossTree.exe`
3. Optionally add to PATH via System Properties → Environment Variables

### macOS

1. Copy `dist/FossTree.app` to `/Applications/`
2. On first launch: right-click → Open (to bypass Gatekeeper)

---

## GitHub Actions (Automated Multi-Platform Builds)

The repository includes a CI workflow at `.github/workflows/build.yml` that:

1. Builds executables for **Linux, Windows, and macOS** in parallel
2. Tests the CLI on each platform
3. Creates a **GitHub Release** with downloadable archives when you push a version tag

### Triggering a Build

```bash
# Tag a version
git tag v0.1.0
git push --tags
```

This creates a release with:
- `FossTree-linux.tar.gz`
- `FossTree-windows.zip`
- `FossTree-macos.tar.gz`

### Manual Trigger

You can also trigger the workflow manually from the GitHub Actions tab (uses `workflow_dispatch`).

---

## Troubleshooting

### `ModuleNotFoundError` at runtime

A dependency was missed during bundling. Add it to `hiddenimports` in `fosstree.spec`:

```python
hiddenimports=[
    "matplotlib.backends.backend_qt5agg",
    "the_missing_module",
],
```

Then rebuild.

### `Failed to load Python shared library`

The `_internal/` folder is missing or was not copied alongside the `FossTree` binary. Always copy the **entire** `dist/FossTree/` directory.

### Qt platform plugin errors on Linux

Install the system Qt platform plugin:

```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

Or set the platform explicitly:

```bash
export QT_QPA_PLATFORM=xcb
./FossTree
```

### Large executable size

The ~218 MB size is dominated by:
- Qt5 shared libraries (~100 MB)
- numpy + matplotlib (~80 MB)
- Python interpreter (~20 MB)

To reduce, enable UPX compression (already enabled in the spec file) or use `ONE_FILE = True` mode.
