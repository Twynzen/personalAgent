"""
Project Control Widget (PyQt6) - GPU-Accelerated Multi-Project Dashboard

High-performance version using PyQt6 for smooth 60 FPS animations.
Embedded in Brain GUI Tab 4.
"""

import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame
)

from sendell.dashboard.components.activity_graph_qt import create_activity_graph_qt
from sendell.dashboard.utils import (
    BG_DARK, BG_PANEL, NEON_GREEN, NEON_CYAN,
    NEON_RED, TEXT_PRIMARY, TEXT_SECONDARY
)
from sendell.utils.logger import get_logger
from sendell.vscode import VSCodeMonitor

logger = get_logger(__name__)


class ProjectControlWidgetQt(QWidget):
    """
    PyQt6 Project Control Center widget.

    Features:
    - Real-time VS Code project detection
    - GPU-accelerated animated graphs (60 FPS)
    - System metrics monitoring
    - QTimer-based updates (no threading, GIL-safe)
    """

    def __init__(self, parent=None):
        """Initialize PyQt6 project control widget"""
        super().__init__(parent)

        logger.info("Initializing PyQt6 Project Control Widget")

        # Data
        self.projects = []
        self.cpu_percent = 0
        self.ram_percent = 0
        self.terminal_count = 0

        # VS Code monitor
        self.vscode_monitor = VSCodeMonitor()

        # Build UI
        self._build_ui()

        # Timer for data updates (5 seconds)
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self._update_data)
        self.data_timer.start(5000)  # Update every 5 seconds

        # Timer for clock (1 second)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        # Initial data load
        self._update_data()

    def _build_ui(self):
        """Build main UI layout"""
        # Set dark background
        self.setStyleSheet(f"background-color: {BG_DARK};")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Content area (2 columns)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Left: Metrics panel (fixed 280px)
        self.metrics_panel = self._create_metrics_panel()
        content_layout.addWidget(self.metrics_panel)

        # Right: Projects panel (expandable)
        self.projects_panel = self._create_projects_panel()
        content_layout.addWidget(self.projects_panel, 1)

        main_layout.addLayout(content_layout)

    def _create_header(self):
        """Create header with title and clock"""
        header = QFrame()
        header.setStyleSheet(f"background-color: {BG_DARK};")
        header.setFixedHeight(60)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 15, 15, 10)

        # Title
        title = QLabel("SENDELL CEREBRO - PROYECTOS")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {NEON_GREEN};")
        layout.addWidget(title)

        # Live indicator
        live_label = QLabel("● LIVE MODE")
        live_label.setFont(QFont("Courier New", 12))
        live_label.setStyleSheet(f"color: {NEON_CYAN};")
        layout.addWidget(live_label)

        layout.addStretch()

        # Clock
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setFont(QFont("Courier New", 12))
        self.clock_label.setStyleSheet(f"color: {NEON_CYAN};")
        layout.addWidget(self.clock_label)

        return header

    def _create_metrics_panel(self):
        """Create left metrics panel"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            background-color: {BG_PANEL};
            border: 1px solid #2a2a2a;
        """)
        panel.setFixedWidth(280)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("METRICAS SISTEMA")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        layout.addSpacing(10)

        # CPU metric
        layout.addWidget(self._create_metric_widget("CPU TOTAL", "cpu"))

        # RAM metric
        layout.addWidget(self._create_metric_widget("MEMORIA", "ram"))

        # Terminals metric
        layout.addWidget(self._create_metric_widget("TERMINALES", "terminals"))

        layout.addStretch()

        # Status
        self.status_label = QLabel("Inicializando...\nEsperando datos")
        self.status_label.setFont(QFont("Courier New", 10))
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        return panel

    def _create_metric_widget(self, name, metric_type):
        """Create a single metric display widget"""
        container = QFrame()
        container.setStyleSheet(f"background-color: {BG_PANEL};")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Name label
        name_label = QLabel(name)
        name_label.setFont(QFont("Courier New", 10))
        name_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(name_label)

        # Value label
        value_label = QLabel("---%")
        value_label.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {NEON_CYAN};")
        layout.addWidget(value_label)

        # Store reference for updates
        if metric_type == "cpu":
            self.cpu_value_label = value_label
        elif metric_type == "ram":
            self.ram_value_label = value_label
        elif metric_type == "terminals":
            self.terminals_value_label = value_label

        return container

    def _create_projects_panel(self):
        """Create right projects panel"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            background-color: {BG_PANEL};
            border: 1px solid #2a2a2a;
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("PROYECTOS ACTIVOS")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # Scroll area for projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG_PANEL};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: #1a1a1a;
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #2a2a2a;
                border-radius: 6px;
            }}
        """)

        # Container for project cards
        self.projects_container = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setContentsMargins(0, 0, 0, 0)
        self.projects_layout.setSpacing(10)
        self.projects_layout.addStretch()

        scroll.setWidget(self.projects_container)
        layout.addWidget(scroll)

        return panel

    def _update_clock(self):
        """Update clock display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(current_time)

    def _update_data(self):
        """Update data from VS Code monitor and system metrics"""
        try:
            # Scan VS Code instances
            instances = self.vscode_monitor.find_vscode_instances()

            # Get system metrics (non-blocking)
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent

            # Terminal count = project count
            terminal_count = len(instances)

            # Update data
            self.projects = instances
            self.cpu_percent = cpu
            self.ram_percent = ram
            self.terminal_count = terminal_count

            # Update UI
            self._update_metrics()
            self._render_projects()

        except Exception as e:
            logger.error(f"Error updating data: {e}")

    def _update_metrics(self):
        """Update metrics panel with real data"""
        # Update CPU
        self.cpu_value_label.setText(f"{self.cpu_percent:.1f}%")

        # Update RAM
        self.ram_value_label.setText(f"{self.ram_percent:.1f}%")

        # Update terminals
        self.terminals_value_label.setText(str(self.terminal_count))

        # Update status
        project_count = len(self.projects)
        if project_count == 0:
            status_text = "Sin proyectos\nactivos"
        else:
            status_text = f"{project_count} proyecto(s)\ndetectado(s)"

        self.status_label.setText(status_text)

    def _render_projects(self):
        """Render project cards"""
        # Clear existing widgets
        while self.projects_layout.count() > 1:  # Keep stretch
            item = self.projects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.projects:
            # Show empty state
            empty_label = QLabel("No hay proyectos VS Code activos\n\nAbre un proyecto en VS Code para verlo aqui")
            empty_label.setFont(QFont("Courier New", 10))
            empty_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.projects_layout.insertWidget(0, empty_label)
            return

        # Render each project card
        for idx, project in enumerate(self.projects):
            card = self._create_project_card(project, idx)
            self.projects_layout.insertWidget(idx, card)

    def _create_project_card(self, project, index):
        """Create a single project card widget"""
        # Determine if running
        name = project.workspace.workspace_name or "Unknown"
        is_running = "sendell" in name.lower() or "gsiaf" in name.lower()

        # Card container
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {BG_PANEL};
            border: 2px solid #2a2a2a;
            border-radius: 5px;
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        # Project name
        name_color = NEON_GREEN if is_running else NEON_RED
        name_label = QLabel(f"[{index + 1}] {name}")
        name_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {name_color};")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Status
        status_text = "RUNNING" if is_running else "OFFLINE"
        status_color = NEON_GREEN if is_running else NEON_RED
        status_label = QLabel(f"[{status_text}]")
        status_label.setFont(QFont("Courier New", 10))
        status_label.setStyleSheet(f"color: {status_color};")
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Activity graph (GPU-accelerated!)
        graph = create_activity_graph_qt(
            parent=card,
            width=1050,
            height=150,
            is_running=is_running
        )
        layout.addWidget(graph)

        # Project info
        path = project.workspace.workspace_path or "Unknown path"
        path_label = QLabel(f"Path: {path}")
        path_label.setFont(QFont("Courier New", 10))
        path_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(path_label)

        pid_label = QLabel(f"PID: {project.pid}")
        pid_label.setFont(QFont("Courier New", 10))
        pid_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(pid_label)

        return card

    def closeEvent(self, event):
        """Cleanup when widget is closed"""
        logger.info("Stopping timers...")
        self.data_timer.stop()
        self.clock_timer.stop()
        super().closeEvent(event)


def create_project_control_widget_qt(parent=None):
    """
    Factory function to create PyQt6 project control widget.

    Args:
        parent: Parent widget

    Returns:
        ProjectControlWidgetQt instance
    """
    return ProjectControlWidgetQt(parent)
