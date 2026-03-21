# 🧬 Architecture Overview

FossTree follows a clean **Model–View–Utility** architecture with strict separation of concerns.

## Package Structure

```
fosstree/
├── models/          Data layer — tree structure and calibrations
├── utils/           Logic layer — parsing, conversion, serialization
└── views/           Presentation layer — visualization and GUI
```

## Design Principles

- **OOP throughout** — every component is a class with clear responsibilities
- **No circular imports** — models ← utils ← views (one-way dependency)
- **Dual interface** — every feature is usable via CLI, GUI, and Python API
- **Immutable topology** — tree structure is fixed after parsing; calibrations are mutable

## Component Dependency Graph

```
┌──────────────────────────────────────────────────────────────┐
│  __main__.py (CLI entry point)                               │
│    ├── cmd_gui()    → views/gui.py                           │
│    ├── cmd_info()   → utils/parser.py → models/tree.py       │
│    ├── cmd_convert()→ utils/beast_xml.py                     │
│    └── cmd_view()   → views/tree_plot.py                     │
├──────────────────────────────────────────────────────────────┤
│  views/gui.py  (PyQt5 application)                           │
│    ├── TreeInfoTab      → PhyloTree.get_calibration_table()  │
│    ├── ConvertTab       → BeastXMLGenerator                  │
│    ├── ViewTab          → TreeVisualizer.plot()               │
│    │   ├── hover/click  → TreeNode.get_leaf_names()          │
│    │   ├── dbl-click    → CalibrationDialog → Calibration    │
│    │   └── export nwk   → NewickWriter                       │
│    └── ZoomableScrollCanvas (Ctrl+scroll zoom)               │
├──────────────────────────────────────────────────────────────┤
│  views/tree_plot.py  (matplotlib rendering)                  │
│    └── TreeVisualizer.plot() → PlotResult                    │
│        ├── node_positions: {node_id: (x, y)}                 │
│        └── internal_nodes: [TreeNode, ...]                   │
├──────────────────────────────────────────────────────────────┤
│  utils/parser.py      NewickParser   → PhyloTree             │
│  utils/beast_xml.py   BeastXMLGenerator → XML string         │
│  utils/writer.py      NewickWriter   → Newick string         │
├──────────────────────────────────────────────────────────────┤
│  models/tree.py                                              │
│    ├── Calibration  (lower, upper, p_lower, p_upper)         │
│    ├── TreeNode     (node_id, name, children, parent, cal)   │
│    └── PhyloTree    (root, taxa, calibrated_nodes, summary)  │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Input**: Newick string with `B()` annotations (file or string)
2. **Parse**: `NewickParser` builds a tree of `TreeNode` objects → `PhyloTree`
3. **Interact**: GUI or API modifies `Calibration` on `TreeNode` objects
4. **Output**: `BeastXMLGenerator`, `NewickWriter`, or `TreeVisualizer` reads `PhyloTree`

The `PhyloTree` object is the central data structure. All operations read from or write to it.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `TreeNode` uses parent pointers | Enables upward traversal for depth computation |
| Calibrations are mutable on nodes | Allows interactive editing without rebuilding the tree |
| `PlotResult` carries node positions | Enables GUI hit-testing without re-computing layout |
| `NewickWriter` walks the tree recursively | Guarantees structural fidelity on roundtrip |
| PyQt5 over tkinter | More mature widget set, better matplotlib integration |
