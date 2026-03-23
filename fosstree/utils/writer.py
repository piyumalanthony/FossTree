"""Newick tree writer with MCMCTree calibration annotations."""

from __future__ import annotations

from pathlib import Path

from fosstree.models import PhyloTree, TreeNode


class NewickWriter:
    """Serializes a PhyloTree back to Newick format with MCMCTree calibrations.

    Output format matches MCMCTree:
        ((A,B)'B(lower,upper,p_lower,p_upper)',C)'L(tL,p,c,pL)';
    """

    def _node_to_newick(self, node: TreeNode) -> str:
        if node.is_leaf:
            return node.name or ""

        children_str = ",".join(
            self._node_to_newick(child) for child in node.children
        )
        result = f"({children_str})"

        if node.calibration:
            result += f"'{node.calibration.to_mcmctree()}'"

        return result

    def to_string(self, tree: PhyloTree) -> str:
        """Serialize a PhyloTree to a Newick string with calibration annotations.

        Args:
            tree: The PhyloTree to serialize.

        Returns:
            Newick string ending with ';'
        """
        return self._node_to_newick(tree.root) + ";\n"

    def write_file(self, tree: PhyloTree, output_path: str | Path) -> Path:
        """Write the tree to a Newick file.

        Args:
            tree: The PhyloTree to serialize.
            output_path: Destination file path.

        Returns:
            The resolved output path.
        """
        path = Path(output_path)
        path.write_text(self.to_string(tree), encoding="utf-8")
        return path.resolve()
