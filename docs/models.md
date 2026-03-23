# Models — `fosstree.models`

Core data structures for phylogenetic trees with fossil calibrations.

**Source**: `fosstree/models/tree.py`

---

## Calibration Types

FossTree supports all MCMCTree calibration types via an abstract base class `CalibrationBase` and concrete subclasses.

### `CalibrationBase` (abstract)

All calibration types implement:

| Method / Property | Returns | Description |
|-------------------|---------|-------------|
| `cal_type` | `str` | Type code: `"B"`, `"L"`, `"U"`, `"G"`, `"SN"`, `"ST"`, `"S2N"` |
| `representative_age` | `float` | Scalar age for color mapping |
| `midpoint` | `float` | Alias for `representative_age` |
| `to_mcmctree()` | `str` | Full MCMCTree string, e.g. `"B(0.5,1.0,0.001,0.025)"` |
| `short_label()` | `str` | Compact label, e.g. `"B(0.5,1.0)"` |

### Concrete Types

| Class | Format | Fields |
|-------|--------|--------|
| `BoundsCalibration` | `B(lower, upper, p_lower, p_upper)` | lower, upper, p_lower=0.001, p_upper=0.025 |
| `LowerCalibration` | `L(tL, p, c, pL)` | tL, p=0.1, c=1.0, pL=0.025 |
| `UpperCalibration` | `U(tU, pR)` | tU, pR=0.025 |
| `GammaCalibration` | `G(alpha, beta)` | alpha, beta |
| `SkewNormalCalibration` | `SN(location, scale, shape)` | location, scale, shape |
| `SkewTCalibration` | `ST(location, scale, shape, df)` | location, scale, shape, df |
| `Skew2NormalsCalibration` | `S2N(p1, loc1, s1, sh1, loc2, s2, sh2)` | p1, loc1, scale1, shape1, loc2, scale2, shape2 |

`Calibration` is an alias for `BoundsCalibration` (backward compatibility).

```python
from fosstree.models import Calibration, GammaCalibration
from fosstree.utils import parse_calibration

# Direct construction
cal = Calibration(lower=5.29, upper=6.361)
cal.to_mcmctree()  # "B(5.29,6.361,0.001,0.025)"

# Parse from string
cal = parse_calibration("G(2,5)")
cal.cal_type         # "G"
cal.representative_age  # 0.4
```

---

## `TreeNode`

A single node in a phylogenetic tree.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `node_id` | `int` | required | Unique identifier |
| `name` | `str \| None` | `None` | Taxon name (leaves only) |
| `children` | `list[TreeNode]` | `[]` | Child nodes |
| `parent` | `TreeNode \| None` | `None` | Parent node |
| `calibration` | `CalibrationBase \| None` | `None` | Fossil calibration |
| `tip_dist` | `float \| None` | `None` | Max branch-length distance to furthest leaf |

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_leaves()` | `list[TreeNode]` | All leaf nodes under this node |
| `get_leaf_names()` | `list[str]` | Sorted taxon names of descendant leaves |
| `get_depth()` | `int` | Edges from root to this node |
| `traverse_preorder()` | `Iterator` | Pre-order traversal |
| `traverse_postorder()` | `Iterator` | Post-order traversal |
| `traverse_leaves()` | `Iterator` | Left-to-right leaf traversal |

---

## `PhyloTree`

High-level container for a complete phylogenetic tree.

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `root` | `TreeNode` | Root node |
| `source` | `str` | Source filename or label |
| `taxa` | `list[str]` | All taxon names |
| `n_taxa` | `int` | Number of taxa |
| `calibrated_nodes` | `list[TreeNode]` | Nodes with calibrations |
| `n_calibrations` | `int` | Number of calibrations |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_calibration_table()` | `list[dict]` | Table with `node`, `clade_name`, `calibration`, `taxa` |
| `compute_tip_distances()` | `None` | Compute `tip_dist` for all nodes from branch lengths |
| `max_depth()` | `int` | Max tree depth |
| `summary()` | `str` | Text summary with calibration table |
