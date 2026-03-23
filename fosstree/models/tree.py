"""Core data models for phylogenetic trees with fossil calibrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ── Calibration Base & Subclasses ─────────────────────────────────────────


class CalibrationBase(ABC):
    """Abstract base for all MCMCTree calibration types."""

    @property
    @abstractmethod
    def cal_type(self) -> str:
        """Type code: 'B', 'L', 'U', 'G', 'SN', 'ST', 'S2N'."""
        ...

    @property
    @abstractmethod
    def representative_age(self) -> float:
        """Scalar age for color mapping and sorting."""
        ...

    @abstractmethod
    def to_mcmctree(self) -> str:
        """Full MCMCTree notation, e.g. 'B(0.5,1.0,0.001,0.025)'."""
        ...

    @abstractmethod
    def short_label(self) -> str:
        """Compact label for plot annotations, e.g. 'B(0.5,1.0)'."""
        ...

    @property
    def midpoint(self) -> float:
        """Alias for representative_age (backward compatibility)."""
        return self.representative_age

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.short_label()})"


@dataclass
class BoundsCalibration(CalibrationBase):
    """B(tL, tU, pL, pU) — soft lower & upper bounds."""

    lower: float
    upper: float
    p_lower: float = 0.001
    p_upper: float = 0.025

    @property
    def cal_type(self) -> str:
        return "B"

    @property
    def representative_age(self) -> float:
        return (self.lower + self.upper) / 2.0

    def to_mcmctree(self) -> str:
        return f"B({self.lower},{self.upper},{self.p_lower},{self.p_upper})"

    def short_label(self) -> str:
        return f"B({self.lower},{self.upper})"


@dataclass
class LowerCalibration(CalibrationBase):
    """L(tL, p, c, pL) — minimum/lower age bound."""

    tL: float
    p: float = 0.1
    c: float = 1.0
    pL: float = 0.025

    @property
    def cal_type(self) -> str:
        return "L"

    @property
    def representative_age(self) -> float:
        return self.tL

    def to_mcmctree(self) -> str:
        return f"L({self.tL},{self.p},{self.c},{self.pL})"

    def short_label(self) -> str:
        return f"L({self.tL})"


@dataclass
class UpperCalibration(CalibrationBase):
    """U(tU, pR) — maximum/upper age bound."""

    tU: float
    pR: float = 0.025

    @property
    def cal_type(self) -> str:
        return "U"

    @property
    def representative_age(self) -> float:
        return self.tU

    def to_mcmctree(self) -> str:
        return f"U({self.tU},{self.pR})"

    def short_label(self) -> str:
        return f"U({self.tU})"


@dataclass
class GammaCalibration(CalibrationBase):
    """G(alpha, beta) — Gamma distribution."""

    alpha: float
    beta: float

    @property
    def cal_type(self) -> str:
        return "G"

    @property
    def representative_age(self) -> float:
        return self.alpha / self.beta if self.beta != 0 else 0.0

    def to_mcmctree(self) -> str:
        return f"G({self.alpha},{self.beta})"

    def short_label(self) -> str:
        return f"G({self.alpha},{self.beta})"


@dataclass
class SkewNormalCalibration(CalibrationBase):
    """SN(location, scale, shape) — Skew-normal distribution."""

    location: float
    scale: float
    shape: float

    @property
    def cal_type(self) -> str:
        return "SN"

    @property
    def representative_age(self) -> float:
        return self.location

    def to_mcmctree(self) -> str:
        return f"SN({self.location},{self.scale},{self.shape})"

    def short_label(self) -> str:
        return f"SN({self.location})"


@dataclass
class SkewTCalibration(CalibrationBase):
    """ST(location, scale, shape, df) — Skew-t distribution."""

    location: float
    scale: float
    shape: float
    df: float

    @property
    def cal_type(self) -> str:
        return "ST"

    @property
    def representative_age(self) -> float:
        return self.location

    def to_mcmctree(self) -> str:
        return f"ST({self.location},{self.scale},{self.shape},{self.df})"

    def short_label(self) -> str:
        return f"ST({self.location})"


@dataclass
class Skew2NormalsCalibration(CalibrationBase):
    """S2N(p1, loc1, scale1, shape1, loc2, scale2, shape2) — mixture of 2 skew-normals."""

    p1: float
    loc1: float
    scale1: float
    shape1: float
    loc2: float
    scale2: float
    shape2: float

    @property
    def cal_type(self) -> str:
        return "S2N"

    @property
    def representative_age(self) -> float:
        return self.p1 * self.loc1 + (1.0 - self.p1) * self.loc2

    def to_mcmctree(self) -> str:
        return (
            f"S2N({self.p1},{self.loc1},{self.scale1},{self.shape1},"
            f"{self.loc2},{self.scale2},{self.shape2})"
        )

    def short_label(self) -> str:
        return f"S2N({self.loc1},{self.loc2})"


# Backward compatibility alias
Calibration = BoundsCalibration


# ── Tree Nodes & PhyloTree ────────────────────────────────────────────────


@dataclass
class TreeNode:
    """A node in a phylogenetic tree."""

    node_id: int
    branch_len: Optional[float] = None
    tip_dist: Optional[float] = None
    name: Optional[str] = None
    children: list[TreeNode] = field(default_factory=list)
    parent: Optional[TreeNode] = None
    calibration: Optional[CalibrationBase] = None

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

    def compute_tip_distances(self) -> None:
        """Compute tip_dist for every node (max branch-length distance to any leaf).

        Requires branch_length attributes on nodes. Leaves get tip_dist=0.
        """
        def _compute(node: TreeNode) -> float:
            if node.is_leaf:
                node.tip_dist = 0.0
                return 0.0
            max_dist = 0.0
            for child in node.children:
                child_dist = _compute(child)
                bl = getattr(child, "branch_length", None) or 0.0
                max_dist = max(max_dist, bl + child_dist)
            node.tip_dist = max_dist
            return max_dist

        _compute(self.root)

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
            f"{'Clade Name':<45} {'Type':>4} {'Calibration':<30} {'#Taxa':>6}",
            "-" * 88,
        ]
        for entry in self.get_calibration_table():
            cal = entry["calibration"]
            lines.append(
                f"{entry['clade_name']:<45} {cal.cal_type:>4} {cal.short_label():<30} "
                f"{len(entry['taxa']):>6}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"PhyloTree(taxa={self.n_taxa}, calibrations={self.n_calibrations})"
