# CLI Reference — `fosstree`

**Source**: `fosstree/__main__.py`

---

## General Usage

```bash
fosstree [command] [arguments]
fosstree          # launches GUI (default)
```

---

## Commands

### `gui` — Launch GUI

```bash
fosstree gui
```

### `info` — Tree Summary

```bash
fosstree info <tree_file>
```

Displays taxa count, calibrations, and calibration table (Type + Calibration columns).

**Example:**

```
$ fosstree info my_tree.tree

Phylogenetic Tree: my_tree.tree
  Taxa: 16
  Calibrations: 3
  Max depth: 5

Clade Name                                    Type Calibration                     #Taxa
----------------------------------------------------------------------------------------
root_all                                         G G(1.92,0.66)                       16
t1_to_t9                                         B B(1.945,2.3773)                     4
t11_to_t6                                        B B(1.471,1.798)                      7
```

### `convert` — BEAST2 XML

Convert MCMCTree calibrations to BEAST2 MRCAPrior XML.

```bash
fosstree convert <tree_file> [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | stdout | Output XML file |
| `--tree-ref` | `@Tree.t:alignment` | BEAST2 tree ID reference |
| `--uniform-start` | `0` | Starting distribution ID index |

### `view` — Visualization

Render the tree as a figure file.

```bash
fosstree view <tree_file> [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | `<tree_file>.pdf` | Output file path |
| `--theme` | `light` | `light` or `dark` |
| `--formats` | inferred | `pdf`, `svg`, `png` (space-separated) |
| `--fig-width` | `20.0` | Figure width in inches |
| `--dpi` | `300` | Output resolution |
