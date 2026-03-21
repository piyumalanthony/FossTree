"""FossTree GUI — PyQt5 application for fossil calibration workflow."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from fosstree.models import Calibration, PhyloTree, TreeNode
from fosstree.utils import BeastXMLGenerator, NewickParser, NewickWriter
from fosstree.views.tree_plot import PlotResult, TreeVisualizer


# ── Calibration Dialog ─────────────────────────────────────────────────────


class CalibrationDialog(QDialog):
    """Popup dialog for adding/editing a fossil calibration on an internal node."""

    def __init__(self, node: TreeNode, parent=None):
        super().__init__(parent)
        self.node = node
        self.result_calibration: Optional[Calibration] = None

        self.setWindowTitle("Add / Edit Fossil Calibration")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Node info
        leaves = node.get_leaf_names()
        n = len(leaves)
        if n <= 6:
            taxa_str = ", ".join(leaves)
        else:
            taxa_str = ", ".join(leaves[:3]) + f" ... ({n} total) ... " + ", ".join(leaves[-3:])

        info_label = QLabel(f"Node ID: {node.node_id}  |  Descendant taxa: {n}\n{taxa_str}")
        info_label.setWordWrap(True)
        info_label.setFont(QFont("monospace", 9))
        info_label.setStyleSheet("background: #f0f0f0; padding: 8px; border-radius: 4px;")
        layout.addWidget(info_label)

        # Current calibration
        if node.calibration:
            cur = node.calibration
            cur_label = QLabel(f"Current: B({cur.lower},{cur.upper},{cur.p_lower},{cur.p_upper})")
            cur_label.setStyleSheet("color: #0066cc; font-weight: bold;")
            layout.addWidget(cur_label)

        # Input
        layout.addWidget(QLabel("Enter calibration string (MCMCTree format):"))

        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("monospace", 12))
        if node.calibration:
            cal = node.calibration
            self.input_field.setText(f"B({cal.lower},{cal.upper},{cal.p_lower},{cal.p_upper})")
        else:
            self.input_field.setPlaceholderText("B(lower,upper,p_lower,p_upper)  e.g. B(5.29,6.361,0.001,0.025)")
        layout.addWidget(self.input_field)

        # Help text
        help_label = QLabel(
            "Format: B(lower, upper[, p_lower, p_upper])\n"
            "  lower  = minimum age constraint\n"
            "  upper  = maximum age constraint\n"
            "  p_lower, p_upper = tail probabilities (default: 0.001, 0.025)"
        )
        help_label.setFont(QFont("monospace", 8))
        help_label.setStyleSheet("color: #666;")
        layout.addWidget(help_label)

        # Buttons
        btn_box = QDialogButtonBox()
        self.btn_apply = btn_box.addButton("Apply", QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_remove = btn_box.addButton("Remove Calibration", QDialogButtonBox.ButtonRole.DestructiveRole)
        self.btn_cancel = btn_box.addButton(QDialogButtonBox.StandardButton.Cancel)

        self.btn_remove.setEnabled(node.calibration is not None)

        btn_box.accepted.connect(self._apply)
        btn_box.rejected.connect(self.reject)
        self.btn_remove.clicked.connect(self._remove)

        layout.addWidget(btn_box)

    def _parse_input(self) -> Optional[Calibration]:
        text = self.input_field.text().strip()
        m = re.match(
            r"B\(\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*,\s*([\d.]+)\s*)?\)",
            text,
        )
        if not m:
            return None
        return Calibration(
            lower=float(m.group(1)),
            upper=float(m.group(2)),
            p_lower=float(m.group(3)) if m.group(3) else 0.001,
            p_upper=float(m.group(4)) if m.group(4) else 0.025,
        )

    def _apply(self) -> None:
        cal = self._parse_input()
        if cal is None:
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Could not parse calibration string.\n"
                "Expected: B(lower,upper) or B(lower,upper,p_lower,p_upper)",
            )
            return
        if cal.lower >= cal.upper:
            QMessageBox.warning(
                self, "Invalid Range", "Lower bound must be less than upper bound."
            )
            return
        self.result_calibration = cal
        self.accept()

    def _remove(self) -> None:
        self.result_calibration = None
        self.done(2)  # custom return code for "remove"


# ── Info Tabs ──────────────────────────────────────────────────────────────


class TreeInfoTab(QWidget):
    """Phase 2: Display tree summary and calibration table."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.stats_label = QLabel("No tree loaded.")
        self.stats_label.setFont(QFont("monospace", 11))
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Clade Name", "Lower", "Upper", "# Taxa"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_tree(self, tree: PhyloTree) -> None:
        self.stats_label.setText(
            f"Source: {tree.source}\n"
            f"Taxa: {tree.n_taxa}    "
            f"Calibrations: {tree.n_calibrations}    "
            f"Max depth: {tree.max_depth()}"
        )
        calib_table = tree.get_calibration_table()
        self.table.setRowCount(len(calib_table))
        for row, entry in enumerate(calib_table):
            cal = entry["calibration"]
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(entry["clade_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{cal.lower:.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{cal.upper:.4f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(len(entry["taxa"]))))
            for col in (0, 2, 3, 4):
                item = self.table.item(row, col)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def clear(self) -> None:
        self.stats_label.setText("No tree loaded.")
        self.table.setRowCount(0)


class ConvertTab(QWidget):
    """Phase 3: Convert calibrations to BEAST2 MRCAPrior XML."""

    def __init__(self):
        super().__init__()
        self.tree: Optional[PhyloTree] = None
        layout = QVBoxLayout(self)

        opts = QGroupBox("Conversion Options")
        opts_layout = QHBoxLayout(opts)
        opts_layout.addWidget(QLabel("Tree Ref:"))
        self.tree_ref_input = QLineEdit("@Tree.t:alignment")
        self.tree_ref_input.setMinimumWidth(250)
        opts_layout.addWidget(self.tree_ref_input)
        opts_layout.addWidget(QLabel("Uniform ID Start:"))
        self.uniform_start = QSpinBox()
        self.uniform_start.setRange(0, 9999)
        self.uniform_start.setValue(0)
        opts_layout.addWidget(self.uniform_start)
        opts_layout.addStretch()
        layout.addWidget(opts)

        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton("Generate XML")
        self.btn_generate.clicked.connect(self._generate)
        self.btn_generate.setEnabled(False)
        btn_layout.addWidget(self.btn_generate)
        self.btn_save = QPushButton("Save XML to File...")
        self.btn_save.clicked.connect(self._save)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy)
        self.btn_copy.setEnabled(False)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.xml_output = QTextEdit()
        self.xml_output.setReadOnly(True)
        self.xml_output.setFont(QFont("monospace", 10))
        self.xml_output.setPlaceholderText("Generated BEAST2 XML will appear here...")
        layout.addWidget(self.xml_output)

    def load_tree(self, tree: PhyloTree) -> None:
        self.tree = tree
        self.btn_generate.setEnabled(True)
        self.xml_output.clear()
        self.btn_save.setEnabled(False)
        self.btn_copy.setEnabled(False)

    def clear(self) -> None:
        self.tree = None
        self.btn_generate.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_copy.setEnabled(False)
        self.xml_output.clear()

    def _make_generator(self) -> BeastXMLGenerator:
        return BeastXMLGenerator(
            tree_ref=self.tree_ref_input.text(),
            uniform_id_start=self.uniform_start.value(),
        )

    def _generate(self) -> None:
        if not self.tree:
            return
        xml = self._make_generator().generate_full_xml(self.tree)
        self.xml_output.setPlainText(xml)
        self.btn_save.setEnabled(True)
        self.btn_copy.setEnabled(True)

    def _save(self) -> None:
        if not self.tree:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save BEAST2 XML", "mrca_priors.xml", "XML Files (*.xml);;All (*)"
        )
        if path:
            out = self._make_generator().write(self.tree, path)
            QMessageBox.information(self, "Saved", f"XML saved to:\n{out}")

    def _copy(self) -> None:
        text = self.xml_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)


