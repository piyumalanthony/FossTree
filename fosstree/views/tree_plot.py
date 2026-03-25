"""Phylogenetic tree visualization with fossil calibration labels."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from fosstree.models import PhyloTree, TreeNode


@dataclass
class PlotResult:
    """Data returned by TreeVisualizer.plot() for interactive use."""

    fig: object  # matplotlib Figure
    ax: object  # matplotlib Axes
    node_positions: dict[int, tuple[float, float]] = field(default_factory=dict)
    internal_nodes: list[TreeNode] = field(default_factory=list)


# ── Theme presets ──────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg": "#ffffff",
        "branch": "#404040",
        "leaf_text": "#111111",
        "label_text": "#222222",
        "label_edge_alpha": 0.7,
        "label_face_alpha": 0.25,
        "node_edge": "black",
        "arrow": "#999999",
        "title": "#111111",
        "cbar_label": "#333333",
    },
    "dark": {
        "bg": "#1e1e1e",
        "branch": "#aaaaaa",
        "leaf_text": "#e0e0e0",
        "label_text": "#eeeeee",
        "label_edge_alpha": 0.8,
        "label_face_alpha": 0.35,
        "node_edge": "#cccccc",
        "arrow": "#777777",
        "title": "#e0e0e0",
        "cbar_label": "#cccccc",
    },
}


class TreeVisualizer:
    """Renders a PhyloTree as a rectangular cladogram with calibration labels.

    Supports light/dark themes, PDF/SVG/PNG export, and configurable styling.
    """

    def __init__(
        self,
        theme: str = "light",
        fig_width: float = 20.0,
        font_size_leaf: int = 11,
        font_size_label: int = 8,
        line_width: float = 0.8,
        node_dot_size: int = 18,
        label_offset_x: float = 0.15,
        leaf_font: str = "monospace",
        cmap_name: str = "coolwarm",
        dpi: int = 300,
        show_branch_lengths: bool = False,
    ):
        if theme not in THEMES:
            raise ValueError(f"Unknown theme {theme!r}. Choose from: {list(THEMES)}")
        self.theme = THEMES[theme]
        self.theme_name = theme
        self.fig_width = fig_width
        self.font_size_leaf = font_size_leaf
        self.font_size_label = font_size_label
        self.line_width = line_width
        self.node_dot_size = node_dot_size
        self.label_offset_x = label_offset_x
        self.leaf_font = leaf_font
        self.cmap = cm.get_cmap(cmap_name)
        self.dpi = dpi
        self.show_branch_lengths = show_branch_lengths

    # ── Layout computation ─────────────────────────────────────────────

    @staticmethod
    def _compute_depth(root: TreeNode) -> dict[int, int]:
        """BFS depth (edges from root) for every node."""
        depth = {root.node_id: 0}
        queue = [root]
        while queue:
            node = queue.pop(0)
            for child in node.children:
                depth[child.node_id] = depth[node.node_id] + 1
                queue.append(child)
        return depth

    def _compute_layout(
        self, tree: PhyloTree, scaled: bool = False,
    ) -> tuple[dict[int, tuple[float, float]], float]:
        """Compute (x, y) positions for every node.

        When scaled=False (cladogram):
            X = integer depth; all leaves aligned at max_depth.
        When scaled=True (phylogram):
            X = cumulative branch length from root; leaves at varying positions.

        Y = leaf traversal order in both modes.
        Internal nodes: y = mean of children y values.

        Returns:
            pos: {node_id: (x, y)}
            max_x: maximum x value across all nodes
        """
        leaf_y: dict[int, int] = {}
        for idx, leaf in enumerate(tree.root.traverse_leaves()):
            leaf_y[leaf.node_id] = idx

        pos: dict[int, tuple[float, float]] = {}

        if scaled:
            # Phylogram: x = cumulative branch length from root
            def assign_scaled(node: TreeNode, parent_x: float) -> float:
                bl = node.branch_len or 0.0
                x = parent_x + bl
                if node.is_leaf:
                    y = float(leaf_y[node.node_id])
                    pos[node.node_id] = (x, y)
                    return y
                child_ys = [assign_scaled(c, x) for c in node.children]
                y = sum(child_ys) / len(child_ys)
                pos[node.node_id] = (x, y)
                return y

            assign_scaled(tree.root, 0.0)
        else:
            # Cladogram: x = integer depth, leaves all at max_depth
            depth = self._compute_depth(tree.root)
            max_depth = max(depth.values())

            def assign_clado(node: TreeNode) -> float:
                if node.is_leaf:
                    y = leaf_y[node.node_id]
                    pos[node.node_id] = (float(max_depth), float(y))
                    return float(y)
                child_ys = [assign_clado(c) for c in node.children]
                y = sum(child_ys) / len(child_ys)
                pos[node.node_id] = (float(depth[node.node_id]), y)
                return y

            assign_clado(tree.root)

        max_x = max(x for x, _ in pos.values())
        return pos, max_x

    # ── Drawing ────────────────────────────────────────────────────────

    def plot(
        self,
        tree: PhyloTree,
        title: Optional[str] = None,
        ax: Optional[plt.Axes] = None,
    ) -> PlotResult:
        """Draw the phylogenetic tree with calibration labels.

        Args:
            tree: PhyloTree to render.
            title: Optional plot title.
            ax: Optional matplotlib Axes to draw on.

        Returns:
            PlotResult with fig, ax, node positions, and internal node list.
        """
        t = self.theme
        n_taxa = tree.n_taxa

        # Check if tree has branch lengths
        has_branch_lengths = any(
            n.branch_len is not None
            for n in tree.root.traverse_preorder()
            if not n.is_root
        )

        scaled = self.show_branch_lengths and has_branch_lengths
        pos, max_x = self._compute_layout(tree, scaled=scaled)

        # Collect internal nodes for interactive use
        internal_nodes = [
            n for n in tree.root.traverse_preorder() if not n.is_leaf
        ]

        # Create figure if not provided
        if ax is None:
            fig_height = max(12, n_taxa * 0.35)
            fig, ax = plt.subplots(figsize=(self.fig_width, fig_height))
        else:
            fig = ax.figure

        ax.set_facecolor(t["bg"])
        fig.set_facecolor(t["bg"])

        # Calibration color mapping
        cal_nodes = tree.calibrated_nodes
        if cal_nodes:
            ages = [n.calibration.midpoint for n in cal_nodes]
            norm = mcolors.Normalize(vmin=min(ages), vmax=max(ages))

        # ── Branches (rectangular / right-angle) ──
        for node in tree.root.traverse_preorder():
            if node.is_leaf:
                continue
            px, py = pos[node.node_id]
            child_ys = [pos[c.node_id][1] for c in node.children]
            # Vertical connector
            ax.plot(
                [px, px],
                [min(child_ys), max(child_ys)],
                color=t["branch"],
                linewidth=self.line_width,
                solid_capstyle="round",
            )
            # Horizontal connectors
            for child in node.children:
                cx, cy = pos[child.node_id]
                ax.plot(
                    [px, cx],
                    [cy, cy],
                    color=t["branch"],
                    linewidth=self.line_width,
                    solid_capstyle="round",
                )

        # ── Branch length labels ──
        if self.show_branch_lengths and has_branch_lengths:
            for node in tree.root.traverse_preorder():
                if node.is_root:
                    continue
                bl = node.branch_len
                if bl is None:
                    continue
                nx, ny = pos[node.node_id]
                px_parent, _ = pos[node.parent.node_id]
                mid_x = (px_parent + nx) / 2.0
                ax.text(
                    mid_x,
                    ny - 0.15,
                    f"{bl:.4g}",
                    fontsize=self.font_size_label - 1,
                    color=t["branch"],
                    ha="center",
                    va="top",
                    alpha=0.7,
                )

        # ── Leaf labels ──
        for leaf in tree.root.traverse_leaves():
            lx, ly = pos[leaf.node_id]
            display_name = (leaf.name or "").replace("_", " ")

            if scaled and lx < max_x:
                # Phylogram: draw dotted guide line from leaf tip to aligned label
                ax.plot(
                    [lx, max_x],
                    [ly, ly],
                    color=t["branch"],
                    linewidth=self.line_width * 0.5,
                    linestyle=":",
                    alpha=0.3,
                )
                label_x = max_x + 0.2
            else:
                label_x = lx + 0.2

            ax.text(
                label_x,
                ly,
                display_name,
                fontsize=self.font_size_leaf,
                fontfamily=self.leaf_font,
                va="center",
                ha="left",
                fontstyle="italic",
                color=t["leaf_text"],
            )

        # ── Internal node dots (all — small grey for uncalibrated) ──
        for node in internal_nodes:
            nx, ny = pos[node.node_id]
            if node.calibration is None:
                ax.scatter(
                    [nx], [ny],
                    s=self.node_dot_size * 0.6,
                    color=t["branch"],
                    alpha=0.35,
                    edgecolors="none",
                    zorder=4,
                )

        # ── Calibration labels ──
        sorted_cals = sorted(cal_nodes, key=lambda n: pos[n.node_id][1])
        for idx, node in enumerate(sorted_cals, 1):
            nx, ny = pos[node.node_id]
            cal = node.calibration
            color = self.cmap(norm(cal.midpoint))

            # Colored dot
            ax.scatter(
                [nx],
                [ny],
                s=self.node_dot_size,
                color=color,
                edgecolors=t["node_edge"],
                linewidths=0.4,
                zorder=5,
            )

            # Label
            label = f"[{idx}] {cal.short_label()}"
            ax.annotate(
                label,
                xy=(nx, ny),
                xytext=(nx - self.label_offset_x, ny + 0.35),
                fontsize=self.font_size_label,
                color=t["label_text"],
                fontweight="bold",
                ha="right",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    facecolor=mcolors.to_rgba(color, alpha=t["label_face_alpha"]),
                    edgecolor=mcolors.to_rgba(color, alpha=t["label_edge_alpha"]),
                    linewidth=0.6,
                ),
                arrowprops=dict(
                    arrowstyle="-",
                    color=t["arrow"],
                    linewidth=0.4,
                ),
                zorder=6,
            )

        # ── Axes styling ──
        ax.set_xlim(-max_x * 0.1, max_x + 4.5)
        ax.set_ylim(-1, n_taxa)
        ax.invert_yaxis()
        ax.axis("off")

        # Colorbar
        if cal_nodes:
            sm = cm.ScalarMappable(cmap=self.cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.3, aspect=20, pad=0.01)
            cbar.set_label(
                "Calibration midpoint (Ma/Ga)",
                fontsize=7,
                color=t["cbar_label"],
            )
            cbar.ax.tick_params(labelsize=6, colors=t["cbar_label"])
            cbar.outline.set_edgecolor(t["cbar_label"])

        if title:
            ax.set_title(
                title,
                fontsize=11,
                fontweight="bold",
                pad=15,
                color=t["title"],
            )

        plt.tight_layout()
        return PlotResult(
            fig=fig,
            ax=ax,
            node_positions=pos,
            internal_nodes=internal_nodes,
        )

    def save(
        self,
        tree: PhyloTree,
        output_path: str | Path,
        title: Optional[str] = None,
        formats: Optional[list[str]] = None,
    ) -> list[Path]:
        """Render and save the tree to one or more file formats.

        Args:
            tree: PhyloTree to render.
            output_path: Base output path (extension determines default format).
            title: Optional plot title.
            formats: List of formats to save (e.g. ["pdf", "svg", "png"]).
                     If None, inferred from output_path extension.

        Returns:
            List of saved file paths.
        """
        path = Path(output_path)
        if formats is None:
            formats = [path.suffix.lstrip(".") or "pdf"]

        result = self.plot(tree, title=title)

        saved: list[Path] = []
        for fmt in formats:
            out = path.with_suffix(f".{fmt}")
            result.fig.savefig(
                str(out),
                bbox_inches="tight",
                dpi=self.dpi,
                facecolor=self.theme["bg"],
            )
            saved.append(out.resolve())

        plt.close(result.fig)
        return saved
