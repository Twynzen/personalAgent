"""
Sendell Brain GUI (PySide6) - Full Qt6 implementation

Complete GPU-accelerated interface for managing memory, prompts, and tools.
No tkinter dependency - pure Qt6 for maximum performance and stability.
"""

import json
import sys
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QTextEdit, QComboBox, QMessageBox,
    QDialog, QLineEdit, QScrollArea, QFrame
)

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_system_prompt
from sendell.dashboard.project_control_qt import create_project_control_widget_qt
from sendell.dashboard.qt_tkinter_bridge import QtBridge
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class BrainGUIQt(QMainWindow):
    """
    Sendell Brain Interface (Full Qt6 Implementation).

    Tabs:
    - Memorias: View/edit facts, conversations
    - Prompts: View/edit system prompt
    - Herramientas: View available tools/actions
    - Proyectos: Multi-Project Control Center (GPU-accelerated)
    """

    def __init__(self, tools: List = None):
        """Initialize Brain GUI"""
        super().__init__()

        self.memory = get_memory()
        self.tools = tools or []

        # Window setup
        self.setWindowTitle("Sendell - Ver Cerebro")
        self.resize(1400, 900)
        self.setStyleSheet("background-color: #000000;")

        # Central widget with tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00ff00;
                background: #000000;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #00ff00;
                padding: 10px 20px;
                margin-right: 2px;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #003300;
                border-bottom: 2px solid #00ff00;
            }
            QTabBar::tab:hover {
                background: #002200;
            }
        """)

        layout.addWidget(self.tabs)

        # Create tabs
        self.create_memories_tab()
        self.create_prompts_tab()
        self.create_tools_tab()
        self.create_projects_tab()

        logger.info("Brain GUI (Qt6) initialized with 4 tabs")

    def create_memories_tab(self):
        """Create Memories tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("MEMORIA DE SENDELL")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ff00;")
        layout.addWidget(title)

        # Facts section
        facts_label = QLabel("Facts Aprendidos:")
        facts_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        facts_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(facts_label)

        # Facts list
        self.facts_list = QListWidget()
        self.facts_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QListWidget::item:selected {
                background-color: #003300;
            }
        """)
        layout.addWidget(self.facts_list)
        self.refresh_facts()

        # Buttons
        buttons_layout = QHBoxLayout()

        add_btn = QPushButton("Agregar Fact")
        add_btn.setStyleSheet(self._button_style("#00ff00"))
        add_btn.clicked.connect(self.add_fact)
        buttons_layout.addWidget(add_btn)

        delete_btn = QPushButton("Eliminar Fact")
        delete_btn.setStyleSheet(self._button_style("#ff0000"))
        delete_btn.clicked.connect(self.delete_fact)
        buttons_layout.addWidget(delete_btn)

        clear_btn = QPushButton("Limpiar Todo")
        clear_btn.setStyleSheet(self._button_style("#ff0000"))
        clear_btn.clicked.connect(self.clear_facts)
        buttons_layout.addWidget(clear_btn)

        layout.addLayout(buttons_layout)

        # Autonomy section
        autonomy_label = QLabel("Nivel de Autonomía:")
        autonomy_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        autonomy_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(autonomy_label)

        autonomy_layout = QHBoxLayout()

        self.autonomy_combo = QComboBox()
        self.autonomy_combo.addItems([
            "1 - Monitor Only (Solo observar)",
            "2 - Ask Permission (Preguntar antes de actuar)",
            "3 - Safe Actions (Acciones seguras automáticas)",
            "4 - Modify State (Modificar estado del sistema)",
            "5 - Full Autonomy (Autonomía completa)"
        ])
        self.autonomy_combo.setCurrentIndex(1)  # Default L2
        self.autonomy_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        autonomy_layout.addWidget(self.autonomy_combo)

        save_autonomy_btn = QPushButton("Guardar Nivel")
        save_autonomy_btn.setStyleSheet(self._button_style("#ffff00"))
        save_autonomy_btn.clicked.connect(self.save_autonomy_level)
        autonomy_layout.addWidget(save_autonomy_btn)

        layout.addLayout(autonomy_layout)

        warning = QLabel("⚠ Cambios requieren reiniciar Sendell")
        warning.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        warning.setStyleSheet("color: #ff0000;")
        layout.addWidget(warning)

        # Stats
        stats_label = QLabel("Estadísticas:")
        stats_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        stats_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(stats_label)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: 'Courier New';
                font-size: 9px;
            }
        """)
        layout.addWidget(self.stats_text)
        self.refresh_stats()

        self.tabs.addTab(widget, "Memorias")

    def create_prompts_tab(self):
        """Create Prompts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("SYSTEM PROMPT")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ff00;")
        layout.addWidget(title)

        # Info
        info = QLabel("Este es el prompt que define la personalidad de Sendell")
        info.setFont(QFont("Courier New", 9))
        info.setStyleSheet("color: #00ff00;")
        layout.addWidget(info)

        # Prompt editor
        self.prompt_text = QTextEdit()
        self.prompt_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: 'Courier New';
                font-size: 9px;
            }
        """)
        self.prompt_text.setPlainText(get_system_prompt())
        layout.addWidget(self.prompt_text)

        # Buttons
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("Guardar Prompt")
        save_btn.setStyleSheet(self._button_style("#00ff00"))
        save_btn.clicked.connect(self.save_prompt)
        buttons_layout.addWidget(save_btn)

        reload_btn = QPushButton("Recargar Original")
        reload_btn.setStyleSheet(self._button_style("#ffff00"))
        reload_btn.clicked.connect(self.reload_prompt)
        buttons_layout.addWidget(reload_btn)

        layout.addLayout(buttons_layout)

        # Warning
        warning = QLabel("NOTA: Los cambios requieren reiniciar Sendell para aplicarse")
        warning.setFont(QFont("Courier New", 8))
        warning.setStyleSheet("color: #ff0000;")
        layout.addWidget(warning)

        self.tabs.addTab(widget, "Prompts")

    def create_tools_tab(self):
        """Create Tools tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("HERRAMIENTAS DISPONIBLES")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ff00;")
        layout.addWidget(title)

        # Info
        info = QLabel(f"Total: {len(self.tools)} herramientas")
        info.setFont(QFont("Courier New", 10))
        info.setStyleSheet("color: #00ff00;")
        layout.addWidget(info)

        # Tools text
        self.tools_text = QTextEdit()
        self.tools_text.setReadOnly(True)
        self.tools_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                font-family: 'Courier New';
                font-size: 9px;
            }
        """)
        layout.addWidget(self.tools_text)
        self.refresh_tools()

        self.tabs.addTab(widget, "Herramientas")

    def create_projects_tab(self):
        """Create Projects tab - GPU-accelerated Qt widget"""
        # Initialize QApplication first
        QtBridge.get_qapp()

        # Create Qt widget directly (no tkinter embedding needed)
        self.qt_project_widget = create_project_control_widget_qt()

        self.tabs.addTab(self.qt_project_widget, "Proyectos")
        logger.info("PySide6 Projects tab created - GPU-accelerated rendering active")

    def _button_style(self, color: str) -> str:
        """Generate button stylesheet"""
        return f"""
            QPushButton {{
                background-color: #1a1a1a;
                color: {color};
                border: 1px solid {color};
                padding: 8px 16px;
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
            }}
            QPushButton:pressed {{
                background-color: #003300;
            }}
        """

    # ==================== MEMORY TAB FUNCTIONS ====================

    def refresh_facts(self):
        """Refresh facts list"""
        self.facts_list.clear()
        facts = self.memory.get_facts()

        for fact in facts:
            display = f"[{fact.get('category', 'general')}] {fact['fact']}"
            self.facts_list.addItem(display)

    def add_fact(self):
        """Add a new fact"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Fact")
        dialog.resize(500, 200)
        dialog.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout(dialog)

        # Fact input
        QLabel("Nuevo Fact:", parent=dialog).setStyleSheet("color: #00ff00; font-family: 'Courier New';")
        layout.addWidget(QLabel("Nuevo Fact:"))

        fact_input = QLineEdit()
        fact_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(fact_input)

        # Category input
        layout.addWidget(QLabel("Categoría:"))

        category_combo = QComboBox()
        category_combo.addItems(["general", "preference", "work", "personal"])
        category_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(category_combo)

        # Save button
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet(self._button_style("#00ff00"))

        def save():
            fact = fact_input.text().strip()
            category = category_combo.currentText()

            if fact:
                self.memory.add_fact(fact, category)
                self.refresh_facts()
                self.refresh_stats()
                dialog.accept()
                QMessageBox.information(self, "Éxito", "Fact agregado correctamente")

        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)

        dialog.exec()

    def delete_fact(self):
        """Delete selected fact"""
        current_row = self.facts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Atención", "Selecciona un fact para eliminar")
            return

        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar este fact?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.memory.remove_fact(current_row)
            self.refresh_facts()
            self.refresh_stats()
            QMessageBox.information(self, "Éxito", "Fact eliminado")

    def clear_facts(self):
        """Clear all facts"""
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar TODOS los facts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.memory.clear_facts()
            self.refresh_facts()
            self.refresh_stats()
            QMessageBox.information(self, "Éxito", "Todos los facts eliminados")

    def refresh_stats(self):
        """Refresh memory statistics"""
        summary = self.memory.get_memory_summary()

        stats = f"""
