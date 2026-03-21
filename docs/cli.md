# ⌨️ CLI Reference — `fosstree`

FossTree provides a command-line interface with four subcommands.

**Source**: `fosstree/__main__.py`

---

## General Usage

```bash
fosstree [command] [arguments]
fosstree --help
```

When invoked with **no arguments**, the GUI launches by default.

---

## Commands

### `gui` — Launch GUI

```bash
fosstree gui
fosstree          # same (default when no args)
```

Opens the PyQt5 graphical interface. See [GUI Documentation](gui.md).

---

### `info` — Tree Summary

Display tree statistics and calibration table.

```bash
fosstree info <tree_file>
```

**Example:**

```bash
$ fosstree info strategy1.tree

Phylogenetic Tree: strategy1.tree
  Taxa: 54
  Calibrations: 34
  Max depth: 15

Clade Name                                       Lower    Upper  #Taxa
----------------------------------------------------------------------
root_all                                        5.5285   8.3300     54
Acanthoscu_to_Xenoturbel_1                      5.5285   6.3610     51
Acropora_m_to_Nematostel                        5.2900   6.3610      5
...
```

---

### `convert` — BEAST2 XML Generation

Convert MCMCTree `B()` calibrations to BEAST2 MRCAPrior XML.

```bash
fosstree convert <tree_file> [options]
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | stdout | Output XML file path |
| `--tree-ref` | `@Tree.t:alignment` | BEAST2 tree ID reference |
| `--uniform-start` | `0` | Starting index for Uniform distribution IDs |

**Examples:**

```bash
# Print to terminal
fosstree convert strategy1.tree

# Save to file
fosstree convert strategy1.tree -o mrca_priors.xml

# Custom BEAST2 tree reference
fosstree convert strategy1.tree --tree-ref "@Tree.t:Comb-16taxa-1x"

# Avoid ID collisions (start Uniform IDs at 50)
fosstree convert strategy1.tree --uniform-start 50 -o priors.xml
```

---

### `view` — Tree Visualization

Render the phylogenetic tree as a figure file.

```bash
fosstree view <tree_file> [options]
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | `<tree_file>.pdf` | Output file path |
| `--theme` | `light` | Color theme: `light` or `dark` |
| `--formats` | inferred from `-o` | Output formats (space-separated): `pdf`, `svg`, `png` |
| `--fig-width` | `20.0` | Figure width in inches |
| `--dpi` | `300` | Output resolution |

**Examples:**

```bash
# Default: saves as strategy1.pdf
fosstree view strategy1.tree

# Dark theme, multiple formats
fosstree view strategy1.tree --theme dark --formats pdf svg png

# Custom output and high DPI
fosstree view strategy1.tree -o figures/tree.pdf --dpi 600

# Extra-wide figure for large trees
fosstree view strategy1.tree --fig-width 30
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (file not found, parse error, etc.) |
