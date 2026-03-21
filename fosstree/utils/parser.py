"""Newick tree parser with MCMCTree B() calibration support."""

from __future__ import annotations

import re
from pathlib import Path

from fosstree.models import TreeNode, Calibration, PhyloTree


class NewickParser:
    """Parses Newick format strings with MCMCTree B() calibration annotations.

    Supports format: ((A,B)'B(lower,upper,p1,p2)',C);
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

        Args:
            newick_str: Newick format string, optionally with B() annotations.
            source: Optional label for the tree source (e.g. filename).

        Returns:
            PhyloTree object with nodes and calibrations attached.
        """
        self._node_counter = 0
        s = newick_str.strip().rstrip(";")

        root = self._new_node()
        stack = [root]
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
                # Check for 'B(...)' annotation
                if i < len(s) and s[i] == "'":
                    end_quote = s.index("'", i + 1)
                    annotation = s[i + 1 : end_quote]
                    m = re.match(
                        r"B\(([\d.]+),([\d.]+)(?:,([\d.]+),([\d.]+))?\)", annotation
                    )
                    if m:
                        closed.calibration = Calibration(
                            lower=float(m.group(1)),
                            upper=float(m.group(2)),
                            p_lower=float(m.group(3)) if m.group(3) else 0.001,
                            p_upper=float(m.group(4)) if m.group(4) else 0.025,
                        )
                    i = end_quote + 1
                # Skip optional branch length
                if i < len(s) and s[i] == ":":
                    i += 1
                    while i < len(s) and s[i] not in "(),';":
                        i += 1

            elif c == ":":
                # Skip branch length
                i += 1
                while i < len(s) and s[i] not in "(),';":
                    i += 1

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
                i = j

        return PhyloTree(root, source=source)

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
