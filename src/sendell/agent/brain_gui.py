"""
Sendell Brain GUI - Visual interface to manage memory, prompts, and tools.

Usage:
    from sendell.agent.brain_gui import show_brain
    show_brain()
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Dict

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_system_prompt
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class BrainGUI:
    """
    Sendell Brain Interface.

    Tabs:
    - Memories: View/edit facts, conversations
    - Prompts: View/edit system prompt
    - Tools: View available tools/actions
    """

    def __init__(self, tools: List = None):
        """Initialize Brain GUI"""
        self.memory = get_memory()
        self.tools = tools or []

        # Create main window
        self.root = tk.Tk()
        self.root.title("Sendell - Ver Cerebro")
        self.root.geometry("900x700")
        self.root.configure(bg='#000000')

        # Create notebook (tabs)
        style = ttk.Style()
        style.theme_use('default')

        # Style for dark theme
        style.configure('TNotebook', background='#000000', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#00ff00',
                       padding=[20, 10], font=('Consolas', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#000000')],
                 foreground=[('selected', '#00ff00')])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_memory_tab()
        self.create_prompts_tab()
        self.create_tools_tab()

        logger.info("Brain GUI initialized")

    def create_memory_tab(self):
        """Create Memories tab"""
        frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(frame, text='Memorias')

        # Title
        title = tk.Label(frame, text="MEMORIA DE SENDELL", font=('Consolas', 16, 'bold'),
                        bg='#000000', fg='#00ff00')
        title.pack(pady=10)

        # Facts section
        facts_label = tk.Label(frame, text="Facts Aprendidos:", font=('Consolas', 12, 'bold'),
                              bg='#000000', fg='#00ff00')
        facts_label.pack(pady=5)

        # Facts listbox with scrollbar
        facts_frame = tk.Frame(frame, bg='#000000')
        facts_frame.pack(fill='both', expand=True, padx=20, pady=5)

        scrollbar = tk.Scrollbar(facts_frame)
        scrollbar.pack(side='right', fill='y')

        self.facts_listbox = tk.Listbox(facts_frame, font=('Consolas', 10),
                                        bg='#1a1a1a', fg='#00ff00',
                                        selectbackground='#003300',
                                        yscrollcommand=scrollbar.set,
                                        height=10)
        self.facts_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.facts_listbox.yview)

        # Load facts
        self.refresh_facts()

        # Buttons for facts
        buttons_frame = tk.Frame(frame, bg='#000000')
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="Agregar Fact", command=self.add_fact,
                 bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10),
                 activebackground='#003300').pack(side='left', padx=5)

        tk.Button(buttons_frame, text="Eliminar Fact", command=self.delete_fact,
                 bg='#1a1a1a', fg='#ff0000', font=('Consolas', 10),
                 activebackground='#330000').pack(side='left', padx=5)

        tk.Button(buttons_frame, text="Limpiar Todo", command=self.clear_facts,
                 bg='#1a1a1a', fg='#ff0000', font=('Consolas', 10),
                 activebackground='#330000').pack(side='left', padx=5)

        # Autonomy Level Control
        autonomy_frame = tk.Frame(frame, bg='#000000')
        autonomy_frame.pack(pady=15)

        autonomy_label = tk.Label(autonomy_frame, text="Nivel de Autonomía:",
                                 font=('Consolas', 12, 'bold'),
                                 bg='#000000', fg='#00ff00')
        autonomy_label.pack()

        # Current level
        from sendell.config import get_settings
        settings = get_settings()
        current_level = settings.agent.autonomy_level.value

        level_info = tk.Label(autonomy_frame,
                             text=f"Actual: L{current_level} - {settings.agent.autonomy_level.name}",
                             font=('Consolas', 10), bg='#000000', fg='#ffff00')
        level_info.pack(pady=5)

        # Level selector
        selector_frame = tk.Frame(autonomy_frame, bg='#000000')
        selector_frame.pack(pady=5)

        tk.Label(selector_frame, text="Cambiar a:", font=('Consolas', 10),
                bg='#000000', fg='#00ff00').pack(side='left', padx=5)

        self.autonomy_var = tk.StringVar(value=str(current_level))
        autonomy_options = [
            "1 - L1: Monitor Only",
            "2 - L2: Ask Permission",
            "3 - L3: Safe Actions",
            "4 - L4: Modify State",
            "5 - L5: Full Autonomy"
        ]

        self.autonomy_combo = ttk.Combobox(selector_frame, textvariable=self.autonomy_var,
                                          values=autonomy_options, width=30,
                                          font=('Consolas', 9), state='readonly')
        self.autonomy_combo.current(current_level - 1)
        self.autonomy_combo.pack(side='left', padx=5)

        tk.Button(selector_frame, text="Guardar", command=self.save_autonomy_level,
                 bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10, 'bold'),
                 activebackground='#003300').pack(side='left', padx=5)

        # Level descriptions
        level_desc = tk.Text(autonomy_frame, font=('Consolas', 8), bg='#1a1a1a',
                            fg='#00ff00', height=6, width=70, wrap='word')
        level_desc.pack(pady=5)
        level_desc.insert('1.0', """L1: Solo observa, nunca actúa
