"""FossTree CLI — Fossil calibration annotation for Bayesian molecular dating.

Usage:
    python -m fosstree gui                          (launch GUI — default when no args)
    python -m fosstree info   <tree_file>
    python -m fosstree convert <tree_file> [-o output.xml] [--tree-ref REF] [--uniform-start N]
    python -m fosstree view   <tree_file> [-o output.pdf] [--theme light|dark] [--formats pdf svg png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_info(args: argparse.Namespace) -> None:
    """Print tree summary and calibration table."""
    from fosstree.utils import NewickParser

    parser = NewickParser()
    tree = parser.parse_file(args.tree_file)
    print(tree.summary())


def cmd_convert(args: argparse.Namespace) -> None:
    """Convert MCMCTree B() calibrations to BEAST2 MRCAPrior XML."""
    from fosstree.utils import NewickParser, BeastXMLGenerator

    parser = NewickParser()
    tree = parser.parse_file(args.tree_file)

    generator = BeastXMLGenerator(
        tree_ref=args.tree_ref,
        uniform_id_start=args.uniform_start,
    )

    if args.output:
        out = generator.write(tree, args.output)
        print(f"BEAST2 XML written to: {out}")
    else:
        print(generator.generate_full_xml(tree))


def cmd_view(args: argparse.Namespace) -> None:
    """Render tree visualization with calibration labels."""
    from fosstree.utils import NewickParser
    from fosstree.views import TreeVisualizer

    parser = NewickParser()
    tree = parser.parse_file(args.tree_file)

    viz = TreeVisualizer(
        theme=args.theme,
        fig_width=args.fig_width,
        dpi=args.dpi,
    )

    output = Path(args.output) if args.output else Path(args.tree_file).with_suffix(".pdf")
    title = f"{Path(args.tree_file).name} — Phylogenetic Tree with B() Fossil Calibrations"

    saved = viz.save(tree, output, title=title, formats=args.formats)
    for p in saved:
        print(f"Saved: {p}")


def cmd_gui(args: argparse.Namespace) -> None:
    """Launch the FossTree GUI application."""
    from fosstree.views.gui import run_gui

    run_gui()


def main(argv: list[str] | None = None) -> None:
    # Default to GUI when no arguments given
    if argv is None and len(sys.argv) == 1:
        cmd_gui(argparse.Namespace())
        return

    ap = argparse.ArgumentParser(
        prog="fosstree",
        description="FossTree — Fossil calibration annotation for Bayesian molecular dating",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    # ── gui ──
    p_gui = sub.add_parser("gui", help="Launch the graphical interface")


    # ── info ──
    p_info = sub.add_parser("info", help="Show tree summary and calibration table")
    p_info.add_argument("tree_file", help="Newick tree file with B() calibrations")

    # ── convert ──
    p_conv = sub.add_parser(
        "convert", help="Convert B() calibrations to BEAST2 MRCAPrior XML"
    )
    p_conv.add_argument("tree_file", help="Newick tree file with B() calibrations")
    p_conv.add_argument("-o", "--output", help="Output XML file (default: stdout)")
    p_conv.add_argument(
        "--tree-ref",
        default="@Tree.t:alignment",
        help="BEAST2 tree ID reference (default: @Tree.t:alignment)",
    )
    p_conv.add_argument(
        "--uniform-start",
        type=int,
        default=0,
        help="Starting index for Uniform distribution IDs (default: 0)",
    )

    # ── view ──
    p_view = sub.add_parser(
        "view", help="Render tree visualization with calibration labels"
    )
    p_view.add_argument("tree_file", help="Newick tree file with B() calibrations")
    p_view.add_argument(
        "-o", "--output", help="Output file path (default: <tree_file>.pdf)"
    )
    p_view.add_argument(
        "--theme",
        choices=["light", "dark"],
        default="light",
        help="Color theme (default: light)",
    )
    p_view.add_argument(
        "--formats",
        nargs="+",
        default=None,
        help="Output formats, e.g. pdf svg png (default: inferred from output path)",
    )
    p_view.add_argument(
        "--fig-width", type=float, default=20.0, help="Figure width in inches"
    )
    p_view.add_argument("--dpi", type=int, default=300, help="Output DPI")

    args = ap.parse_args(argv)

    commands = {
        "gui": cmd_gui,
        "info": cmd_info,
        "convert": cmd_convert,
        "view": cmd_view,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
