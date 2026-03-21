# 🧬 Models — `fosstree.models`

The models module defines the core data structures for representing phylogenetic trees with fossil calibrations.

**Source**: `fosstree/models/tree.py`

---

## `Calibration`

Represents an MCMCTree `B(lower, upper, p_lower, p_upper)` uniform bound calibration.

```python
from fosstree.models import Calibration

cal = Calibration(lower=5.29, upper=6.361, p_lower=0.001, p_upper=0.025)

cal.midpoint     # 5.8255 — used for colormap in visualization
cal.to_mcmctree()  # "B(5.29,6.361,0.001,0.025)"
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `lower` | `float` | required | Minimum age constraint |
| `upper` | `float` | required | Maximum age constraint |
| `p_lower` | `float` | 0.001 | Left tail probability |
| `p_upper` | `float` | 0.025 | Right tail probability |

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `midpoint` | `float` | `(lower + upper) / 2` |

---

## `TreeNode`

Represents a single node in a phylogenetic tree (either a leaf or an internal node).

```python
from fosstree.models import TreeNode, Calibration

# Leaf node
leaf = TreeNode(node_id=0, name="Homo_sapie")
leaf.is_leaf      # True
leaf.is_root      # True (no parent)

# Internal node with calibration
internal = TreeNode(node_id=1)
internal.children = [leaf]
leaf.parent = internal
internal.calibration = Calibration(lower=0.616, upper=1.646)
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `node_id` | `int` | required | Unique identifier |
| `name` | `str \| None` | `None` | Taxon name (leaves only) |
| `children` | `list[TreeNode]` | `[]` | Child nodes |
| `parent` | `TreeNode \| None` | `None` | Parent node |
| `calibration` | `Calibration \| None` | `None` | Fossil calibration |

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `is_leaf` | `bool` | `True` if no children |
| `is_root` | `bool` | `True` if no parent |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_leaves()` | `list[TreeNode]` | All leaf nodes under this node |
| `get_leaf_names()` | `list[str]` | Sorted taxon names of all descendant leaves |
| `get_depth()` | `int` | Number of edges from root to this node |
| `traverse_preorder()` | `Iterator[TreeNode]` | Pre-order traversal (root first) |
| `traverse_postorder()` | `Iterator[TreeNode]` | Post-order traversal (leaves first) |
| `traverse_leaves()` | `Iterator[TreeNode]` | Left-to-right leaf traversal |

---

## `PhyloTree`

High-level container representing a complete phylogenetic tree with its calibrations.

```python
from fosstree import NewickParser

tree = NewickParser().parse_file("strategy1.tree")

tree.n_taxa           # 54
tree.n_calibrations   # 34
tree.taxa             # ['Amphimedon', 'Suberites_', ...]
tree.max_depth()      # 15
tree.calibrated_nodes # [TreeNode(...), ...]

# Print summary
print(tree.summary())

# Get calibration table with unique clade names
for entry in tree.get_calibration_table():
    print(entry['clade_name'], entry['calibration'], len(entry['taxa']))
```

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `root` | `TreeNode` | Root node of the tree |
| `source` | `str` | Source filename or label |
| `taxa` | `list[str]` | All taxon names in traversal order |
| `n_taxa` | `int` | Number of taxa |
| `calibrated_nodes` | `list[TreeNode]` | All nodes with calibrations |
| `n_calibrations` | `int` | Number of calibrations |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_clade_name(node)` | `str` | Human-readable name (e.g., `"Homo_sapie_to_Mus_muscul"`) |
| `get_calibration_table()` | `list[dict]` | Table with keys: `node`, `clade_name`, `calibration`, `taxa` |
| `max_depth()` | `int` | Maximum tree depth (edges from root to deepest leaf) |
| `summary()` | `str` | Formatted text summary with calibration table |
