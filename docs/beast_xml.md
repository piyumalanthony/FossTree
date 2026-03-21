# 🧪 BEAST2 XML Generator — `fosstree.utils.beast_xml`

Converts fossil calibrations from a `PhyloTree` into BEAST2-compatible MRCAPrior XML blocks.

**Source**: `fosstree/utils/beast_xml.py`

---

## `BeastXMLGenerator`

### Basic Usage

```python
from fosstree.utils import NewickParser, BeastXMLGenerator

tree = NewickParser().parse_file("strategy1.tree")

gen = BeastXMLGenerator(
    tree_ref="@Tree.t:alignment",   # your BEAST2 tree ID
    uniform_id_start=0              # starting index for Uniform IDs
)

# Generate XML string
prior_xml, log_xml = gen.generate(tree)

# Generate full XML with comment headers
full_xml = gen.generate_full_xml(tree)

# Write directly to file
output_path = gen.write(tree, "mrca_priors.xml")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tree_ref` | `str` | `"@Tree.t:alignment"` | BEAST2 tree ID reference |
| `uniform_id_start` | `int` | `0` | Starting index for `Uniform.N` distribution IDs |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `generate(tree)` | `(prior_xml, log_xml)` | Tuple of prior block and log entries |
| `generate_full_xml(tree)` | `str` | Complete XML snippet with comment headers |
| `write(tree, output_path)` | `Path` | Write XML to file, returns resolved path |

---

## Output Format

### MRCAPrior Distribution Blocks

These go inside your BEAST2 XML `<distribution id='prior' ...>` block:

```xml
<distribution id="Homo_sapie_to_Mus_muscul.prior"
              spec="beast.base.evolution.tree.MRCAPrior"
              monophyletic="true" tree="@Tree.t:alignment">
    <taxonset id="Homo_sapie_to_Mus_muscul" spec="TaxonSet">
        <taxon id="Homo_sapie" spec="Taxon"/>
        <taxon id="Mus_muscul" spec="Taxon"/>
    </taxonset>
    <Uniform id="Uniform.0" lower="0.616" name="distr" upper="1.646"/>
</distribution>
```

### Log Entries

These go inside your `<logger id='tracelog' ...>` block:

```xml
<log idref="Homo_sapie_to_Mus_muscul.prior"/>
```

### Taxon ID Handling

- First occurrence of a taxon: `<taxon id="Name" spec="Taxon"/>`
- Subsequent occurrences: `<taxon idref="Name"/>`

This ensures valid BEAST2 XML with no duplicate IDs.

---

## CLI Usage

```bash
# Print XML to stdout
fosstree convert strategy1.tree

# Save to file
fosstree convert strategy1.tree -o priors.xml

# Custom tree reference
fosstree convert strategy1.tree --tree-ref "@Tree.t:myalignment"

# Custom Uniform ID start (to avoid collisions with existing IDs)
fosstree convert strategy1.tree --uniform-start 100
```

---

## Integration with BEAST2

1. Run `fosstree convert` to generate the XML blocks
2. Open your BEAST2 XML file
3. Paste the **MRCAPrior blocks** inside `<distribution id="prior" ...>`
4. Paste the **log entries** inside `<logger id="tracelog" ...>`
5. Ensure the `tree` attribute matches your tree's ID
