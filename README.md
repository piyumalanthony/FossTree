# 🧬 FossTree

### Fossil Calibration Annotation for Bayesian Molecular Dating

<p align="center">
  <strong>🌳 Parse · 🦴 Calibrate · 🧪 Convert · 📊 Visualize</strong>
</p>

---

FossTree is a standalone tool for working with **fossil calibrations** on phylogenetic trees. It reads [MCMCTree](http://abacus.gene.ucl.ac.uk/software/paml.html)-format Newick trees with `B(lower, upper)` annotations, lets you **interactively add and edit calibrations** through a GUI, generates [BEAST2](https://www.beast2.org/) MRCAPrior XML blocks, and produces publication-quality tree visualizations.

> 🦕 Built for researchers who need to bridge the gap between MCMCTree and BEAST2 fossil calibration formats — without manual XML editing.

---

## ✨ Features

### 🌲 Tree Parsing
- Parse Newick trees with MCMCTree `B(min, max, p_lower, p_upper)` calibration annotations
- Full OOP tree model (`TreeNode`, `Calibration`, `PhyloTree`)
- Supports trees of any size and topology

### 🦴 Interactive Calibration Editing
- **Hover** over any internal node to see its descendant taxa
- **Click** a node to display the full list of descendant species
- **Double-click** to add, edit, or remove fossil calibrations via a popup dialog
- Changes are rendered immediately on the tree

### 🧪 BEAST2 XML Generation
- Converts MCMCTree `B()` calibrations to BEAST2 `MRCAPrior` distribution blocks
- Generates matching `<taxonset>` definitions with correct `id`/`idref` handling
- Produces trace logger `<log>` entries
- Configurable tree reference ID and Uniform distribution indexing

### 📊 Tree Visualization
- Rectangular cladogram layout (FigTree-style right-angle branches)
- Calibration labels with age-gradient coloring (coolwarm colormap)
- Light and dark themes with auto-refresh on theme change
- Ctrl+scroll zoom, pan, fit-to-window
- Export to PDF, SVG, or PNG at configurable DPI

### 📤 MCMCTree Newick Export
- Write modified trees back to Newick format with `B()` annotations
- Perfect roundtrip: parse → edit → export preserves all calibrations

---

## 🖥️ GUI Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Load Tree File          [Browse...] [Load]        │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: Tree Info │ Phase 3: BEAST2 XML │ Phase 4: View   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Source: strategy1.tree                              │    │
│  │  Taxa: 54    Calibrations: 34    Max depth: 15      │    │
│  │                                                      │    │
│  │  # │ Clade Name              │ Lower │ Upper │ Taxa │    │
│  │  1 │ root_all                │ 5.529 │ 8.330 │   54 │    │
│  │  2 │ Acropora_to_Nematostel  │ 5.290 │ 6.361 │    5 │    │
│  │  3 │ Homo_sapie_to_Mus_musc  │ 0.616 │ 1.646 │    2 │    │
│  │  ...                                                 │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Status: Loaded strategy1.tree — 54 taxa, 34 calibrations  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Standalone Executable (no Python needed)

Download the latest release for your platform from [Releases](../../releases):

| Platform | Download | How to run |
|----------|----------|------------|
| 🐧 Linux | `FossTree-linux.tar.gz` | `./FossTree` from terminal |
| 🪟 Windows | `FossTree-windows.zip` | Double-click `FossTree.exe` |
| 🍎 macOS | `FossTree-macos.tar.gz` | Double-click `FossTree.app` |

> ⚠️ Keep the `FossTree` binary and `_internal/` folder together — the binary loads its dependencies from there.

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/piyumalanthony/FossTree.git
cd FossTree

# Install in a virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

pip install -e .

# Launch
fosstree                     # GUI (default)
fosstree info my_tree.tree   # CLI
```

**Requirements:** Python ≥ 3.10, PyQt5, matplotlib

---

## 🧬 Usage

### GUI Mode

```bash
fosstree                  # Launch the GUI
python -m fosstree gui    # Explicit
```

**Workflow:**
1. **Load** — Browse and select a `.tree` / `.nwk` file
2. **Info** — Review taxa count, calibration table, tree depth
3. **BEAST2 XML** — Generate and save MRCAPrior XML blocks
4. **Visualize** — Render the tree, interact with nodes, add calibrations

### CLI Mode

```bash
# 🌳 Tree summary + calibration table
fosstree info strategy1.tree

# 🧪 Convert to BEAST2 XML
fosstree convert strategy1.tree -o priors.xml
fosstree convert strategy1.tree --tree-ref "@Tree.t:myalignment"

# 📊 Render tree visualization
fosstree view strategy1.tree -o tree.pdf
fosstree view strategy1.tree --theme dark --formats pdf svg png --dpi 600
```

### 🐍 Python API

```python
from fosstree import NewickParser, BeastXMLGenerator, TreeVisualizer
from fosstree.utils import NewickWriter
from fosstree.models import Calibration

# Parse a tree
tree = NewickParser().parse_file("strategy1.tree")
print(f"{tree.n_taxa} taxa, {tree.n_calibrations} calibrations")

# Inspect calibrations
for entry in tree.get_calibration_table():
    print(f"{entry['clade_name']}: B({entry['calibration'].lower}, {entry['calibration'].upper})")

# Add a new calibration to an internal node
node = tree.calibrated_nodes[0]  # or find by traversal
node.calibration = Calibration(lower=5.0, upper=6.5, p_lower=0.001, p_upper=0.025)

# Generate BEAST2 XML
gen = BeastXMLGenerator(tree_ref="@Tree.t:alignment")
gen.write(tree, "mrca_priors.xml")

# Export modified tree back to MCMCTree Newick format
NewickWriter().write_file(tree, "modified_tree.tree")

# Visualize
viz = TreeVisualizer(theme="light", dpi=300)
viz.save(tree, "tree_figure.pdf", formats=["pdf", "svg"])
```

---

## 🦴 Calibration Format

FossTree works with the MCMCTree uniform bound calibration format:

```
B(lower, upper, p_lower, p_upper)
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `lower` | Minimum age bound (100s of Ma) | required |
| `upper` | Maximum age bound (100s of Ma) | required |
| `p_lower` | Left tail probability | 0.001 |
| `p_upper` | Right tail probability | 0.025 |

**Example tree with calibrations:**
```
((Human, Mouse)'B(0.616,1.646,0.001,0.025)', Chicken)'B(3.18,3.329,0.001,0.025)';
```

---

## 📁 Project Structure

```
FossTree/
├── fosstree/                    # 🐍 Python package
│   ├── __init__.py              # Package root, version, public exports
│   ├── __main__.py              # CLI entry point (gui/info/convert/view)
│   ├── models/
│   │   └── tree.py              # 🧬 TreeNode, Calibration, PhyloTree
│   ├── utils/
│   │   ├── parser.py            # 🌳 NewickParser — Newick + B() → PhyloTree
│   │   ├── beast_xml.py         # 🧪 BeastXMLGenerator → BEAST2 MRCAPrior XML
│   │   └── writer.py            # 📤 NewickWriter → MCMCTree Newick export
│   └── views/
│       ├── tree_plot.py         # 📊 TreeVisualizer — matplotlib cladogram
│       └── gui.py               # 🖥️ PyQt5 GUI application
├── docs/                        # 📚 Documentation
├── strategy1.tree               # 🦕 Example tree (54 taxa, 34 calibrations)
├── pyproject.toml               # Package metadata & dependencies
├── requirements.txt             # Pinned dependency versions
├── fosstree.spec                # PyInstaller build configuration
└── .github/workflows/build.yml  # CI/CD for multi-platform executables
```

---

## 🔨 Building Standalone Executables

### Local Build (current OS)

```bash
pip install pyinstaller
pyinstaller fosstree.spec
# Output: dist/FossTree/
```

### Automated Builds (all platforms)

Push a version tag to trigger GitHub Actions:

```bash
git tag v0.1.0
git push --tags
```

This builds executables for Linux, Windows, and macOS and attaches them to a GitHub Release.

---

## 🧪 Supported Conversions

```
                    ┌─────────────────┐
                    │  MCMCTree .tree  │
                    │  with B() nodes  │
                    └────────┬────────┘
                             │
                        parse (NewickParser)
                             │
                             ▼
                    ┌─────────────────┐
                    │    PhyloTree     │◄──── interactive editing (GUI)
                    │  (in-memory)     │
                    └──┬──────┬───┬───┘
                       │      │   │
          ┌────────────┘      │   └────────────┐
          ▼                   ▼                 ▼
  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
  │ BEAST2 XML    │  │ MCMCTree     │  │ PDF/SVG/PNG  │
  │ MRCAPrior     │  │ Newick       │  │ Tree Figure  │
  │ (beast_xml)   │  │ (writer)     │  │ (tree_plot)  │
  └───────────────┘  └──────────────┘  └──────────────┘
```

---

## 📋 Dependencies

| Package | Purpose |
|---------|---------|
| [PyQt5](https://pypi.org/project/PyQt5/) | GUI framework |
| [matplotlib](https://matplotlib.org/) | Tree visualization & figure export |

All other dependencies (numpy, Pillow, etc.) are pulled in transitively.

---

## 📜 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

---

## 🙏 Citation

If you use FossTree in your research, please cite:

```
FossTree: Fossil Calibration Annotation for Bayesian Molecular Dating
https://github.com/piyumalanthony/FossTree
```

---

<p align="center">
  🧬 Made for phylogeneticists, by a phylogeneticist 🌳
</p>