# ── Scrollable / Zoomable Canvas ───────────────────────────────────────────


class ZoomableScrollCanvas(QScrollArea):
    """Scrollable area with Ctrl+scroll zoom for a matplotlib FigureCanvas."""

    ZOOM_FACTOR = 1.15
    MIN_ZOOM = 0.2
    MAX_ZOOM = 5.0

    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.canvas = FigureCanvas(figure)
        self._zoom = 1.0
        self._base_width = 0
        self._base_height = 0

        self.setWidget(self.canvas)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_base_size(self, width_px: int, height_px: int) -> None:
        self._base_width = width_px
        self._base_height = height_px
        self._zoom = 1.0
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        w = int(self._base_width * self._zoom)
        h = int(self._base_height * self._zoom)
        self.canvas.setFixedSize(w, h)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                new_zoom = self._zoom * self.ZOOM_FACTOR
            elif delta < 0:
                new_zoom = self._zoom / self.ZOOM_FACTOR
            else:
                return
            new_zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, new_zoom))
            if new_zoom == self._zoom:
                return

            old_pos = event.pos()
            hbar = self.horizontalScrollBar()
            vbar = self.verticalScrollBar()
            old_hval = hbar.value() + old_pos.x()
            old_vval = vbar.value() + old_pos.y()

            ratio = new_zoom / self._zoom
            self._zoom = new_zoom
            self._apply_zoom()

            hbar.setValue(int(old_hval * ratio) - old_pos.x())
            vbar.setValue(int(old_vval * ratio) - old_pos.y())
            event.accept()
        else:
            super().wheelEvent(event)

    @property
    def zoom_percent(self) -> int:
        return int(self._zoom * 100)


