# Tree Visualization — `fosstree.views.tree_plot`

Renders phylogenetic trees as rectangular cladograms or phylograms with fossil calibration labels.

**Source**: `fosstree/views/tree_plot.py`

---

## Usage

```python
from fosstree import NewickParser, TreeVisualizer

tree = NewickParser().parse_file("my_tree.tree")

# Cladogram (default)
viz = TreeVisualizer(theme="light", dpi=300)
viz.save(tree, "tree.pdf")

# Phylogram (branch-length scaled)
viz = TreeVisualizer(show_branch_lengths=True, dpi=300)
viz.save(tree, "tree_scaled.pdf")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `theme` | `str` | `"light"` | `"light"` or `"dark"` |
| `fig_width` | `float` | `20.0` | Figure width in inches |
| `font_size_leaf` | `int` | `11` | Taxon label font size |
| `font_size_label` | `int` | `8` | Calibration label font size |
| `line_width` | `float` | `0.8` | Branch line width |
| `node_dot_size` | `int` | `18` | Node marker dot size |
| `cmap_name` | `str` | `"coolwarm"` | Colormap for calibration ages |
| `dpi` | `int` | `300` | DPI for saved figures |
| `show_branch_lengths` | `bool` | `False` | Enable phylogram mode with branch length labels |

---

## Layout Modes

### Cladogram (default)

- X-axis = depth from root (all leaves aligned at max depth)
- Y-axis = leaf traversal order
- Branches = right-angle connectors

### Phylogram (`show_branch_lengths=True`)

- X-axis = cumulative branch length from root
- Leaves at varying X positions based on total path length
- Dotted guide lines connect leaf tips to aligned labels
- Branch length values displayed on each branch
- Falls back to cladogram if tree has no branch lengths

---

## Visual Elements

| Element | Description |
|---------|-------------|
| Branches | Right-angle lines connecting parent to children |
| Leaf labels | Italic monospace taxon names (aligned with guide lines in phylogram) |
| Internal node dots | Small grey dots on uncalibrated nodes |
| Calibration dots | Colored dots with age-gradient coloring |
| Calibration labels | `[N] type(params)` with colored background, e.g. `[1] B(0.5,1.0)` |
| Branch length labels | Values on each branch (phylogram mode only) |
| Colorbar | Calibration representative age scale |

---

## CLI

```bash
fosstree view my_tree.tree                          # cladogram PDF
fosstree view my_tree.tree --theme dark             # dark theme
fosstree view my_tree.tree --formats pdf svg png    # multiple formats
fosstree view my_tree.tree -o tree.pdf --dpi 600    # high resolution
```
