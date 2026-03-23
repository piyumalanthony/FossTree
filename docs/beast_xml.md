# BEAST2 XML Generator — `fosstree.utils.beast_xml`

Converts fossil calibrations from a `PhyloTree` into BEAST2-compatible MRCAPrior XML blocks.

**Source**: `fosstree/utils/beast_xml.py`

---

## Usage

```python
from fosstree.utils import NewickParser, BeastXMLGenerator

tree = NewickParser().parse_file("my_tree.tree")

gen = BeastXMLGenerator(
    tree_ref="@Tree.t:alignment",
    uniform_id_start=0
)

# Generate and write
gen.write(tree, "mrca_priors.xml")

# Or get XML strings
prior_xml, log_xml = gen.generate(tree)
full_xml = gen.generate_full_xml(tree)
```

---

## Calibration Type Mapping

Different MCMCTree calibration types map to different BEAST2 distributions:

| MCMCTree | BEAST2 Distribution | Notes |
|----------|---------------------|-------|
| `B(lower, upper)` | `<Uniform lower="..." upper="..."/>` | Direct mapping |
| `U(tU)` | `<Uniform lower="0" upper="tU"/>` | Direct mapping |
| `G(alpha, beta)` | `<Gamma alpha="..." beta="1/beta"/>` | BEAST2 uses scale (1/rate) |
| `L(tL)` | `<Exponential offset="tL"/>` | Approximate — warning emitted |
| `SN`, `ST`, `S2N` | `<Uniform/>` placeholder | No BEAST2 equivalent — warning emitted |

When a calibration type has no direct BEAST2 equivalent, the generator emits an XML comment warning the user to review and replace the placeholder distribution.

---

## Output Format

### MRCAPrior Blocks

Paste inside your BEAST2 `<distribution id='prior' ...>` block:

```xml
<distribution id="clade_name.prior"
              spec="beast.base.evolution.tree.MRCAPrior"
              monophyletic="true" tree="@Tree.t:alignment">
    <taxonset id="clade_name" spec="TaxonSet">
        <taxon id="Homo_sapie" spec="Taxon"/>
        <taxon id="Mus_muscul" spec="Taxon"/>
    </taxonset>
    <Uniform id="Uniform.0" lower="0.616" name="distr" upper="1.646"/>
</distribution>
```

### Log Entries

Paste inside `<logger id='tracelog' ...>`:

```xml
<log idref="clade_name.prior"/>
```

---

## CLI

```bash
fosstree convert my_tree.tree                    # print to stdout
fosstree convert my_tree.tree -o priors.xml      # save to file
fosstree convert my_tree.tree --tree-ref "@Tree.t:myalignment"
```