# ── View Tab (interactive) ─────────────────────────────────────────────────


class ViewTab(QWidget):
    """Phase 4: Interactive tree visualization with node selection and calibration editing."""

    # Callback signature for when tree is modified (so main window can refresh other tabs)
    on_tree_modified = None  # set by FossTreeMainWindow

    def __init__(self):
        super().__init__()
        self.tree: Optional[PhyloTree] = None
        self._screen_dpi = 100
        self._plot_result: Optional[PlotResult] = None
        self._hover_node: Optional[TreeNode] = None
        self._mpl_cids: list = []

        layout = QVBoxLayout(self)

        # ── Options ──
        opts = QGroupBox("Visualization Options")
        opts_layout = QHBoxLayout(opts)
        opts_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.currentTextChanged.connect(self._on_option_changed)
        opts_layout.addWidget(self.theme_combo)
        opts_layout.addWidget(QLabel("Font (leaves):"))
        self.font_leaf = QSpinBox()
        self.font_leaf.setRange(6, 24)
        self.font_leaf.setValue(11)
        self.font_leaf.valueChanged.connect(self._on_option_changed)
        opts_layout.addWidget(self.font_leaf)
        opts_layout.addWidget(QLabel("Font (labels):"))
        self.font_label = QSpinBox()
        self.font_label.setRange(5, 18)
        self.font_label.setValue(8)
        self.font_label.valueChanged.connect(self._on_option_changed)
        opts_layout.addWidget(self.font_label)
        opts_layout.addWidget(QLabel("Export DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(300)
        opts_layout.addWidget(self.dpi_spin)
        opts_layout.addStretch()
        layout.addWidget(opts)

        # ── Buttons ──
        btn_layout = QHBoxLayout()
        self.btn_render = QPushButton("Render Tree")
        self.btn_render.clicked.connect(self._render)
        self.btn_render.setEnabled(False)
        btn_layout.addWidget(self.btn_render)

        self.btn_export = QPushButton("Export Figure...")
        self.btn_export.clicked.connect(self._export_figure)
        self.btn_export.setEnabled(False)
        btn_layout.addWidget(self.btn_export)

        self.btn_export_nwk = QPushButton("Export MCMCTree Newick...")
        self.btn_export_nwk.clicked.connect(self._export_newick)
        self.btn_export_nwk.setEnabled(False)
        btn_layout.addWidget(self.btn_export_nwk)

        self.btn_fit = QPushButton("Fit to Window")
        self.btn_fit.clicked.connect(self._fit_to_window)
        self.btn_fit.setEnabled(False)
        btn_layout.addWidget(self.btn_fit)

        self.btn_zoom_100 = QPushButton("100%")
        self.btn_zoom_100.clicked.connect(self._zoom_reset)
        self.btn_zoom_100.setEnabled(False)
        btn_layout.addWidget(self.btn_zoom_100)

        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setMinimumWidth(90)
        btn_layout.addWidget(self.zoom_label)

        btn_layout.addStretch()
        hint_label = QLabel("Ctrl+Scroll: zoom | Scroll: pan | Click node: leaves | Dbl-click: calibrate")
        hint_label.setStyleSheet("color: #888; font-size: 10px;")
        btn_layout.addWidget(hint_label)
        layout.addLayout(btn_layout)

        # ── Splitter: canvas (top) + info panel (bottom) ──
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Canvas area
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self.figure = plt.figure(figsize=(16, 10))
        self.toolbar = NavigationToolbar(FigureCanvas(self.figure), self)
        self.toolbar.canvas = None
        canvas_layout.addWidget(self.toolbar)

        self.scroll_canvas = ZoomableScrollCanvas(self.figure, self)
        self.toolbar.canvas = self.scroll_canvas.canvas
        canvas_layout.addWidget(self.scroll_canvas)

        splitter.addWidget(canvas_container)

        # Node info panel
        self.node_info = QTextEdit()
        self.node_info.setReadOnly(True)
        self.node_info.setFont(QFont("monospace", 10))
        self.node_info.setPlaceholderText(
            "Click an internal node to see its descendant taxa here.\n"
            "Double-click to add/edit a fossil calibration."
        )
        self.node_info.setMaximumHeight(180)
        splitter.addWidget(self.node_info)

        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

        # Track zoom via resize events
        self.scroll_canvas.canvas.installEventFilter(self)
        self._last_zoom_pct = 100

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Resize:
            pct = self.scroll_canvas.zoom_percent
            if pct != self._last_zoom_pct:
                self._last_zoom_pct = pct
                self.zoom_label.setText(f"Zoom: {pct}%")
        return super().eventFilter(obj, event)

    def load_tree(self, tree: PhyloTree) -> None:
        self.tree = tree
        self.btn_render.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.btn_export_nwk.setEnabled(True)
        self.btn_fit.setEnabled(False)
        self.btn_zoom_100.setEnabled(False)
        self.node_info.clear()

    def clear(self) -> None:
        self.tree = None
        self._plot_result = None
        self._disconnect_mpl_events()
        self.btn_render.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_export_nwk.setEnabled(False)
        self.btn_fit.setEnabled(False)
        self.btn_zoom_100.setEnabled(False)
        self.figure.clear()
        self.scroll_canvas.canvas.draw()
        self.node_info.clear()

    def _make_visualizer(self, dpi: int = 100) -> TreeVisualizer:
        return TreeVisualizer(
            theme=self.theme_combo.currentText(),
            font_size_leaf=self.font_leaf.value(),
            font_size_label=self.font_label.value(),
            dpi=dpi,
        )

    # ── Rendering ──────────────────────────────────────────────────────

    def _on_option_changed(self, *_args) -> None:
        """Auto re-render when theme or font settings change."""
        if self.tree and self._plot_result is not None:
            self._render()

    def _render(self) -> None:
        if not self.tree:
            return

        self._disconnect_mpl_events()
        self.figure.clear()
        viz = self._make_visualizer(dpi=self._screen_dpi)

        n_taxa = self.tree.n_taxa
        fig_width = 20
        fig_height = max(12, n_taxa * 0.35)
        self.figure.set_size_inches(fig_width, fig_height)
        self.figure.set_dpi(self._screen_dpi)

        ax = self.figure.add_subplot(111)
        title = f"{self.tree.source} — Phylogenetic Tree with B() Fossil Calibrations"
        self._plot_result = viz.plot(self.tree, title=title, ax=ax)

        px_w = int(fig_width * self._screen_dpi)
        px_h = int(fig_height * self._screen_dpi)
        self.scroll_canvas.set_base_size(px_w, px_h)
        self.scroll_canvas.canvas.draw()

        self.btn_export.setEnabled(True)
        self.btn_fit.setEnabled(True)
        self.btn_zoom_100.setEnabled(True)
        self.zoom_label.setText(f"Zoom: {self.scroll_canvas.zoom_percent}%")

        # Connect interactive mouse events
        self._connect_mpl_events()

    def _connect_mpl_events(self) -> None:
        canvas = self.scroll_canvas.canvas
        self._mpl_cids = [
            canvas.mpl_connect("motion_notify_event", self._on_mouse_move),
            canvas.mpl_connect("button_press_event", self._on_mouse_click),
        ]

    def _disconnect_mpl_events(self) -> None:
        canvas = self.scroll_canvas.canvas
        for cid in self._mpl_cids:
            canvas.mpl_disconnect(cid)
        self._mpl_cids.clear()

    # ── Hit detection ──────────────────────────────────────────────────

    def _find_nearest_internal_node(
        self, data_x: float, data_y: float, threshold: float = 0.6
    ) -> Optional[TreeNode]:
        """Find the nearest internal node to (data_x, data_y) within threshold."""
        if not self._plot_result:
            return None

        best_node = None
        best_dist_sq = threshold * threshold

        for node in self._plot_result.internal_nodes:
            nx, ny = self._plot_result.node_positions[node.node_id]
            dx = data_x - nx
            dy = data_y - ny
            dist_sq = dx * dx + dy * dy
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_node = node

        return best_node

    # ── Mouse event handlers ───────────────────────────────────────────

    def _on_mouse_move(self, event) -> None:
        """Show tooltip with leaf taxa when hovering near an internal node."""
        if event.inaxes is None or not self._plot_result:
            QToolTip.hideText()
            self._hover_node = None
            return

        node = self._find_nearest_internal_node(event.xdata, event.ydata)

        if node is None:
            if self._hover_node is not None:
                QToolTip.hideText()
                self._hover_node = None
            return

        if node is self._hover_node:
            return  # same node, keep tooltip

        self._hover_node = node
        leaves = node.get_leaf_names()
        n = len(leaves)

        # Build tooltip text
        if node.calibration:
            cal = node.calibration
            header = f"Calibrated node (ID {node.node_id}) — B({cal.lower},{cal.upper})\n"
        else:
            header = f"Internal node (ID {node.node_id}) — no calibration\n"

        if n <= 12:
            taxa_text = "\n".join(f"  {t}" for t in leaves)
        else:
            top = "\n".join(f"  {t}" for t in leaves[:5])
            bot = "\n".join(f"  {t}" for t in leaves[-5:])
            taxa_text = f"{top}\n  ... ({n - 10} more) ...\n{bot}"

        tooltip = f"{header}{n} descendant taxa:\n{taxa_text}\n\nDouble-click to add/edit calibration"

        QToolTip.showText(QCursor.pos(), tooltip, self.scroll_canvas.canvas)

    def _on_mouse_click(self, event) -> None:
        """Single click: show leaves in panel. Double click: open calibration dialog."""
        if event.inaxes is None or not self._plot_result:
            return

        node = self._find_nearest_internal_node(event.xdata, event.ydata)
        if node is None:
            return

        leaves = node.get_leaf_names()
        n = len(leaves)

        if event.dblclick:
            # ── Double click: calibration dialog ──
            self._open_calibration_dialog(node)
        else:
            # ── Single click: show leaves in info panel ──
            if node.calibration:
                cal = node.calibration
                header = f"Node {node.node_id} — B({cal.lower},{cal.upper},{cal.p_lower},{cal.p_upper})"
            else:
                header = f"Node {node.node_id} — no calibration"

            taxa_list = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(leaves))
            self.node_info.setPlainText(
                f"{header}\n{n} descendant taxa:\n{taxa_list}"
            )

    # ── Calibration editing ────────────────────────────────────────────

    def _open_calibration_dialog(self, node: TreeNode) -> None:
        dlg = CalibrationDialog(node, parent=self)
        result = dlg.exec_()

        if result == QDialog.DialogCode.Accepted:
            # Apply new calibration
            node.calibration = dlg.result_calibration
            self._on_tree_modified(node, "added/updated")

        elif result == 2:
            # Remove calibration
            node.calibration = None
            self._on_tree_modified(node, "removed")

    def _on_tree_modified(self, node: TreeNode, action: str) -> None:
        """Re-render after calibration change and notify main window."""
        cal_str = node.calibration.to_mcmctree() if node.calibration else "none"
        self.node_info.setPlainText(
            f"Calibration {action} on node {node.node_id}: {cal_str}\n"
            f"Re-rendering tree..."
        )

        # Re-render
        self._render()

        # Notify main window to refresh other tabs
        if self.on_tree_modified:
            self.on_tree_modified()

    # ── Zoom controls ──────────────────────────────────────────────────

    def _fit_to_window(self) -> None:
        if self.scroll_canvas._base_width == 0:
            return
        viewport = self.scroll_canvas.viewport().size()
        scale_w = viewport.width() / self.scroll_canvas._base_width
        scale_h = viewport.height() / self.scroll_canvas._base_height
        self.scroll_canvas._zoom = min(scale_w, scale_h)
        self.scroll_canvas._apply_zoom()
        self.zoom_label.setText(f"Zoom: {self.scroll_canvas.zoom_percent}%")

    def _zoom_reset(self) -> None:
        self.scroll_canvas._zoom = 1.0
        self.scroll_canvas._apply_zoom()
        self.zoom_label.setText("Zoom: 100%")

    # ── Export ─────────────────────────────────────────────────────────

    def _export_figure(self) -> None:
        if not self.tree:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tree Figure",
            f"{Path(self.tree.source).stem}_tree.pdf",
            "PDF (*.pdf);;SVG (*.svg);;PNG (*.png);;All (*)",
        )
        if path:
            viz = self._make_visualizer(dpi=self.dpi_spin.value())
            ext = Path(path).suffix.lstrip(".") or "pdf"
            saved = viz.save(self.tree, path, formats=[ext])
            QMessageBox.information(self, "Exported", f"Saved to:\n{saved[0]}")

    def _export_newick(self) -> None:
        if not self.tree:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export MCMCTree Newick",
            f"{Path(self.tree.source).stem}_calibrated.tree",
            "Tree Files (*.tree *.nwk *.newick *.tre);;All (*)",
        )
        if path:
            writer = NewickWriter()
            out = writer.write_file(self.tree, path)
            QMessageBox.information(
                self,
                "Exported",
                f"MCMCTree Newick saved to:\n{out}\n\n"
                f"Calibrations: {self.tree.n_calibrations}",
            )


