# Newick Parser — `fosstree.utils.parser`

Parses Newick format strings with MCMCTree calibration annotations into `PhyloTree` objects.

**Source**: `fosstree/utils/parser.py`

---

## Usage

```python
from fosstree.utils import NewickParser

parser = NewickParser()

# From file (plain Newick or MCMCTree format)
tree = parser.parse_file("my_tree.tree")

# From string
tree = parser.parse_string("((A,B)'B(5.29,6.361)',C);")
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `parse_file(filepath)` | `PhyloTree` | Parse a Newick tree file |
| `parse_string(newick_str, source="")` | `PhyloTree` | Parse a Newick string |

---

## Supported Formats

### Plain Newick

```
((A,B),C);
((A:0.1,B:0.2):0.3,C:0.4);
```

Branch lengths after `:` are parsed and stored on nodes.

### MCMCTree Format

Files that start with a header line (e.g. `16 1` meaning 16 taxa, 1 tree) are auto-detected. The parser emits a warning and reads the tree from the first `(`:

```
16 1
((((t8:1.64,t15:1.64):0.52,...)'B(1.945,2.377)':0.35,...)'G(1.92,0.66)';
```

### Supported Calibration Types

All MCMCTree calibration types are recognized in quoted annotations after `)`:

| Pattern | Example |
|---------|---------|
| `B(lower, upper[, pL, pU])` | `'B(0.616,1.646,0.001,0.025)'` |
| `L(tL[, p, c, pL])` | `'L(0.06,0.1,1,0.025)'` |
| `U(tU[, pR])` | `'U(0.08,0.025)'` |
| `G(alpha, beta)` | `'G(2,5)'` |
| `SN(location, scale, shape)` | `'SN(0.5,0.1,3)'` |
| `ST(location, scale, shape, df)` | `'ST(0.5,0.1,3,5)'` |
| `S2N(p1, loc1, s1, sh1, loc2, s2, sh2)` | `'S2N(0.3,0.5,0.1,2,1.0,0.2,-1)'` |

Optional parameters use MCMCTree defaults when omitted.

### What the Parser Handles

- All 7 MCMCTree calibration types
- MCMCTree format files with header lines
- Branch lengths (stored on nodes, used for phylogram visualization)
- Tip distance computation (auto-computed when branch lengths are present)
- Arbitrarily nested parentheses
- Taxon names with underscores
- Trees with or without `;`

### Shared Parser

The `parse_calibration()` function is available for parsing calibration strings independently:

```python
from fosstree.utils import parse_calibration

cal = parse_calibration("G(2,5)")
# GammaCalibration(alpha=2.0, beta=5.0)
```