L2: Pregunta siempre antes de actuar (RECOMENDADO)
L3: Ejecuta automáticamente acciones seguras (abrir apps, consultas)
L4: Puede cerrar apps, modificar archivos (requiere cuidado)
L5: Autonomía completa (usar solo si confías totalmente)""")
        level_desc.config(state='disabled')

        # Warning
        warning = tk.Label(autonomy_frame,
                          text="⚠ Cambios requieren reiniciar Sendell",
                          font=('Consolas', 8, 'bold'), bg='#000000', fg='#ff0000')
        warning.pack(pady=5)

        # Memory stats
        stats_label = tk.Label(frame, text="Estadísticas:", font=('Consolas', 12, 'bold'),
                              bg='#000000', fg='#00ff00')
        stats_label.pack(pady=10)

        self.stats_text = tk.Text(frame, font=('Consolas', 9), bg='#1a1a1a', fg='#00ff00',
                                 height=5, width=80)
        self.stats_text.pack(pady=5)
        self.refresh_stats()

    def create_prompts_tab(self):
        """Create Prompts tab"""
        frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(frame, text='Prompts')

        # Title
        title = tk.Label(frame, text="SYSTEM PROMPT", font=('Consolas', 16, 'bold'),
                        bg='#000000', fg='#00ff00')
        title.pack(pady=10)

        # Info label
        info = tk.Label(frame, text="Este es el prompt que define la personalidad de Sendell",
                       font=('Consolas', 9), bg='#000000', fg='#00ff00')
        info.pack(pady=5)

        # Prompt editor
        self.prompt_text = scrolledtext.ScrolledText(frame, font=('Consolas', 9),
                                                     bg='#1a1a1a', fg='#00ff00',
                                                     insertbackground='#00ff00',
                                                     wrap='word')
        self.prompt_text.pack(fill='both', expand=True, padx=20, pady=10)

        # Load current prompt
        current_prompt = get_system_prompt()
        self.prompt_text.insert('1.0', current_prompt)

        # Buttons
        buttons_frame = tk.Frame(frame, bg='#000000')
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="Guardar Prompt", command=self.save_prompt,
                 bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10, 'bold'),
                 activebackground='#003300').pack(side='left', padx=5)

        tk.Button(buttons_frame, text="Recargar Original", command=self.reload_prompt,
                 bg='#1a1a1a', fg='#ffff00', font=('Consolas', 10),
                 activebackground='#333300').pack(side='left', padx=5)

        # Warning
        warning = tk.Label(frame,
                          text="NOTA: Los cambios requieren reiniciar Sendell para aplicarse",
                          font=('Consolas', 8), bg='#000000', fg='#ff0000')
        warning.pack(pady=5)

    def create_tools_tab(self):
        """Create Tools tab"""
        frame = tk.Frame(self.notebook, bg='#000000')
        self.notebook.add(frame, text='Herramientas')

        # Title
        title = tk.Label(frame, text="HERRAMIENTAS DISPONIBLES", font=('Consolas', 16, 'bold'),
                        bg='#000000', fg='#00ff00')
        title.pack(pady=10)

        # Info
        info = tk.Label(frame, text=f"Total: {len(self.tools)} herramientas",
                       font=('Consolas', 10), bg='#000000', fg='#00ff00')
        info.pack(pady=5)

        # Tools list
        tools_frame = tk.Frame(frame, bg='#000000')
        tools_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(tools_frame)
        scrollbar.pack(side='right', fill='y')

        self.tools_text = tk.Text(tools_frame, font=('Consolas', 9),
                                  bg='#1a1a1a', fg='#00ff00',
                                  yscrollcommand=scrollbar.set,
                                  wrap='word')
        self.tools_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.tools_text.yview)

        # Load tools
        self.refresh_tools()

    # ==================== MEMORY TAB FUNCTIONS ====================

    def refresh_facts(self):
        """Refresh facts list"""
        self.facts_listbox.delete(0, tk.END)
        facts = self.memory.get_facts()

        for i, fact in enumerate(facts):
            display = f"[{fact.get('category', 'general')}] {fact['fact']}"
            self.facts_listbox.insert(tk.END, display)

    def add_fact(self):
        """Add a new fact"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Fact")
        dialog.geometry("500x200")
        dialog.configure(bg='#000000')

        tk.Label(dialog, text="Nuevo Fact:", bg='#000000', fg='#00ff00',
                font=('Consolas', 10)).pack(pady=10)

        fact_entry = tk.Entry(dialog, font=('Consolas', 10), bg='#1a1a1a', fg='#00ff00',
                             insertbackground='#00ff00', width=60)
        fact_entry.pack(pady=5)

        tk.Label(dialog, text="Categoría:", bg='#000000', fg='#00ff00',
                font=('Consolas', 10)).pack(pady=5)

        category_var = tk.StringVar(value="general")
        category_menu = ttk.Combobox(dialog, textvariable=category_var,
                                     values=["general", "preference", "work", "personal"],
                                     font=('Consolas', 10))
        category_menu.pack(pady=5)

        def save():
            fact = fact_entry.get().strip()
            category = category_var.get()

            if fact:
                self.memory.add_fact(fact, category)
                self.refresh_facts()
                self.refresh_stats()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Fact agregado correctamente")

        tk.Button(dialog, text="Guardar", command=save, bg='#1a1a1a', fg='#00ff00',
                 font=('Consolas', 10, 'bold')).pack(pady=10)

    def delete_fact(self):
        """Delete selected fact"""
        selection = self.facts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Atención", "Selecciona un fact para eliminar")
            return

        index = selection[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este fact?"):
            self.memory.remove_fact(index)
            self.refresh_facts()
            self.refresh_stats()
            messagebox.showinfo("Éxito", "Fact eliminado")

    def clear_facts(self):
        """Clear all facts"""
        if messagebox.askyesno("Confirmar", "¿Eliminar TODOS los facts?"):
            self.memory.clear_facts()
            self.refresh_facts()
            self.refresh_stats()
            messagebox.showinfo("Éxito", "Todos los facts eliminados")

    def refresh_stats(self):
        """Refresh memory statistics"""
        self.stats_text.delete('1.0', tk.END)
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
        self.stats_text.insert('1.0', stats)
        self.stats_text.config(state='disabled')

    def save_autonomy_level(self):
        """Save autonomy level to .env file"""
        try:
            # Get selected level (extract first character)
            selected = self.autonomy_combo.get()
            new_level = int(selected[0])

            # Read .env file
            env_path = ".env"
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

            messagebox.showinfo(
                "Éxito",
                f"Nivel de autonomía cambiado a L{new_level}.\n\n"
                "IMPORTANTE: Reinicia Sendell para aplicar los cambios:\n"
                "1. Cierra el chat actual\n"
                "2. Ejecuta: uv run python -m sendell chat"
            )

            logger.info(f"Autonomy level changed to L{new_level}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el nivel: {e}")
            logger.error(f"Failed to save autonomy level: {e}")

    # ==================== PROMPTS TAB FUNCTIONS ====================

    def save_prompt(self):
        """Save edited prompt to file"""
        new_prompt = self.prompt_text.get('1.0', tk.END).strip()

        # Save to prompts.py
        prompts_file = "src/sendell/agent/prompts.py"

        try:
            # Read current file
            with open(prompts_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find and replace the prompt content
            # This is a simple approach - in production you'd want more robust parsing
            start_marker = 'prompt = f"""'
            end_marker = '"""'

            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = content.find(end_marker, start_idx)

                if end_idx != -1:
                    # Replace prompt
                    new_content = content[:start_idx] + new_prompt + content[end_idx:]

                    # Save
                    with open(prompts_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    messagebox.showinfo("Éxito",
                                      "Prompt guardado.\n\nREINICIA Sendell para aplicar cambios.")
                else:
                    messagebox.showerror("Error", "No se pudo encontrar el final del prompt")
            else:
                messagebox.showerror("Error", "No se pudo encontrar el prompt en el archivo")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def reload_prompt(self):
        """Reload original prompt"""
        if messagebox.askyesno("Confirmar", "¿Recargar el prompt original?"):
            self.prompt_text.delete('1.0', tk.END)
            self.prompt_text.insert('1.0', get_system_prompt())
            messagebox.showinfo("Éxito", "Prompt recargado")

    # ==================== TOOLS TAB FUNCTIONS ====================

    def refresh_tools(self):
        """Refresh tools list"""
        self.tools_text.delete('1.0', tk.END)

        if not self.tools:
            self.tools_text.insert('1.0', "No hay herramientas cargadas")
            return

        output = f"TOTAL HERRAMIENTAS: {len(self.tools)}\n"
        output += "=" * 80 + "\n\n"

        for i, tool in enumerate(self.tools, 1):
            # Get tool info
            name = getattr(tool, 'name', 'Unknown')
            description = getattr(tool, 'description', 'No description')

            output += f"{i}. {name}\n"
            output += f"   {description}\n"
            output += "-" * 80 + "\n"

        self.tools_text.insert('1.0', output)
        self.tools_text.config(state='disabled')

    # ==================== MAIN ====================

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


def show_brain(tools: List = None):
    """
    Show the Brain GUI.

    Args:
        tools: List of available tools (optional)

    Example:
        >>> from sendell.agent.brain_gui import show_brain
        >>> show_brain()
    """
    gui = BrainGUI(tools=tools)
    gui.run()


if __name__ == "__main__":
    # Test the GUI
    show_brain()
