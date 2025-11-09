"""
Project Control Widget - Centro de Control Multi-Proyecto

Embedded widget for Brain GUI Tab 4.
Displays VS Code projects, metrics, and activity graphs.
"""

import queue
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import psutil

from sendell.dashboard.utils import (
    BG_DARK,
    BG_PANEL,
    NEON_GREEN,
    NEON_CYAN,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    STATUS_IDLE,
)
from sendell.utils.logger import get_logger
from sendell.vscode import VSCodeMonitor

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

        # Data
        self.projects = []
        self.cpu_percent = 0
        self.ram_percent = 0
        self.terminal_count = 0

        # Threading
        self.update_queue = queue.Queue()
        self.stop_event = threading.Event()

        # VS Code monitor
        self.vscode_monitor = VSCodeMonitor()

        # Build UI
        self._create_styles()
        self._build_ui()

        # Start background worker
        self._start_background_worker()

        # Start UI updates
        self._update_clock()
        self._check_queue()

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

        # CPU metric
        cpu_container = ttk.Frame(metrics_frame, style="Panel.TFrame")
        cpu_container.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            cpu_container,
            text="CPU TOTAL",
            style="Info.TLabel"
        ).pack(anchor="w")

        self.cpu_value_label = ttk.Label(
            cpu_container,
            text="---%",
            font=("Courier New", 24, "bold"),
            foreground=NEON_CYAN,
            background=BG_PANEL
        )
        self.cpu_value_label.pack(anchor="w", pady=(5, 0))

        # RAM metric
        ram_container = ttk.Frame(metrics_frame, style="Panel.TFrame")
        ram_container.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            ram_container,
            text="MEMORIA",
            style="Info.TLabel"
        ).pack(anchor="w")

        self.ram_value_label = ttk.Label(
            ram_container,
            text="---%",
            font=("Courier New", 24, "bold"),
            foreground=NEON_CYAN,
            background=BG_PANEL
        )
        self.ram_value_label.pack(anchor="w", pady=(5, 0))

        # Terminals metric
        terminals_container = ttk.Frame(metrics_frame, style="Panel.TFrame")
        terminals_container.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            terminals_container,
            text="TERMINALES",
            style="Info.TLabel"
        ).pack(anchor="w")

        self.terminals_value_label = ttk.Label(
            terminals_container,
            text="---",
            font=("Courier New", 24, "bold"),
            foreground=NEON_CYAN,
            background=BG_PANEL
        )
        self.terminals_value_label.pack(anchor="w", pady=(5, 0))

        # Status info at bottom
        status_frame = ttk.Frame(metrics_frame, style="Panel.TFrame")
        status_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.status_label = ttk.Label(
            status_frame,
            text="Inicializando...\nEsperando datos",
            style="Info.TLabel",
            justify="center"
        )
        self.status_label.pack()

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

        # Scrollable container for projects
        canvas = tk.Canvas(
            projects_frame,
            bg=BG_PANEL,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(projects_frame, orient="vertical", command=canvas.yview)

        self.projects_container = ttk.Frame(canvas, style="Panel.TFrame")
        self.projects_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.projects_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
        scrollbar.pack(side="right", fill="y", pady=(0, 15), padx=(0, 15))

    def _update_clock(self):
        """Update clock every second"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)

        # Schedule next update
        self.after(1000, self._update_clock)

    def _start_background_worker(self):
        """Start background thread to scan VS Code projects"""
        def worker():
            logger.info("Background worker started")
            while not self.stop_event.is_set():
                try:
                    # Scan VS Code instances (returns list of VSCodeInstance dataclasses)
                    instances = self.vscode_monitor.find_vscode_instances()

                    # Get system metrics
                    cpu = psutil.cpu_percent(interval=0.1)
                    ram = psutil.virtual_memory().percent

                    # For now, terminal count = number of projects
                    # (In future we can detect actual terminal processes per project)
                    terminal_count = len(instances)

                    # Put data in queue for UI thread
                    self.update_queue.put({
                        "type": "update",
                        "projects": instances,
                        "cpu": cpu,
                        "ram": ram,
                        "terminals": terminal_count
                    })

                except Exception as e:
                    logger.error(f"Error in background worker: {e}")
                    self.update_queue.put({
                        "type": "error",
                        "message": str(e)
                    })

                # Wait 5 seconds before next scan
                self.stop_event.wait(5)

            logger.info("Background worker stopped")

        # Start worker thread
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def _check_queue(self):
        """Check queue for updates from background thread"""
        try:
            while True:
                update = self.update_queue.get_nowait()

                if update["type"] == "update":
                    # Update data
                    self.projects = update["projects"]
                    self.cpu_percent = update["cpu"]
                    self.ram_percent = update["ram"]
                    self.terminal_count = update["terminals"]

                    # Update UI
                    self._update_metrics()
                    self._render_projects()

                elif update["type"] == "error":
                    logger.error(f"Background error: {update['message']}")
                    self.status_label.config(text=f"Error:\n{update['message']}")

        except queue.Empty:
            pass

        # Schedule next check (every 100ms)
        self.after(100, self._check_queue)

    def _update_metrics(self):
        """Update metrics panel with real data"""
        # Update CPU
        cpu_text = f"{self.cpu_percent:.1f}%"
        self.cpu_value_label.config(text=cpu_text)

        # Update RAM
        ram_text = f"{self.ram_percent:.1f}%"
        self.ram_value_label.config(text=ram_text)

        # Update terminals
        self.terminals_value_label.config(text=str(self.terminal_count))

        # Update status
        project_count = len(self.projects)
        if project_count == 0:
            status_text = "Sin proyectos\nactivos"
        else:
            status_text = f"{project_count} proyecto(s)\ndetectado(s)"

        self.status_label.config(text=status_text)

    def _render_projects(self):
        """Render project cards in scrollable container"""
        # Clear existing widgets
        for widget in self.projects_container.winfo_children():
            widget.destroy()

        if not self.projects:
            # Show empty state
            empty_label = ttk.Label(
                self.projects_container,
                text="No hay proyectos VS Code activos\n\nAbre un proyecto en VS Code para verlo aqui",
                style="Info.TLabel",
                justify="center"
            )
            empty_label.pack(pady=50)
            return

        # Render each project card
        for idx, project in enumerate(self.projects):
            self._create_project_card(self.projects_container, project, idx)

    def _create_project_card(self, parent, project, index):
        """Create a single project card widget"""
        from sendell.dashboard.utils import NEON_YELLOW, NEON_RED
        from sendell.dashboard.components import create_activity_graph

        # Determine if project is RUNNING or OFFLINE
        # For now: heuristic based on name (contains "sendell" or "GSIAF")
        # Later: detect actual terminal activity
        name = project.workspace.workspace_name or "Unknown"
        is_running = "sendell" in name.lower() or "gsiaf" in name.lower()

        # Card container
        card = ttk.Frame(parent, style="Panel.TFrame", relief="raised", borderwidth=2)
        card.pack(fill="x", padx=10, pady=10)

        # Header with project name
        header = ttk.Frame(card, style="Panel.TFrame")
        header.pack(fill="x", padx=15, pady=(15, 10))

        # Project name - GREEN if running, RED if offline
        name_color = NEON_GREEN if is_running else NEON_RED
        name_label = ttk.Label(
            header,
            text=f"[{index + 1}] {name}",
            font=("Courier New", 12, "bold"),
            foreground=name_color,
            background=BG_PANEL
        )
        name_label.pack(side="left")

        # Status indicator - RUNNING or OFFLINE
        status_text = "RUNNING" if is_running else "OFFLINE"
        status_color = NEON_GREEN if is_running else NEON_RED
        status_label = ttk.Label(
            header,
            text=f"[{status_text}]",
            font=("Courier New", 10),
            foreground=status_color,
            background=BG_PANEL
        )
        status_label.pack(side="right")

        # Activity graph (pulse line if running, grid only if offline)
        graph = create_activity_graph(
            card,
            width=1050,
            height=150,
            is_running=is_running
        )
        graph.pack(fill="x", padx=15, pady=(10, 10))

        # Project info
        info_frame = ttk.Frame(card, style="Panel.TFrame")
        info_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Path (access dataclass attribute directly)
        path = project.workspace.workspace_path or "Unknown path"
        path_label = ttk.Label(
            info_frame,
            text=f"Path: {path}",
            style="Info.TLabel"
        )
        path_label.pack(anchor="w", pady=2)

        # PID (access dataclass attribute directly)
        pid = project.pid
        pid_label = ttk.Label(
            info_frame,
            text=f"PID: {pid}",
            style="Info.TLabel"
        )
        pid_label.pack(anchor="w", pady=2)

    def destroy(self):
        """Cleanup when widget is destroyed"""
        logger.info("Stopping background worker...")
        self.stop_event.set()
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join(timeout=2)
        super().destroy()


def create_project_control_widget(parent):
    """
    Factory function to create project control widget.

    Args:
        parent: Parent tkinter widget (tab frame)

    Returns:
        ProjectControlWidget instance
    """
    return ProjectControlWidget(parent)
