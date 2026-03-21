# 🌳 Newick Parser — `fosstree.utils.parser`

Parses Newick format strings with MCMCTree `B()` calibration annotations into `PhyloTree` objects.

**Source**: `fosstree/utils/parser.py`

---

## `NewickParser`

### Basic Usage

```python
from fosstree.utils import NewickParser

parser = NewickParser()

# From file
tree = parser.parse_file("strategy1.tree")

# From string
tree = parser.parse_string(
    "((A,B)'B(5.29,6.361,0.001,0.025)',C);",
    source="example"
)
```

### Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse_file(filepath)` | `str \| Path` | `PhyloTree` | Parse a Newick tree file |
| `parse_string(newick_str, source="")` | `str, str` | `PhyloTree` | Parse a Newick string |

---

## Supported Format

### Standard Newick

```
((A,B),C);
((A:0.1,B:0.2):0.3,C:0.4);
```

Branch lengths after `:` are parsed but not used in cladogram layout.

### MCMCTree Calibration Annotations

Calibrations are attached to internal nodes as quoted strings after the closing `)`:

```
((A,B)'B(lower,upper,p_lower,p_upper)',C);
```

**Examples:**

```
# Full format with tail probabilities
((Human,Mouse)'B(0.616,1.646,0.001,0.025)',Chicken);

# Nested calibrations
(((A,B)'B(1.0,2.0,0.001,0.025)',(C,D))'B(3.0,4.0,0.001,0.025)',E);
```

### Supported Calibration Patterns

| Pattern | Parsed as |
|---------|-----------|
| `'B(5.29,6.361,0.001,0.025)'` | lower=5.29, upper=6.361, p_lower=0.001, p_upper=0.025 |
| `'B(5.29,6.361)'` | lower=5.29, upper=6.361, p_lower=0.001 (default), p_upper=0.025 (default) |

### What the Parser Handles

- Arbitrarily nested parentheses
- Taxon names with underscores (e.g., `Homo_sapie`)
- Optional branch lengths after `:`
- `B()` annotations with 2 or 4 parameters
- Trees ending with or without `;`
- Leading/trailing whitespace

### File Format

Tree files should contain a single Newick string (one line or wrapped). The parser reads the entire file as one string.

```
# strategy1.tree
((Amphimedon,Suberites_),(Trichoplax,(...)'B(5.29,6.361,0.001,0.025)',...)'B(5.5285,8.33,0.001,0.001)';
```
