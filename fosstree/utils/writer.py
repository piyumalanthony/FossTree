"""Newick tree writer with MCMCTree calibration annotations."""

from __future__ import annotations

from pathlib import Path

from fosstree.models import PhyloTree, TreeNode


class NewickWriter:
    """Serializes a PhyloTree back to Newick format with MCMCTree calibrations.

    Output format matches MCMCTree:
        ((A,B)'B(lower,upper,p_lower,p_upper)',C)'L(tL,p,c,pL)';
    """

    def _node_to_newick(self, node: TreeNode, include_branch_lengths: bool) -> str:
        if node.is_leaf:
            result = node.name or ""
            if include_branch_lengths and node.branch_len is not None:
                result += f":{node.branch_len}"
            return result

        children_str = ",".join(
            self._node_to_newick(child, include_branch_lengths)
            for child in node.children
        )
        result = f"({children_str})"

        if node.calibration:
            result += f"'{node.calibration.to_mcmctree()}'"

        if include_branch_lengths and node.branch_len is not None:
            result += f":{node.branch_len}"

        return result

    def to_string(self, tree: PhyloTree, include_branch_lengths: bool = False) -> str:
        """Serialize a PhyloTree to a Newick string with calibration annotations.

        Args:
            tree: The PhyloTree to serialize.
            include_branch_lengths: If True, include branch lengths in the output.

        Returns:
            Newick string ending with ';'
        """
        return self._node_to_newick(tree.root, include_branch_lengths) + ";\n"

    def write_file(
        self, tree: PhyloTree, output_path: str | Path,
        include_branch_lengths: bool = False,
    ) -> Path:
        """Write the tree to a Newick file.

        Args:
            tree: The PhyloTree to serialize.
            output_path: Destination file path.
            include_branch_lengths: If True, include branch lengths in the output.

        Returns:
            The resolved output path.
        """
        path = Path(output_path)
        path.write_text(
            self.to_string(tree, include_branch_lengths), encoding="utf-8"
        )
        return path.resolve()
