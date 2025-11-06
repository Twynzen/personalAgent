"""
Sendell Epic Dashboard - Cyberpunk style monitoring interface

Real-time visual debugging dashboard with:
- Live metrics (CPU, RAM, Disk, Terminals)
- Animated graphs
- Pulsing project indicators
- psutil vs WebSocket comparison
- Error detection and alerts
"""

import math
import threading
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque
from datetime import datetime
from typing import Optional
import queue

import psutil

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class EpicDashboard:
    """Epic cyberpunk-style monitoring dashboard"""

    def __init__(self, vscode_manager=None):
        self.vscode_manager = vscode_manager
        self.root = tk.Tk()
        self.root.title("⚡ SENDELL CEREBRO")
        self.root.geometry("1400x900")
        self.root.configure(bg='#000000')

        # Data storage for graphs
        self.cpu_history = deque(maxlen=60)  # Last 60 seconds
        self.ram_history = deque(maxlen=60)
        self.disk_history = deque(maxlen=60)

        # Animation state
        self.pulse_phase = 0

        # Threading components for non-blocking updates
        self.update_queue = queue.Queue()
        self.stop_thread = threading.Event()

        # Cache VSCodeMonitor (create once, reuse forever)
        try:
            from sendell.vscode import VSCodeMonitor
            self.psutil_monitor = VSCodeMonitor()
            logger.info("VSCodeMonitor cached for dashboard")
        except Exception as e:
            logger.error(f"Could not initialize VSCodeMonitor: {e}")
            self.psutil_monitor = None

        # Current data (updated from queue)
        self.current_instances = []
        self.current_cpu = 0
        self.current_ram = 0
        self.current_disk = 0

        # Create UI with 2-column layout
        self.create_header()

        # Main container (2 columns: projects left, metrics+graphs right)
        main_container = tk.Frame(self.root, bg='#000000')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        # LEFT COLUMN: Projects list (vertical)
        self.left_frame = tk.Frame(main_container, bg='#000000', width=400)
        self.left_frame.pack(side='left', fill='both', expand=False, padx=(0, 10))
        self.create_projects_panel_vertical()

        # RIGHT COLUMN: Metrics + Graphs
        self.right_frame = tk.Frame(main_container, bg='#000000')
        self.right_frame.pack(side='right', fill='both', expand=True)
        self.create_metrics_panel()
        self.create_graphs_panel()

        self.create_footer()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start background worker thread (heavy operations)
        self.update_thread = threading.Thread(target=self.background_worker, daemon=True)
        self.update_thread.start()
        logger.info("Epic Dashboard background worker started")

        # Start UI update loop (lightweight, reads from queue)
        self.root.after(100, self.check_queue)
        self.root.after(50, self.update_animations)

    def create_header(self):
        """Create header with title and time"""
        header_frame = tk.Frame(self.root, bg='#000000', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)

        # Title
        title = tk.Label(
            header_frame,
            text="⚡ SENDELL CEREBRO",
            font=('Courier New', 24, 'bold'),
            bg='#000000',
            fg='#00ff00'
        )
        title.pack(side='left', padx=20)

        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="LIVE MODE | MONITOR DE PROYECTOS",
            font=('Courier New', 10),
            bg='#000000',
            fg='#00aa00'
        )
        subtitle.pack(side='left', padx=10)

        # Time label
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=('Courier New', 16, 'bold'),
            bg='#000000',
            fg='#00ffff'
        )
        self.time_label.pack(side='right', padx=20)

        # Buttons
        btn_frame = tk.Frame(header_frame, bg='#000000')
        btn_frame.pack(side='right', padx=10)

        tk.Button(
            btn_frame,
            text="🔍 ESCANEAR",
            font=('Courier New', 10, 'bold'),
            bg='#1a1a1a',
            fg='#00ffff',
            activebackground='#003366',
            command=self.manual_scan,
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="🔄 ACTUALIZAR",
            font=('Courier New', 10, 'bold'),
            bg='#1a1a1a',
            fg='#00ff00',
            activebackground='#003300',
            command=self.force_update,
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)

    def create_metrics_panel(self):
        """Create top metrics panel (CPU, RAM, Terminals) in right column"""
        metrics_frame = tk.Frame(self.right_frame, bg='#000000')
        metrics_frame.pack(fill='x', pady=(0, 10))

        # Create 3 metric cards (removed DISCO - not in expectativa.png)
        self.cpu_label = self.create_metric_card(metrics_frame, "CPU TOTAL", "0", "%", '#00ff00')
        self.ram_label = self.create_metric_card(metrics_frame, "MEMORIA", "0", "%", '#ffff00')
        self.terminals_label = self.create_metric_card(metrics_frame, "TERMINALES", "0", "", '#00ffff')

    def create_metric_card(self, parent, title, value, unit, color):
        """Create a single metric card"""
        card = tk.Frame(parent, bg='#0a0a0a', relief='solid', borderwidth=1)
        card.pack(side='left', fill='both', expand=True, padx=5)

        # Title
        tk.Label(
            card,
            text=title,
            font=('Courier New', 10),
            bg='#0a0a0a',
            fg='#666666'
        ).pack(pady=(10, 5))

        # Value
        value_label = tk.Label(
            card,
            text=value,
            font=('Courier New', 36, 'bold'),
            bg='#0a0a0a',
            fg=color
        )
        value_label.pack(pady=5)

        # Unit
        tk.Label(
            card,
            text=unit,
            font=('Courier New', 12),
            bg='#0a0a0a',
            fg='#666666'
        ).pack(pady=(0, 10))

        return value_label

    def create_projects_panel_vertical(self):
        """Create vertical projects list panel in left column (like expectativa.png)"""
        # Header
        header = tk.Frame(self.left_frame, bg='#0a0a0a', relief='solid', borderwidth=1)
        header.pack(fill='x', pady=(0, 5))

        tk.Label(
            header,
            text="PROYECTOS DETECTADOS",
            font=('Courier New', 12, 'bold'),
            bg='#0a0a0a',
            fg='#00ff00'
        ).pack(pady=10)

        self.projects_count_label = tk.Label(
            header,
            text="(0)",
            font=('Courier New', 10),
            bg='#0a0a0a',
            fg='#666666'
        )
        self.projects_count_label.pack(pady=(0, 10))

        # Scrollable projects list
        list_frame = tk.Frame(self.left_frame, bg='#000000')
        list_frame.pack(fill='both', expand=True)

        # Canvas + Scrollbar for project cards
        self.projects_canvas = tk.Canvas(
            list_frame,
            bg='#000000',
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.projects_canvas.yview)
        self.projects_frame = tk.Frame(self.projects_canvas, bg='#000000')

        self.projects_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.projects_canvas.pack(side='left', fill='both', expand=True)

        # Create window in canvas for scrollable content
        self.projects_canvas.create_window((0, 0), window=self.projects_frame, anchor='nw')
        self.projects_frame.bind('<Configure>',
            lambda e: self.projects_canvas.configure(scrollregion=self.projects_canvas.bbox('all')))

    # NOTE: create_comparison_panel() removed - not in expectativa.png
    # Comparison data is shown in footer instead

    def create_graphs_panel(self):
        """Create animated graphs panel in right column (stacked vertically)"""
        graphs_container = tk.Frame(self.right_frame, bg='#000000')
        graphs_container.pack(fill='both', expand=True)

        # CPU Graph (STACKED VERTICALLY)
        cpu_frame = tk.Frame(graphs_container, bg='#0a0a0a', relief='solid', borderwidth=1)
        cpu_frame.pack(fill='both', expand=True, pady=5)

        tk.Label(
            cpu_frame,
            text="ACTIVIDAD CPU",
            font=('Courier New', 10, 'bold'),
            bg='#0a0a0a',
            fg='#00ff00'
        ).pack(pady=5)

        self.cpu_canvas = tk.Canvas(
            cpu_frame,
            bg='#000000',
            height=150,
            highlightthickness=0
        )
        self.cpu_canvas.pack(fill='both', expand=True, padx=10, pady=10)

        # RAM Graph (STACKED VERTICALLY)
        ram_frame = tk.Frame(graphs_container, bg='#0a0a0a', relief='solid', borderwidth=1)
        ram_frame.pack(fill='both', expand=True, pady=5)

        tk.Label(
            ram_frame,
            text="ACTIVIDAD MEMORIA",
            font=('Courier New', 10, 'bold'),
            bg='#0a0a0a',
            fg='#ffff00'
        ).pack(pady=5)

        self.ram_canvas = tk.Canvas(
            ram_frame,
            bg='#000000',
            height=150,
            highlightthickness=0
        )
        self.ram_canvas.pack(fill='both', expand=True, padx=10, pady=10)

        # Disk I/O Graph (STACKED VERTICALLY) - Simulated with disk usage for now
        disk_frame = tk.Frame(graphs_container, bg='#0a0a0a', relief='solid', borderwidth=1)
        disk_frame.pack(fill='both', expand=True, pady=5)

        tk.Label(
            disk_frame,
            text="PULSACION RED/IO",
            font=('Courier New', 10, 'bold'),
            bg='#0a0a0a',
            fg='#00ffff'
        ).pack(pady=5)

        self.disk_canvas = tk.Canvas(
            disk_frame,
            bg='#000000',
            height=150,
            highlightthickness=0
        )
        self.disk_canvas.pack(fill='both', expand=True, padx=10, pady=10)

    def create_footer(self):
        """Create footer with system info"""
        footer_frame = tk.Frame(self.root, bg='#000000', height=30)
        footer_frame.pack(fill='x', side='bottom', padx=10, pady=5)

        self.footer_label = tk.Label(
            footer_frame,
            text="",
            font=('Courier New', 9),
            bg='#000000',
            fg='#00aa00'
        )
        self.footer_label.pack(side='left')

    def background_worker(self):
        """
        Background thread worker - runs heavy operations here (safe to block).
        Scans VS Code instances every 5 seconds, system metrics every 1 second.
        """
        logger.info("Background worker started - metrics every 1s, projects every 5s")

        cycle_count = 0
        last_instances = []

        while not self.stop_thread.is_set():
            try:
                # LIGHTWEIGHT metrics every cycle (1 second)
                cpu = psutil.cpu_percent()  # NO interval = instantaneous (fast but less accurate)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent

                # HEAVY project scan every 5 cycles (5 seconds)
                if cycle_count % 5 == 0:
                    if self.psutil_monitor:
                        last_instances = self.psutil_monitor.find_vscode_instances()
                        logger.debug(f"Project scan: {len(last_instances)} instances, "
                                   f"{sum(len(i.terminals) for i in last_instances)} terminals")

                # WebSocket data (lightweight)
                ws_terminal_count = 0
                ws_project_count = 0
                if self.vscode_manager:
                    projects = self.vscode_manager.get_all_projects()
                    ws_project_count = len(projects)
                    ws_terminal_count = sum(len(p.terminals) for p in projects)

                # Put results in queue (non-blocking)
                data = {
                    "cpu": cpu,
                    "ram": ram,
                    "disk": disk,
                    "instances": last_instances,  # Use cached instances
                    "ws_terminal_count": ws_terminal_count,
                    "ws_project_count": ws_project_count,
                    "timestamp": time.time()
                }
                self.update_queue.put(data)

                cycle_count += 1

            except Exception as e:
                logger.error(f"Background worker error: {e}")

            # Wait 1 second before next cycle
            self.stop_thread.wait(1)

        logger.info("Background worker stopped")

    def check_queue(self):
        """
        Check queue for updates from background thread (runs on UI thread).
        This is FAST and non-blocking - safe to run every 100ms.
        """
        try:
            # Try to get data from queue (non-blocking)
            data = self.update_queue.get_nowait()

            # Update current data (FAST - no I/O)
            self.current_cpu = data['cpu']
            self.current_ram = data['ram']
            self.current_disk = data['disk']
            self.current_instances = data['instances']

            # Add to history for graphs
            self.cpu_history.append(self.current_cpu)
            self.ram_history.append(self.current_ram)
            self.disk_history.append(self.current_disk)

            # Update UI widgets (FAST - no blocking)
            self.cpu_label.config(text=str(int(self.current_cpu)))
            self.ram_label.config(text=str(int(self.current_ram)))
            self.disk_label.config(text=str(int(self.current_disk)))

            terminal_count = sum(len(inst.terminals) for inst in self.current_instances)
            self.terminals_label.config(text=str(terminal_count))

            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)

            # Update comparison panel
            self.update_comparison_fast(data)

            # Update footer
            self.update_footer_fast(data)

        except queue.Empty:
            # No data yet - that's OK, will check again in 100ms
            pass
        except Exception as e:
            logger.error(f"Queue check error: {e}")

        # Schedule next check (every 100ms - very frequent but lightweight)
        self.root.after(100, self.check_queue)

    def update_animations(self):
        """Update animations (pulsing, graphs) - runs every 50ms for smooth animation"""
        try:
            # Increment pulse phase
            self.pulse_phase = (self.pulse_phase + 1) % 60

            # Redraw graphs (3 params: canvas, data, color)
            self.draw_graph(self.cpu_canvas, self.cpu_history, '#00ff00')
            self.draw_graph(self.ram_canvas, self.ram_history, '#ffff00')
            self.draw_graph(self.disk_canvas, self.disk_history, '#00ffff')

            # Redraw projects with pulsing
            self.update_projects_display()

        except Exception as e:
            logger.error(f"Animation update error: {e}")

        # Schedule next animation update (50ms = 20 FPS)
        self.root.after(50, self.update_animations)

    def update_comparison_fast(self, data):
        """Update comparison text using data from queue (FAST)"""
        try:
            instances = data['instances']
            psutil_count = sum(len(inst.terminals) for inst in instances)
            ws_count = data['ws_terminal_count']

            self.comparison_text.delete('1.0', tk.END)

            output = f"psutil: {len(instances)} instancias, {psutil_count} terminales\n"
            output += f"WebSocket: {ws_count} terminales monitoreados\n\n"

            if psutil_count > 0 and ws_count == 0:
                output += ">>> DISCREPANCIA CRITICA <<<\n"
                output += f"psutil detecta {psutil_count} terminales\n"
                output += "WebSocket NO detecta nada (syncExistingTerminals fallo)\n"
            elif psutil_count != ws_count:
                output += f">>> DISCREPANCIA: psutil={psutil_count} vs ws={ws_count}\n"
            else:
                output += ">>> SYNC OK <<<\n"

            self.comparison_text.insert('1.0', output)

        except Exception as e:
            logger.error(f"Comparison update error: {e}")

    def update_footer_fast(self, data):
        """Update footer with current stats (FAST)"""
        try:
            instances = data['instances']
            terminal_count = sum(len(inst.terminals) for inst in instances)
            status_text = f"● SISTEMA OPERATIVO | {len(instances)} PROYECTOS ACTIVOS | "
            status_text += f"{terminal_count} TERMINALES | CPU: {int(data['cpu'])}% | RAM: {int(data['ram'])}%"
            self.footer_label.config(text=status_text)
        except Exception as e:
            logger.error(f"Footer update error: {e}")

    def update_ui(self, cpu, ram, disk):
        """Update UI elements (must run on main thread)"""
        try:
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)

            # Update metrics
            self.cpu_label.config(text=str(int(cpu)))
            self.ram_label.config(text=str(int(ram)))
            self.disk_label.config(text=str(int(disk)))

            # Update terminal count
            terminal_count = self.get_terminal_count()
            self.terminals_label.config(text=str(terminal_count))

            # Update comparison
            self.update_comparison()

            # Update projects
            self.update_projects_display()

            # Update graphs
            self.draw_graph(self.cpu_canvas, self.cpu_history, '#00ff00')
            self.draw_graph(self.ram_canvas, self.ram_history, '#ffff00')
            self.draw_graph(self.disk_canvas, self.disk_history, '#00ffff')

            # Update footer
            self.update_footer()

        except Exception as e:
            logger.error(f"UI update error: {e}")

    def get_cached_instances(self):
        """Get VS Code instances with caching (refresh every 10s, not every 2s)"""
        current_time = time.time()

        # If cache is fresh (less than 10 seconds old), return it
        if current_time - self.instances_cache_time < self.cache_ttl:
            return self.instances_cache

        # Cache is stale, refresh it
        try:
            if self.psutil_monitor:
                self.instances_cache = self.psutil_monitor.find_vscode_instances()
                self.instances_cache_time = current_time
            else:
                self.instances_cache = []
        except Exception as e:
            logger.error(f"Failed to refresh instances cache: {e}")
            self.instances_cache = []

        return self.instances_cache

    def get_terminal_count(self):
        """Get total terminal count from both sources"""
        try:
            instances = self.get_cached_instances()
            return sum(len(inst.terminals) for inst in instances)
        except:
            return 0

    def update_comparison(self):
        """Update comparison text (psutil vs WebSocket)"""
        try:
            instances = self.get_cached_instances()
            if not instances and not self.psutil_monitor:
                self.comparison_text.delete('1.0', tk.END)
                self.comparison_text.insert('1.0', "psutil monitor not available")
                return

            psutil_count = sum(len(inst.terminals) for inst in instances)

            ws_count = 0
            if self.vscode_manager:
                projects = self.vscode_manager.get_all_projects()
                ws_count = sum(len(p.terminals) for p in projects)

            self.comparison_text.delete('1.0', tk.END)

            output = f"psutil: {len(instances)} instancias, {psutil_count} terminales\n"
            output += f"WebSocket: {ws_count} terminales monitoreados\n\n"

            if psutil_count > 0 and ws_count == 0:
                output += ">>> DISCREPANCIA CRITICA <<<\n"
                output += "psutil detecta terminales, pero WebSocket no.\n"
                output += "Causa: syncExistingTerminals() no ejecutado.\n"
            elif psutil_count != ws_count:
                output += ">>> DISCREPANCIA PARCIAL <<<\n"
                output += f"Diferencia: {abs(psutil_count - ws_count)} terminales\n"
            else:
                output += ">>> SINCRONIZACION OK <<<\n"

            self.comparison_text.insert('1.0', output)

        except Exception as e:
            self.comparison_text.delete('1.0', tk.END)
            self.comparison_text.insert('1.0', f"Error: {e}")

    def update_projects_display(self):
        """Update vertical projects list with pulsing indicators (like expectativa.png)"""
        try:
            instances = self.current_instances

            # Clear existing widgets
            for widget in self.projects_frame.winfo_children():
                widget.destroy()

            # Update count
            if hasattr(self, 'projects_count_label'):
                self.projects_count_label.config(text=f"({len(instances)})")

            if not instances:
                no_proj = tk.Label(
                    self.projects_frame,
                    text="No se detectaron proyectos",
                    font=('Courier New', 10),
                    bg='#000000',
                    fg='#666666'
                )
                no_proj.pack(pady=20)
                return

            # Create vertical project cards
            for i, inst in enumerate(instances):
                self.create_project_card(inst, i)

        except Exception as e:
            logger.error(f"Projects display update error: {e}")

    def create_project_card(self, inst, index):
        """Create a single project card (vertical layout like expectativa.png)"""
        # Card frame
        card = tk.Frame(self.projects_frame, bg='#0a0a0a', relief='solid', borderwidth=1)
        card.pack(fill='x', padx=5, pady=5)

        # Header with pulsing circle + name
        header = tk.Frame(card, bg='#0a0a0a')
        header.pack(fill='x', padx=10, pady=10)

        # Pulsing circle (left side)
        pulse_size = int(8 + math.sin(self.pulse_phase / 10.0 + index) * 3)
        has_terminals = len(inst.terminals) > 0
        color = '#00ff00' if has_terminals else '#666666'

        circle_canvas = tk.Canvas(header, bg='#0a0a0a', width=20, height=20, highlightthickness=0)
        circle_canvas.pack(side='left', padx=(0, 10))
        circle_canvas.create_oval(
            10 - pulse_size, 10 - pulse_size,
            10 + pulse_size, 10 + pulse_size,
            fill=color, outline=color
        )

        # Project info (right side)
        info_frame = tk.Frame(header, bg='#0a0a0a')
        info_frame.pack(side='left', fill='both', expand=True)

        # Project name
        name = inst.workspace.workspace_name or 'unknown'
        tk.Label(
            info_frame,
            text=name,
            font=('Courier New', 11, 'bold'),
            bg='#0a0a0a',
            fg='#00ff00',
            anchor='w'
        ).pack(fill='x')

        # Status and terminals
        status_text = "Status: RUNNING" if has_terminals else "Status: IDLE"
        term_text = f"Terminales: {len(inst.terminals)}"

        stats_label = tk.Label(
            info_frame,
            text=f"{term_text} | {status_text}",
            font=('Courier New', 8),
            bg='#0a0a0a',
            fg='#666666',
            anchor='w'
        )
        stats_label.pack(fill='x', pady=(2, 0))

    def draw_graph(self, canvas, data, color):
        """Draw animated graph on canvas"""
        try:
            canvas.delete('all')
            width = canvas.winfo_width()
            height = canvas.winfo_height()

            if width <= 1 or height <= 1:
                return

            if len(data) < 2:
                return

            # Draw grid
            for i in range(0, 101, 25):
                y = height - (i / 100 * height)
                canvas.create_line(0, y, width, y, fill='#1a1a1a', width=1)

            # Draw graph line
            points = []
            max_points = min(len(data), 60)
            step = width / max_points

            for i, value in enumerate(list(data)[-max_points:]):
                x = i * step
                y = height - (value / 100 * height)
                points.extend([x, y])

            if len(points) >= 4:
                canvas.create_line(points, fill=color, width=2, smooth=True)

                # Fill area under graph
                fill_points = points + [width, height, 0, height]
                canvas.create_polygon(fill_points, fill=color, stipple='gray25', outline='')

        except Exception as e:
            logger.error(f"Graph drawing error: {e}")

    def update_footer(self):
        """Update footer with system info"""
        try:
            instances = self.get_cached_instances()
            if not instances and not self.psutil_monitor:
                self.footer_label.config(text="● SISTEMA OPERATIVO | psutil not available")
                return

            total_projects = len(instances)
            total_terminals = sum(len(inst.terminals) for inst in instances)

            footer_text = f"● SISTEMA OPERATIVO | {total_projects} PROYECTOS ACTIVOS | "
            footer_text += f"{total_terminals} TERMINALES | CPU: {psutil.cpu_count()} cores"

            self.footer_label.config(text=footer_text)

        except Exception as e:
            self.footer_label.config(text="● SISTEMA OPERATIVO | ERROR")

    def manual_scan(self):
        """Manual scan button handler"""
        try:
            messagebox.showinfo(
                "Escaneando",
                "Escaneando proyectos y terminales...\nRevisa el panel de comparacion."
            )
            self.update_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al escanear: {e}")

    def force_update(self):
        """Force update button handler"""
        try:
            self.update_data()
        except Exception as e:
            logger.error(f"Force update error: {e}")

    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

    def on_closing(self):
        """Handle window close - stop background thread gracefully"""
        logger.info("Closing Epic Dashboard - stopping background thread...")
        self.stop_thread.set()  # Signal thread to stop
        if hasattr(self, 'update_thread'):
            self.update_thread.join(timeout=2)  # Wait up to 2 seconds
        self.root.destroy()


def show_epic_dashboard(vscode_manager=None):
    """
    Show the epic cyberpunk dashboard.

    Args:
        vscode_manager: VSCodeIntegrationManager instance (optional)
    """
    dashboard = EpicDashboard(vscode_manager=vscode_manager)
    dashboard.run()


if __name__ == "__main__":
    # Test the dashboard
    show_epic_dashboard()
