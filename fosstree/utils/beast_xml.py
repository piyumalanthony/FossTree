"""BEAST2 MRCAPrior XML generator from PhyloTree calibrations."""

from __future__ import annotations

from pathlib import Path

from fosstree.models import (
    CalibrationBase,
    BoundsCalibration,
    LowerCalibration,
    UpperCalibration,
    GammaCalibration,
    PhyloTree,
)


class BeastXMLGenerator:
    """Generates BEAST2 MRCAPrior XML blocks from a calibrated PhyloTree.

    Produces:
      - Taxon set + MRCAPrior distribution blocks (for the <prior> section)
      - Log idref entries (for the <tracelog> section)
    """

    def __init__(self, tree_ref: str = "@Tree.t:alignment", uniform_id_start: int = 0):
        """
        Args:
            tree_ref: BEAST2 tree ID reference (e.g. "@Tree.t:alignment").
            uniform_id_start: Starting index for distribution IDs.
        """
        self.tree_ref = tree_ref
        self.uniform_id_start = uniform_id_start

    def _generate_distribution_xml(
        self, cal: CalibrationBase, uid: int, indent: str = "                    "
    ) -> tuple[str, str]:
        """Generate the BEAST2 distribution XML element for a calibration.

        Returns:
            Tuple of (xml_element, warning_comment). warning_comment is empty
            if the mapping is exact.
        """
        if isinstance(cal, BoundsCalibration):
            xml = (
                f'{indent}<Uniform id="Uniform.{uid}" '
                f'lower="{cal.lower}" name="distr" upper="{cal.upper}"/>'
            )
            return xml, ""

        if isinstance(cal, UpperCalibration):
            xml = (
                f'{indent}<Uniform id="Uniform.{uid}" '
                f'lower="0.0" name="distr" upper="{cal.tU}"/>'
            )
            return xml, ""

        if isinstance(cal, GammaCalibration):
            scale = 1.0 / cal.beta if cal.beta != 0 else 1.0
            xml = (
                f'{indent}<Gamma id="Gamma.{uid}" name="distr">\n'
                f'{indent}    <parameter name="alpha">{cal.alpha}</parameter>\n'
                f'{indent}    <parameter name="beta">{scale}</parameter>\n'
                f'{indent}</Gamma>'
            )
            return xml, ""

        if isinstance(cal, LowerCalibration):
            xml = (
                f'{indent}<Exponential id="Exponential.{uid}" name="distr" offset="{cal.tL}">\n'
                f'{indent}    <parameter name="mean">1.0</parameter>\n'
                f'{indent}</Exponential>'
            )
            warning = (
                f"{indent}<!-- WARNING: {cal.to_mcmctree()} approximated as "
                f"Exponential with offset. Review parameters. -->"
            )
            return xml, warning

        # SN, ST, S2N — no direct BEAST2 equivalent
        age = cal.representative_age
        xml = (
            f'{indent}<Uniform id="Uniform.{uid}" '
            f'lower="0.0" name="distr" upper="{age * 2}"/>'
        )
        warning = (
            f"{indent}<!-- WARNING: {cal.to_mcmctree()} has no direct BEAST2 equivalent. "
            f"Using placeholder Uniform(0, {age * 2}). Review and replace. -->"
        )
        return xml, warning

    def generate(self, tree: PhyloTree) -> tuple[str, str]:
        """Generate BEAST2 XML blocks from the tree's calibrations.

        Args:
            tree: A PhyloTree with calibrated nodes.

        Returns:
            Tuple of (prior_xml, log_xml) strings.
        """
        calib_table = tree.get_calibration_table()
        seen_taxa: set[str] = set()
        prior_lines: list[str] = []
        log_lines: list[str] = []
        uid = self.uniform_id_start

        for entry in calib_table:
            clade_name = entry["clade_name"]
            cal = entry["calibration"]
            taxa = entry["taxa"]

            prior_lines.append(
                f'                <distribution id="{clade_name}.prior" '
                f'spec="beast.base.evolution.tree.MRCAPrior" '
                f'monophyletic="true" tree="{self.tree_ref}">'
            )
            prior_lines.append(
                f'                    <taxonset id="{clade_name}" spec="TaxonSet">'
            )

            for taxon in taxa:
                if taxon not in seen_taxa:
                    prior_lines.append(
                        f'                        <taxon id="{taxon}" spec="Taxon"/>'
                    )
                    seen_taxa.add(taxon)
                else:
                    prior_lines.append(
                        f'                        <taxon idref="{taxon}"/>'
                    )

            prior_lines.append("                    </taxonset>")

            dist_xml, warning = self._generate_distribution_xml(cal, uid)
            if warning:
                prior_lines.append(warning)
            prior_lines.append(dist_xml)

            prior_lines.append("                </distribution>")
            prior_lines.append("")

            log_lines.append(f'            <log idref="{clade_name}.prior"/>')
            uid += 1

        return "\n".join(prior_lines), "\n".join(log_lines)

    def generate_full_xml(self, tree: PhyloTree) -> str:
        """Generate a complete XML snippet with comment headers.

        Args:
            tree: A PhyloTree with calibrated nodes.

        Returns:
            Complete XML string ready to paste into a BEAST2 XML file.
        """
        prior_xml, log_xml = self.generate(tree)
        parts = [
            "<!-- MRCA Prior blocks -->",
            "<!-- Paste inside <distribution id='prior' ...> block -->",
            prior_xml,
            "",
            "<!-- Log entries -->",
            "<!-- Paste inside <logger id='tracelog' ...> block -->",
            log_xml,
        ]
        return "\n".join(parts)

    def write(self, tree: PhyloTree, output_path: str | Path) -> Path:
        """Generate and write BEAST2 XML to a file.

        Args:
            tree: A PhyloTree with calibrated nodes.
            output_path: Destination file path.

        Returns:
            The resolved output path.
        """
        path = Path(output_path)
        path.write_text(self.generate_full_xml(tree), encoding="utf-8")
        return path.resolve()
