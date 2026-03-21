# 📤 Newick Export — `fosstree.utils.writer`

Serializes a `PhyloTree` back to MCMCTree-compatible Newick format with `B()` calibration annotations.

**Source**: `fosstree/utils/writer.py`

---

## `NewickWriter`

### Basic Usage

```python
from fosstree.utils import NewickParser, NewickWriter
from fosstree.models import Calibration

# Parse, modify, export
tree = NewickParser().parse_file("strategy1.tree")

# Add a new calibration
for node in tree.root.traverse_preorder():
    if not node.is_leaf and node.calibration is None:
        leaves = node.get_leaf_names()
        if "Homo_sapie" in leaves and "Gallus_gal" in leaves:
            node.calibration = Calibration(lower=3.0, upper=3.5)
            break

# Write back to Newick
writer = NewickWriter()

# To string
newick_str = writer.to_string(tree)
print(newick_str)

# To file
output_path = writer.write_file(tree, "modified_tree.tree")
print(f"Saved to: {output_path}")
```

### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_string(tree)` | `PhyloTree` | `str` | Newick string ending with `;` |
| `write_file(tree, output_path)` | `PhyloTree, str\|Path` | `Path` | Write to file, returns resolved path |

---

## Output Format

The writer produces standard Newick with MCMCTree `B()` annotations:

```
((A,B)'B(5.29,6.361,0.001,0.025)',(C,D))'B(3.0,4.0,0.001,0.025)';
```

### Rules

- Leaf nodes → taxon name only (e.g., `Homo_sapie`)
- Internal nodes without calibration → `(children)` only
- Internal nodes with calibration → `(children)'B(lower,upper,p_lower,p_upper)'`
- All four calibration parameters are always written (no short form)
- Tree ends with `;` and newline

---

## Roundtrip Fidelity

The parser → writer roundtrip preserves:

- All taxon names
- Tree topology (parent-child relationships)
- All calibrations (existing + newly added)
- Calibration parameters (lower, upper, p_lower, p_upper)

```python
# Verify roundtrip
tree1 = NewickParser().parse_file("input.tree")
NewickWriter().write_file(tree1, "output.tree")
tree2 = NewickParser().parse_file("output.tree")

assert tree1.taxa == tree2.taxa
assert tree1.n_calibrations == tree2.n_calibrations
```

> **Note**: Branch lengths are discarded during parsing and are not preserved in the output. FossTree works with cladograms (topology only).

---

## GUI Export

In the GUI, click **Export MCMCTree Newick...** in the Visualization tab to save the current tree (with all edits) to a `.tree` file.
