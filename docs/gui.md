# 🖥️ GUI Application — `fosstree.views.gui`

A PyQt5 desktop application providing a complete visual workflow for fossil calibration annotation.

**Source**: `fosstree/views/gui.py`

---

## Launching

```bash
fosstree              # GUI is the default (no arguments)
fosstree gui          # Explicit
python -m fosstree    # Module invocation
```

---

## Workflow Phases

### Phase 1: Load Tree File

- Click **Browse...** to open a file dialog
- Supports `.tree`, `.nwk`, `.newick`, `.tre` extensions
- Click **Load** to parse the tree
- On success, all tabs become enabled and the status bar updates

### Phase 2: Tree Info

- Displays taxa count, calibration count, and max tree depth
- Sortable calibration table with columns:
  - `#` — calibration index
  - `Clade Name` — auto-generated from first/last descendant taxa
  - `Lower` / `Upper` — age bounds
  - `# Taxa` — number of descendant taxa

### Phase 3: BEAST2 XML

- **Tree Ref** — BEAST2 tree ID reference (e.g., `@Tree.t:alignment`)
- **Uniform ID Start** — starting index for Uniform distribution IDs
- **Generate XML** — produces the XML in the text area
- **Save XML to File...** — writes to a `.xml` file
- **Copy to Clipboard** — copies XML text for pasting into BEAST2

### Phase 4: Visualization

The main interactive view. See sections below for details.

---

## Interactive Tree Visualization

### Controls

| Control | Action |
|---------|--------|
| **Ctrl + scroll wheel** | Zoom in/out (0.2x – 5x) |
| **Scroll wheel** | Pan vertically |
| **Fit to Window** button | Scale tree to fit visible area |
| **100%** button | Reset zoom to native size |

### Node Interaction

| Mouse Action | Effect |
|-------------|--------|
| **Hover** over internal node | Tooltip shows node ID, calibration status, and descendant taxa |
| **Single click** internal node | Info panel below canvas shows full list of descendant taxa |
| **Double-click** internal node | Opens calibration dialog (see below) |

### Calibration Dialog

Opened by double-clicking any internal node. Features:

- **Node info display** — shows node ID and descendant taxa
- **Current calibration** — displays existing calibration if present
- **Input field** — enter calibration in MCMCTree format:
  - Full: `B(5.29,6.361,0.001,0.025)`
  - Short: `B(5.29,6.361)` (uses default p_lower=0.001, p_upper=0.025)
- **Apply** — validates and applies the calibration
- **Remove Calibration** — removes existing calibration from the node
- **Cancel** — closes without changes

After applying or removing, the tree **re-renders immediately** and the Info and BEAST2 XML tabs are refreshed.

### Visualization Options

| Option | Description | Default |
|--------|-------------|---------|
| Theme | `light` or `dark` — auto-refreshes on change | light |
| Font (leaves) | Taxon label font size (6–24) | 11 |
| Font (labels) | Calibration label font size (5–18) | 8 |
| Export DPI | Resolution for exported figures | 300 |

### Export

| Button | Output |
|--------|--------|
| **Export Figure...** | Save tree as PDF, SVG, or PNG |
| **Export MCMCTree Newick...** | Save tree with all calibrations (original + new) as `.tree` file |

---

## Component Classes

| Class | Description |
|-------|-------------|
| `FossTreeMainWindow` | Main window — file loader, tab container, status bar |
| `TreeInfoTab` | Phase 2 — summary stats and calibration table |
| `ConvertTab` | Phase 3 — BEAST2 XML generation with options |
| `ViewTab` | Phase 4 — interactive visualization with node editing |
| `ZoomableScrollCanvas` | Scrollable matplotlib canvas with Ctrl+scroll zoom |
| `CalibrationDialog` | Popup dialog for adding/editing fossil calibrations |
