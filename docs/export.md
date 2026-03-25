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

# Write (calibrations only)
writer = NewickWriter()
newick_str = writer.to_string(tree)
writer.write_file(tree, "modified.tree")

# Write with branch lengths
newick_bl = writer.to_string(tree, include_branch_lengths=True)
writer.write_file(tree, "with_lengths.tree", include_branch_lengths=True)
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_string(tree, include_branch_lengths=False)` | `str` | Newick string ending with `;` |
| `write_file(tree, output_path, include_branch_lengths=False)` | `Path` | Write to file, returns resolved path |

---

## Output Format

All MCMCTree calibration types are written using `to_mcmctree()`:

```
((A,B)'B(5.29,6.361,0.001,0.025)',(C,D))'G(2,5)';
```

With `include_branch_lengths=True`:

```
((A:0.5,B:0.3)'B(5.29,6.361,0.001,0.025)':0.2,(C:0.4,D:0.6):0.1)'G(2,5)';
```

- Leaf nodes: taxon name (+ `:length` if branch lengths enabled)
- Internal nodes with calibration: `(children)'TYPE(params)'` (+ `:length`)
- Internal nodes without calibration: `(children)` (+ `:length`)
- All parameters are written (no short form)

---

## Roundtrip Fidelity

Parse, edit, export preserves all taxon names, topology, and calibrations (all types). When `include_branch_lengths=True`, branch lengths are also preserved.

---

## GUI Export

In the Visualization tab, click **Export MCMCTree Newick...** to save the current tree with all edits. If the **Branch lengths** checkbox is checked, branch lengths are included in the exported file.
