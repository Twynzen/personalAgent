"""
Project Control Widget - Centro de Control Multi-Proyecto

Embedded widget for Brain GUI Tab 4.
Displays VS Code projects, metrics, and activity graphs.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from sendell.dashboard.utils import (
    BG_DARK,
    BG_PANEL,
    NEON_GREEN,
    NEON_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectControlWidget(ttk.Frame):
    """
    Main widget for Project Control Center.

    Embedded in Brain GUI Tab 4.
    Shows VS Code projects, system metrics, and activity graphs.
    """

    def __init__(self, parent):
        """Initialize project control widget"""
        super().__init__(parent)

        # Configure dark theme
        self.configure(style="Dark.TFrame")

        logger.info("Initializing Project Control Widget")

        # Build UI
        self._create_styles()
        self._build_ui()

        # Start clock update
        self._update_clock()

    def _create_styles(self):
        """Create custom ttk styles for cyberpunk theme"""
        style = ttk.Style()

        # Dark frame style
        style.configure(
            "Dark.TFrame",
            background=BG_DARK
        )

        # Panel frame style
        style.configure(
            "Panel.TFrame",
            background=BG_PANEL,
            relief="solid",
            borderwidth=1
        )

        # Header label style
        style.configure(
            "Header.TLabel",
            background=BG_DARK,
            foreground=NEON_GREEN,
            font=("Courier New", 16, "bold")
        )

        # Clock label style
        style.configure(
            "Clock.TLabel",
            background=BG_DARK,
            foreground=NEON_CYAN,
            font=("Courier New", 12)
        )

        # Section title style
        style.configure(
            "Section.TLabel",
            background=BG_PANEL,
            foreground=TEXT_PRIMARY,
            font=("Courier New", 12, "bold")
        )

        # Info text style
        style.configure(
            "Info.TLabel",
            background=BG_PANEL,
            foreground=TEXT_SECONDARY,
            font=("Courier New", 10)
        )

    def _build_ui(self):
        """Build main UI layout"""
        # Main container (fills entire tab)
        main_container = ttk.Frame(self, style="Dark.TFrame")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        self._create_header(main_container)

        # Content area (2 columns)
        content_frame = ttk.Frame(main_container, style="Dark.TFrame")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left column: Metrics (280px fixed width)
        self._create_metrics_panel(content_frame)

        # Right column: Projects (remaining space)
        self._create_projects_panel(content_frame)

    def _create_header(self, parent):
        """Create header with title and clock"""
        header_frame = ttk.Frame(parent, style="Dark.TFrame", height=60)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)

        # Title (left side)
        title_label = ttk.Label(
            header_frame,
            text="SENDELL CEREBRO - PROYECTOS",
            style="Header.TLabel"
        )
        title_label.pack(side="left")

        # Live indicator
        live_frame = ttk.Frame(header_frame, style="Dark.TFrame")
        live_frame.pack(side="left", padx=15)

        live_dot = tk.Canvas(
            live_frame,
            width=12,
            height=12,
            bg=BG_DARK,
            highlightthickness=0
        )
        live_dot.pack(side="left")
        live_dot.create_oval(2, 2, 10, 10, fill=NEON_GREEN, outline="")

        live_label = ttk.Label(
            live_frame,
            text="LIVE MODE",
            style="Clock.TLabel"
        )
        live_label.pack(side="left", padx=(5, 0))

        # Clock (right side)
        self.clock_label = ttk.Label(
            header_frame,
            text="00:00:00",
            style="Clock.TLabel"
        )
        self.clock_label.pack(side="right")

    def _create_metrics_panel(self, parent):
        """Create left metrics panel"""
        metrics_frame = ttk.Frame(
            parent,
            style="Panel.TFrame",
            width=280
        )
        metrics_frame.pack(side="left", fill="y", padx=(0, 10))
        metrics_frame.pack_propagate(False)

        # Title
        title = ttk.Label(
            metrics_frame,
            text="METRICAS SISTEMA",
            style="Section.TLabel"
        )
        title.pack(pady=(15, 20), padx=15, anchor="w")

        # Placeholder metrics
        metrics_info = [
            ("CPU TOTAL", "---%"),
            ("MEMORIA", "---%"),
            ("TERMINALES", "---")
        ]

        for metric_name, metric_value in metrics_info:
            metric_container = ttk.Frame(metrics_frame, style="Panel.TFrame")
            metric_container.pack(fill="x", padx=15, pady=10)

            name_label = ttk.Label(
                metric_container,
                text=metric_name,
                style="Info.TLabel"
            )
            name_label.pack(anchor="w")

            value_label = ttk.Label(
                metric_container,
                text=metric_value,
                font=("Courier New", 24, "bold"),
                foreground=NEON_CYAN,
                background=BG_PANEL
            )
            value_label.pack(anchor="w", pady=(5, 0))

        # Status info at bottom
        status_frame = ttk.Frame(metrics_frame, style="Panel.TFrame")
        status_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        status_label = ttk.Label(
            status_frame,
            text="Inicializando...\nEsperando datos",
            style="Info.TLabel",
            justify="center"
        )
        status_label.pack()

    def _create_projects_panel(self, parent):
        """Create right projects panel"""
        projects_frame = ttk.Frame(parent, style="Panel.TFrame")
        projects_frame.pack(side="right", fill="both", expand=True)

        # Title
        title = ttk.Label(
            projects_frame,
            text="PROYECTOS ACTIVOS",
            style="Section.TLabel"
        )
        title.pack(pady=(15, 20), padx=15, anchor="w")

        # Placeholder content
        placeholder_frame = ttk.Frame(projects_frame, style="Panel.TFrame")
        placeholder_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Center message
        message_container = ttk.Frame(placeholder_frame, style="Panel.TFrame")
        message_container.place(relx=0.5, rely=0.5, anchor="center")

        # Icon (using text)
        icon_label = ttk.Label(
            message_container,
            text="[ ]",
            font=("Courier New", 48, "bold"),
            foreground=NEON_GREEN,
            background=BG_PANEL
        )
        icon_label.pack(pady=(0, 20))

        # Message
        message_label = ttk.Label(
            message_container,
            text="CENTRO DE CONTROL MULTI-PROYECTO\n\n"
                 "Sistema de monitoreo inicializado\n"
                 "Escaneando proyectos VS Code...\n\n"
                 "[Fase 0: UI Foundation Completada]",
            style="Section.TLabel",
            justify="center"
        )
        message_label.pack()

        # Version info
        version_label = ttk.Label(
            message_container,
            text="v0.3-simplified | Powered by psutil",
            style="Info.TLabel"
        )
        version_label.pack(pady=(20, 0))

    def _update_clock(self):
        """Update clock every second"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)

        # Schedule next update
        self.after(1000, self._update_clock)


def create_project_control_widget(parent):
    """
    Factory function to create project control widget.

    Args:
        parent: Parent tkinter widget (tab frame)

    Returns:
        ProjectControlWidget instance
    """
    return ProjectControlWidget(parent)
