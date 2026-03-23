# GUI Application — `fosstree.views.gui`

PyQt5 desktop application for fossil calibration annotation.

**Source**: `fosstree/views/gui.py`

---

## Launching

```bash
fosstree              # default (no arguments)
fosstree gui          # explicit
python -m fosstree    # module invocation
```

---

## Workflow

### Phase 1: Load Tree File

- Browse for `.tree`, `.nwk`, `.newick`, `.tre` files
- Supports plain Newick and MCMCTree format (auto-detected with info dialog)

### Phase 2: Tree Info

- Taxa count, calibration count, max depth
- Calibration table with columns: `#`, `Clade Name`, `Type`, `Calibration`, `# Taxa`

### Phase 3: BEAST2 XML

- Configure tree reference and distribution ID start
- Generate, save, or copy MRCAPrior XML blocks

### Phase 4: Visualization

Interactive tree rendering with calibration editing.

---

## Node Interaction

| Mouse Action | Effect |
|-------------|--------|
| **Hover** | Tooltip: node ID, calibration, tip distance (if branch lengths enabled), descendant taxa |
| **Click** | Info panel: full descendant taxa list, calibration details, tip distance |
| **Double-click** | Opens calibration dialog |

---

## Calibration Dialog

Double-click any internal node to open. Features:

- **Node info** with descendant taxa count and tip distance (when branch lengths enabled)
- **Type selector** dropdown: B, L, U, G, SN, ST, S2N
- **Input field** for MCMCTree format string with dynamic help text per type
- **Apply** validates and sets the calibration
- **Remove Calibration** clears the node's calibration

After applying or removing, the tree re-renders and all tabs refresh.

---

## Visualization Options

| Option | Description | Default |
|--------|-------------|---------|
| Theme | `light` or `dark` | light |
| Font (leaves) | Taxon label font size | 11 |
| Font (labels) | Calibration label font size | 8 |
| Branch lengths | Toggle phylogram mode (scaled branches, tip distances, branch length labels) | off |
| Export DPI | Resolution for exported figures | 300 |

---

## Export

| Button | Output |
|--------|--------|
| **Export Figure...** | PDF, SVG, or PNG |
| **Export MCMCTree Newick...** | Tree with all calibrations as `.tree` file |

---

## Controls

| Control | Action |
|---------|--------|
| Ctrl + scroll | Zoom (0.2x - 5x) |
| Scroll | Pan |
| Fit to Window | Auto-scale to viewport |
| 100% | Reset zoom |
