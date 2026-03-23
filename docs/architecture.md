# Architecture Overview

FossTree follows a **Model-View-Utility** architecture with strict separation of concerns.

## Package Structure

```
fosstree/
├── models/          Data layer — tree structure and calibrations
│   └── tree.py      CalibrationBase + 7 subclasses, TreeNode, PhyloTree
├── utils/           Logic layer — parsing, conversion, serialization
│   ├── calibration_parser.py  Shared parse_calibration() for all types
│   ├── parser.py              NewickParser (Newick + MCMCTree format)
│   ├── beast_xml.py           BeastXMLGenerator (type-dispatched)
│   └── writer.py              NewickWriter (polymorphic output)
└── views/           Presentation layer — visualization and GUI
    ├── tree_plot.py           TreeVisualizer (cladogram + phylogram)
    └── gui.py                 PyQt5 GUI application
```

## Design Principles

- **Polymorphic calibrations** — `CalibrationBase` ABC with 7 concrete types; consuming code uses `to_mcmctree()`, `short_label()`, `midpoint` without knowing the type
- **No circular imports** — models <- utils <- views (one-way dependency)
- **Dual interface** — every feature is usable via CLI, GUI, and Python API
- **Immutable topology** — tree structure is fixed after parsing; calibrations are mutable

## Data Flow

1. **Input**: Newick string or MCMCTree format file
2. **Parse**: `NewickParser` builds `TreeNode` tree -> `PhyloTree`, computes `tip_dist` if branch lengths present
3. **Interact**: GUI or API modifies calibrations on `TreeNode` objects
4. **Output**: `BeastXMLGenerator` (type-dispatched XML), `NewickWriter` (polymorphic), or `TreeVisualizer` (cladogram/phylogram)

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Abstract base class for calibrations | Polymorphic `to_mcmctree()` / `short_label()` — no switch statements in consuming code |
| Shared `parse_calibration()` | Single parser used by both `NewickParser` and GUI dialog |
| `tip_dist` computed at parse time | Available for display without recomputation |
| Phylogram layout alongside cladogram | Same `_compute_layout()` with `scaled` flag — no code duplication |
| `Calibration = BoundsCalibration` alias | Backward compatibility with existing code |