# ── Main Window ────────────────────────────────────────────────────────────


class FossTreeMainWindow(QMainWindow):
    """Main application window with phased workflow."""

    def __init__(self):
        super().__init__()
        self.tree: Optional[PhyloTree] = None
        self.parser = NewickParser()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("FossTree — Fossil Calibration Annotation Tool")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ── File loader ──
        file_group = QGroupBox("Phase 1: Load Tree File")
        file_layout = QHBoxLayout(file_group)
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        self.file_path_label.setPlaceholderText("Select a Newick tree file with B() calibrations...")
        file_layout.addWidget(self.file_path_label)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_file)
        file_layout.addWidget(btn_browse)
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(self._load_tree)
        file_layout.addWidget(btn_load)
        main_layout.addWidget(file_group)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.info_tab = TreeInfoTab()
        self.tabs.addTab(self.info_tab, "Phase 2: Tree Info")
        self.convert_tab = ConvertTab()
        self.tabs.addTab(self.convert_tab, "Phase 3: BEAST2 XML")
        self.view_tab = ViewTab()
        self.view_tab.on_tree_modified = self._refresh_after_calibration_change
        self.tabs.addTab(self.view_tab, "Phase 4: Visualization")

        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, False)
        main_layout.addWidget(self.tabs)

        # ── Status bar ──
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready — select a tree file to begin.")

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Newick Tree File", "",
            "Tree Files (*.tree *.nwk *.newick *.tre);;All Files (*)",
        )
        if path:
            self.file_path_label.setText(path)

    def _load_tree(self) -> None:
        path = self.file_path_label.text().strip()
        if not path:
            QMessageBox.warning(self, "No File", "Please select a tree file first.")
            return
        if not Path(path).exists():
            QMessageBox.critical(self, "Error", f"File not found:\n{path}")
            return
        try:
            self.tree = self.parser.parse_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse tree:\n{e}")
            return

        self._update_status()

        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, True)

        self.info_tab.load_tree(self.tree)
        self.convert_tab.load_tree(self.tree)
        self.view_tab.load_tree(self.tree)
        self.tabs.setCurrentIndex(0)

    def _refresh_after_calibration_change(self) -> None:
        """Called by ViewTab when a calibration is added/removed/changed."""
        if self.tree:
            self.info_tab.load_tree(self.tree)
            self.convert_tab.load_tree(self.tree)
            self._update_status()

    def _update_status(self) -> None:
        if self.tree:
            self.status.showMessage(
                f"Loaded: {self.tree.source} — "
                f"{self.tree.n_taxa} taxa, {self.tree.n_calibrations} calibrations"
            )


def run_gui() -> None:
    """Launch the FossTree GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("FossTree")
    app.setStyle("Fusion")

    window = FossTreeMainWindow()
    window.show()
    sys.exit(app.exec_())