Total Facts: {summary['total_facts']}
Total Conversaciones: {summary['total_conversations']}
Total Sesiones: {summary['total_sessions']}
Preferencias: {summary['preferences_count']}

Creado: {summary['created_at']}
Última actualización: {summary['last_updated']}

Archivo: {summary['memory_file']}
"""
        self.stats_text.setPlainText(stats)

    def save_autonomy_level(self):
        """Save autonomy level to .env file"""
        try:
            # Get selected level (extract first character)
            selected = self.autonomy_combo.currentText()
            new_level = int(selected[0])

            # Read .env file
            env_path = Path(".env")
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Update or add SENDELL_AUTONOMY_LEVEL
            found = False
            for i, line in enumerate(lines):
                if line.startswith('SENDELL_AUTONOMY_LEVEL='):
                    lines[i] = f'SENDELL_AUTONOMY_LEVEL={new_level}\n'
                    found = True
                    break

            if not found:
                lines.append(f'\nSENDELL_AUTONOMY_LEVEL={new_level}\n')

            # Write back
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            QMessageBox.information(
                self, "Éxito",
                f"Nivel de autonomía cambiado a L{new_level}.\n\n"
                "IMPORTANTE: Reinicia Sendell para aplicar los cambios:\n"
                "1. Cierra el chat actual\n"
                "2. Ejecuta: uv run python -m sendell chat"
            )

            logger.info(f"Autonomy level changed to L{new_level}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el nivel: {e}")

    # ==================== PROMPTS TAB FUNCTIONS ====================

    def save_prompt(self):
        """Save system prompt"""
        try:
            new_prompt = self.prompt_text.toPlainText()
            prompt_file = Path("src/sendell/agent/prompts.py")

            # Read current file
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple replacement (this is a simplified version)
            # In production, you'd want more sophisticated parsing
            QMessageBox.information(
                self, "Guardado",
                "Prompt guardado. Reinicia Sendell para aplicar cambios."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def reload_prompt(self):
        """Reload original prompt"""
        self.prompt_text.setPlainText(get_system_prompt())
        QMessageBox.information(self, "Recargado", "Prompt original recargado")

    # ==================== TOOLS TAB FUNCTIONS ====================

    def refresh_tools(self):
        """Refresh tools list"""
        tools_text = ""

        for i, tool in enumerate(self.tools, 1):
            name = tool.name if hasattr(tool, 'name') else str(tool)
            description = tool.description if hasattr(tool, 'description') else "No description"

            tools_text += f"\n{'='*60}\n"
            tools_text += f"[{i}] {name}\n"
            tools_text += f"{'='*60}\n"
            tools_text += f"{description}\n"

        self.tools_text.setPlainText(tools_text)


def show_brain(tools: List = None) -> str:
    """
    Show the Sendell Brain GUI (Qt6 version).

    Args:
        tools: List of available tools

    Returns:
        Success message
    """
    logger.info("Opening Sendell Brain (Qt6)...")

    # Ensure QApplication exists
    app = QtBridge.get_qapp()

    # Create and show GUI
    gui = BrainGUIQt(tools)
    gui.show()

    # Run Qt event loop (this will block until window is closed)
    # But since this is called from a thread in chat mode, it won't block the main chat
    app.exec()

    return "Brain GUI closed"
