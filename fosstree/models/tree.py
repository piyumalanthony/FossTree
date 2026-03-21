"""Core data models for phylogenetic trees with fossil calibrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Calibration:
    """MCMCTree B(lower, upper, p_lower, p_upper) fossil calibration."""

    lower: float
    upper: float
    p_lower: float = 0.001
    p_upper: float = 0.025

    @property
    def midpoint(self) -> float:
        return (self.lower + self.upper) / 2.0

    def to_mcmctree(self) -> str:
        return f"B({self.lower},{self.upper},{self.p_lower},{self.p_upper})"

    def __repr__(self) -> str:
        return f"Calibration(B({self.lower},{self.upper}))"


@dataclass
class TreeNode:
    """A node in a phylogenetic tree."""

    node_id: int
    name: Optional[str] = None
    children: list[TreeNode] = field(default_factory=list)
    parent: Optional[TreeNode] = None
    calibration: Optional[Calibration] = None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def get_leaves(self) -> list[TreeNode]:
        """Return all leaf nodes under this node."""
        if self.is_leaf:
            return [self]
        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())
        return leaves

    def get_leaf_names(self) -> list[str]:
        """Return sorted taxon names of all leaves under this node."""
        return sorted(leaf.name for leaf in self.get_leaves() if leaf.name)

    def get_depth(self) -> int:
        """Depth from root (number of edges)."""
        depth = 0
        node = self
        while node.parent is not None:
            depth += 1
            node = node.parent
        return depth

    def traverse_preorder(self):
        """Yield nodes in pre-order traversal."""
        yield self
        for child in self.children:
            yield from child.traverse_preorder()

    def traverse_postorder(self):
        """Yield nodes in post-order traversal."""
        for child in self.children:
            yield from child.traverse_postorder()
        yield self

    def traverse_leaves(self):
        """Yield leaf nodes in left-to-right order (preserves Newick topology)."""
        if self.is_leaf:
            yield self
        else:
            for child in self.children:
                yield from child.traverse_leaves()

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"TreeNode(id={self.node_id}, name={self.name!r})"
        cal = f", cal={self.calibration}" if self.calibration else ""
        return f"TreeNode(id={self.node_id}, children={len(self.children)}{cal})"


class PhyloTree:
    """A phylogenetic tree with fossil calibrations.

    Provides high-level access to the tree structure, taxa, and calibrations.
    """

    def __init__(self, root: TreeNode, source: str = ""):
        self.root = root
        self.source = source

    @property
    def taxa(self) -> list[str]:
        """All taxon names in tree-traversal order."""
        return [leaf.name for leaf in self.root.traverse_leaves() if leaf.name]

    @property
    def n_taxa(self) -> int:
        return len(self.taxa)

    @property
    def calibrated_nodes(self) -> list[TreeNode]:
        """All internal nodes that have a calibration, sorted by node_id."""
        return sorted(
            (n for n in self.root.traverse_preorder() if n.calibration),
            key=lambda n: n.node_id,
        )

    @property
    def n_calibrations(self) -> int:
        return len(self.calibrated_nodes)

    def get_clade_name(self, node: TreeNode) -> str:
        """Generate a human-readable clade name for a calibrated node."""
        leaf_names = node.get_leaf_names()
        if len(leaf_names) == self.n_taxa:
            return "root_all"
        first = leaf_names[0][:10]
        last = leaf_names[-1][:10]
        return f"{first}_to_{last}"

    def get_calibration_table(self) -> list[dict]:
        """Build a table of calibrations with unique clade names.

        Returns list of dicts with keys: node, clade_name, calibration, taxa.
        """
        entries = []
        for node in self.calibrated_nodes:
            entries.append({
                "node": node,
                "clade_name": self.get_clade_name(node),
                "calibration": node.calibration,
                "taxa": node.get_leaf_names(),
            })

        # Ensure unique clade names by appending suffix for duplicates
        name_count: dict[str, int] = {}
        for entry in entries:
            name = entry["clade_name"]
            name_count[name] = name_count.get(name, 0) + 1

        # For names that appear more than once, add _1, _2, ...
        counters: dict[str, int] = {}
        for entry in entries:
            name = entry["clade_name"]
            if name_count[name] > 1:
                counters[name] = counters.get(name, 0) + 1
                entry["clade_name"] = f"{name}_{counters[name]}"

        return entries

    def max_depth(self) -> int:
        """Maximum depth (edges from root to deepest leaf)."""
        return max(leaf.get_depth() for leaf in self.root.traverse_leaves())

    def summary(self) -> str:
        """Return a text summary of the tree."""
        lines = [
            f"Phylogenetic Tree: {self.source or '(unnamed)'}",
            f"  Taxa: {self.n_taxa}",
            f"  Calibrations: {self.n_calibrations}",
            f"  Max depth: {self.max_depth()}",
            "",
            f"{'Clade Name':<45} {'Lower':>8} {'Upper':>8} {'#Taxa':>6}",
            "-" * 70,
        ]
        for entry in self.get_calibration_table():
            cal = entry["calibration"]
            lines.append(
                f"{entry['clade_name']:<45} {cal.lower:>8.4f} {cal.upper:>8.4f} "
                f"{len(entry['taxa']):>6}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"PhyloTree(taxa={self.n_taxa}, calibrations={self.n_calibrations})"
