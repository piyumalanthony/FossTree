"""Newick tree parser with MCMCTree calibration support."""

from __future__ import annotations

import re
import warnings
from pathlib import Path

from fosstree.models import TreeNode, PhyloTree
from fosstree.utils.calibration_parser import parse_calibration

# MCMCTree header: e.g. "16 1" meaning 16 taxa, 1 tree
_MCMCTREE_HEADER = re.compile(r"^\s*(\d+)\s+(\d+)\s*$")


class NewickParser:
    """Parses Newick format strings with MCMCTree calibration annotations.

    Supports format: ((A,B)'B(lower,upper,p1,p2)',C);
    Also supports L(), U(), G(), SN(), ST(), S2N() calibration types.
    Branch lengths after ':' are recorded but not used in cladogram layout.
    """

    def __init__(self):
        self._node_counter = 0

    def _new_node(self) -> TreeNode:
        node = TreeNode(node_id=self._node_counter)
        self._node_counter += 1
        return node

    def parse_string(self, newick_str: str, source: str = "") -> PhyloTree:
        """Parse a Newick string into a PhyloTree.

        Accepts plain Newick or MCMCTree format (header line + tree).
        If the input does not start with '(' it will attempt to detect
        MCMCTree format (e.g. "16 1\\n((...));") and extract the tree.

        Args:
            newick_str: Newick format string, optionally with calibration annotations.
            source: Optional label for the tree source (e.g. filename).

        Returns:
            PhyloTree object with nodes and calibrations attached.

        Raises:
            ValueError: If the string is not valid Newick or MCMCTree format.
        """
        self._node_counter = 0
        s = newick_str.strip()

        # Handle input that doesn't start with '('
        if not s.startswith("("):
            s = self._extract_newick(s, source)

        s = s.rstrip(";")

        root = self._new_node()
        stack = [root]
        last_leaf = None
        i = 1  # skip opening '('

        while i < len(s):
            c = s[i]

            if c == "(":
                node = self._new_node()
                node.parent = stack[-1]
                stack[-1].children.append(node)
                stack.append(node)
                i += 1

            elif c == ",":
                i += 1

            elif c == ")":
                closed = stack.pop()
                i += 1
                # Check for calibration annotation in quotes
                if i < len(s) and s[i] == "'":
                    end_quote = s.index("'", i + 1)
                    annotation = s[i + 1 : end_quote]
                    cal = parse_calibration(annotation)
                    if cal is not None:
                        closed.calibration = cal
                    i = end_quote + 1
                # Skip optional branch length
                if i < len(s) and s[i] == ":":
                    start_br = i
                    i += 1
                    while i < len(s) and s[i] not in "(),';":
                        i += 1
                    m_br  =  re.search(r":(\d+\.?\d*(?:[eE][+-]?\d+)?)", s[start_br:i + 1])
                    if m_br:
                        closed.branch_len = float(m_br.group(1))

            elif c == ":":
                # Leaf branch length
                start_br = i
                i += 1
                while i < len(s) and s[i] not in "(),';":
                    i += 1
                if last_leaf is not None:
                    m_br = re.search(r":(\d+\.?\d*(?:[eE][+-]?\d+)?)", s[start_br:i + 1])
                    if m_br:
                        last_leaf.branch_len = float(m_br.group(1))
                    last_leaf = None

            else:
                # Taxon name
                j = i
                while j < len(s) and s[j] not in "(),':\"":
                    j += 1
                name = s[i:j].strip()
                if name:
                    leaf = self._new_node()
                    leaf.name = name
                    leaf.parent = stack[-1]
                    stack[-1].children.append(leaf)
                    last_leaf = leaf
                i = j

        tree = PhyloTree(root, source=source)

        # Compute tip distances if branch lengths are available
        has_bl = any(
            n.branch_len is not None
            for n in root.traverse_preorder()
            if not n.is_root
        )
        if has_bl:
            tree.compute_tip_distances()

        return tree

    @staticmethod
    def _extract_newick(text: str, source: str = "") -> str:
        """Extract the Newick tree string from text that doesn't start with '('.

        Detects MCMCTree format (header like '16 1' followed by tree) and
        raises ValueError for unrecognised formats.
        """
        lines = text.splitlines()
        first_line = lines[0].strip() if lines else ""

        # Check for MCMCTree header: "N_taxa  N_trees"
        m = _MCMCTREE_HEADER.match(first_line)
        if m:
            n_taxa, n_trees = int(m.group(1)), int(m.group(2))
            warnings.warn(
                f"This is not a plain Newick file — detected MCMCTree format "
                f"with {n_taxa} taxa and {n_trees} tree(s). "
                f"Reading tree from the first '(' character.",
                stacklevel=3,
            )
            # Find the tree starting from '('
            rest = text[text.index("\n") + 1:] if "\n" in text else ""
            paren_pos = rest.find("(")
            if paren_pos == -1:
                raise ValueError(
                    f"MCMCTree header found ({n_taxa} taxa, {n_trees} tree) "
                    f"but no tree string starting with '(' was found."
                )
            return rest[paren_pos:].strip()

        # Not MCMCTree header either — genuinely invalid
        raise ValueError(
            f"Not a valid Newick format: tree string must start with '('. "
            f"Got: {first_line[:60]!r}"
        )

    def parse_file(self, filepath: str | Path) -> PhyloTree:
        """Parse a Newick tree file.

        Args:
            filepath: Path to a file containing a single Newick tree string.

        Returns:
            PhyloTree object.
        """
        path = Path(filepath)
        text = path.read_text(encoding="utf-8").strip()
        return self.parse_string(text, source=path.name)
