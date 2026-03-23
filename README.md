# FossTree

[![Build](https://github.com/piyumalanthony/FossTree/actions/workflows/build.yml/badge.svg)](https://github.com/piyumalanthony/FossTree/actions/workflows/build.yml)

**Fossil Calibration Annotation for Bayesian Molecular Dating**

---

FossTree is a tool for working with fossil calibrations on phylogenetic trees. It reads [MCMCTree](http://abacus.gene.ucl.ac.uk/software/paml.html)-format Newick trees with calibration annotations, lets you interactively add and edit calibrations through a GUI, generates [BEAST2](https://www.beast2.org/) MRCAPrior XML blocks, and produces publication-quality tree visualizations.

---

## Features

- **Parse** Newick trees with all MCMCTree calibration types: `B()`, `L()`, `U()`, `G()`, `SN()`, `ST()`, `S2N()`
- **Auto-detect** MCMCTree format files (e.g. header line `16 1` followed by tree)
- **Visualize** as cladogram (unscaled) or phylogram (branch-length scaled)
- **Interact** with nodes: hover for taxa, click for details, double-click to calibrate
- **Convert** calibrations to BEAST2 MRCAPrior XML
- **Export** modified trees back to MCMCTree Newick format

---

## Quick Start

### Standalone Executable (no Python needed)

Download from [Releases](../../releases):

| Platform | Download | Run |
|----------|----------|-----|
| Linux | `FossTree-linux.tar.gz` | `./FossTree` |
| Windows | `FossTree-windows.zip` | `FossTree.exe` |
| macOS | `FossTree-macos.tar.gz` | `FossTree.app` |

### Install from Source

```bash
git clone https://github.com/piyumalanthony/FossTree.git
cd FossTree
pip install -e .
fosstree          # launch GUI
```

**Requirements:** Python 3.10+, PyQt5, matplotlib

---

## Usage

### GUI

```bash
fosstree
```

1. **Load** a `.tree` / `.nwk` file (plain Newick or MCMCTree format)
2. **Info** tab shows taxa count, calibration table, tree stats
3. **BEAST2 XML** tab generates MRCAPrior XML blocks
4. **Visualization** tab renders the tree with interactive node editing

### CLI

```bash
fosstree info my_tree.tree              # tree summary
fosstree convert my_tree.tree -o p.xml  # BEAST2 XML
fosstree view my_tree.tree              # render to PDF
```

### Python API

```python
from fosstree import NewickParser, BeastXMLGenerator, TreeVisualizer
from fosstree.utils import NewickWriter, parse_calibration
from fosstree.models import Calibration, LowerCalibration, GammaCalibration

# Parse
tree = NewickParser().parse_file("my_tree.tree")
print(tree.summary())

# Add calibrations (any MCMCTree type)
node = tree.calibrated_nodes[0]
node.calibration = Calibration(lower=5.0, upper=6.5)
# node.calibration = LowerCalibration(tL=0.06, p=0.1, c=1.0, pL=0.025)
# node.calibration = GammaCalibration(alpha=2, beta=5)

# Convert to BEAST2 XML
BeastXMLGenerator().write(tree, "priors.xml")

# Export back to MCMCTree Newick
NewickWriter().write_file(tree, "modified.tree")

# Visualize (cladogram or phylogram)
TreeVisualizer(show_branch_lengths=True).save(tree, "tree.pdf")
```

---

## Supported Calibration Types

| Type | Format | Description |
|------|--------|-------------|
| **B** | `B(lower, upper[, pL, pU])` | Lower & upper bounds |
| **L** | `L(tL[, p, c, pL])` | Lower (minimum) bound |
| **U** | `U(tU[, pR])` | Upper (maximum) bound |
| **G** | `G(alpha, beta)` | Gamma distribution |
| **SN** | `SN(location, scale, shape)` | Skew-normal |
| **ST** | `ST(location, scale, shape, df)` | Skew-t |
| **S2N** | `S2N(p1, loc1, s1, sh1, loc2, s2, sh2)` | Mixture of 2 skew-normals |

**Example tree:**
```
((Human, Mouse)'B(0.616,1.646)', Chicken)'G(2,5)';
```

### BEAST2 Mapping

| MCMCTree | BEAST2 Distribution |
|----------|---------------------|
| B | Uniform |
| U | Uniform(0, tU) |
| G | Gamma |
| L | Exponential with offset (approximate) |
| SN, ST, S2N | Placeholder Uniform with warning comment |

---

## Visualization Modes

- **Cladogram** (default) — all leaves aligned, topology only
- **Phylogram** (branch lengths checkbox) — branches scaled by length, dotted guide lines to aligned labels, tip distances shown on hover

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [PyQt5](https://pypi.org/project/PyQt5/) | GUI |
| [matplotlib](https://matplotlib.org/) | Visualization |

---

## License

[GNU General Public License v3.0](LICENSE)

---

## Citation

```
FossTree: Fossil Calibration Annotation for Bayesian Molecular Dating
https://github.com/piyumalanthony/FossTree
```
