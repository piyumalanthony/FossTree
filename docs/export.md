# Newick Export — `fosstree.utils.writer`

Serializes a `PhyloTree` back to MCMCTree-compatible Newick format with calibration annotations.

**Source**: `fosstree/utils/writer.py`

---

## Usage

```python
from fosstree.utils import NewickParser, NewickWriter
from fosstree.models import Calibration, GammaCalibration

tree = NewickParser().parse_file("my_tree.tree")

# Add calibrations (any type)
node = tree.calibrated_nodes[0]
node.calibration = Calibration(lower=3.0, upper=3.5)

# Write
writer = NewickWriter()
newick_str = writer.to_string(tree)
writer.write_file(tree, "modified.tree")
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_string(tree)` | `str` | Newick string ending with `;` |
| `write_file(tree, output_path)` | `Path` | Write to file, returns resolved path |

---

## Output Format

All MCMCTree calibration types are written using `to_mcmctree()`:

```
((A,B)'B(5.29,6.361,0.001,0.025)',(C,D))'G(2,5)';
```

- Leaf nodes: taxon name only
- Internal nodes with calibration: `(children)'TYPE(params)'`
- Internal nodes without calibration: `(children)` only
- All parameters are written (no short form)

---

## Roundtrip Fidelity

Parse, edit, export preserves all taxon names, topology, and calibrations (all types).

> **Note**: Branch lengths are parsed but not written back. The export preserves calibration data, not branch lengths.

---

## GUI Export

In the Visualization tab, click **Export MCMCTree Newick...** to save the current tree with all edits.
