# 📊 Tree Visualization — `fosstree.views.tree_plot`

Renders phylogenetic trees as rectangular cladograms with fossil calibration labels using matplotlib.

**Source**: `fosstree/views/tree_plot.py`

---

## `TreeVisualizer`

### Basic Usage

```python
from fosstree import NewickParser, TreeVisualizer

tree = NewickParser().parse_file("strategy1.tree")

viz = TreeVisualizer(theme="light", dpi=300)

# Save to file(s)
viz.save(tree, "tree.pdf", formats=["pdf", "svg", "png"])

# Get figure and axes for further customization
result = viz.plot(tree, title="My Tree")
result.fig.savefig("custom.pdf")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `theme` | `str` | `"light"` | Color theme: `"light"` or `"dark"` |
| `fig_width` | `float` | `20.0` | Figure width in inches |
| `font_size_leaf` | `int` | `11` | Font size for taxon labels |
| `font_size_label` | `int` | `8` | Font size for calibration labels |
| `line_width` | `float` | `0.8` | Branch line width |
| `node_dot_size` | `int` | `18` | Size of node marker dots |
| `label_offset_x` | `float` | `0.15` | Horizontal offset for calibration labels |
| `leaf_font` | `str` | `"monospace"` | Font family for leaf labels |
| `cmap_name` | `str` | `"coolwarm"` | Matplotlib colormap for calibration ages |
| `dpi` | `int` | `300` | DPI for saved figures |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `plot(tree, title=None, ax=None)` | `PlotResult` | Draw the tree, return result with positions |
| `save(tree, output_path, title=None, formats=None)` | `list[Path]` | Render and save to file(s) |

---

## `PlotResult`

Returned by `plot()`, contains everything needed for interactive use.

| Field | Type | Description |
|-------|------|-------------|
| `fig` | `Figure` | matplotlib Figure object |
| `ax` | `Axes` | matplotlib Axes object |
| `node_positions` | `dict[int, (float, float)]` | Node ID → (x, y) in data coordinates |
| `internal_nodes` | `list[TreeNode]` | All internal nodes (for hit-testing) |

---

## Themes

### Light Theme (default)
- White background, dark grey branches
- Black text for taxa, dark calibration labels
- Suitable for publications and printing

### Dark Theme
- Dark grey background (`#1e1e1e`), light grey branches
- Light text throughout
- Suitable for presentations and screen viewing

---

## Layout Algorithm

FossTree uses a **rectangular cladogram** layout (FigTree-style):

- **X-axis** = depth from root (all leaves aligned at max depth)
- **Y-axis** = leaf traversal order (preserves Newick topology)
- **Internal nodes** = positioned at mean Y of children
- **Branches** = right-angle connectors (vertical + horizontal segments)

---

## Visual Elements

| Element | Description |
|---------|-------------|
| **Branches** | Right-angle lines connecting parent to children |
| **Leaf labels** | Italic monospace taxon names (underscores → spaces) |
| **Internal node dots** | Small grey dots on uncalibrated nodes |
| **Calibration dots** | Colored dots on calibrated nodes (age-gradient) |
| **Calibration labels** | `[N] B(lower,upper)` with colored background boxes |
| **Colorbar** | Shows calibration midpoint age scale |

---

## CLI Usage

```bash
# Default: light theme, PDF output
fosstree view strategy1.tree

# Dark theme, multiple formats
fosstree view strategy1.tree --theme dark --formats pdf svg png

# Custom output path and DPI
fosstree view strategy1.tree -o figures/my_tree.pdf --dpi 600

# Wider figure
fosstree view strategy1.tree --fig-width 30
```
