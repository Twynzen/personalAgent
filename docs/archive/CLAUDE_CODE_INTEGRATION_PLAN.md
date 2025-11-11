# 🎯 PLAN: Claude Code Terminal Integration & Control

**Fecha**: 2025-11-10
**Objetivo**: Integrar control bidireccional de terminales Claude Code desde Sendell Dashboard
**Complejidad**: Alta (manejo de terminales, detección de estados, comunicación bidireccional)

---

## 📋 RESUMEN EJECUTIVO

### Lo que queremos lograr:

**Desde el Dashboard de Sendell:**
1. Ver qué proyectos VS Code están abiertos
2. Abrir terminal Claude Code en un proyecto con un click
3. Ver el terminal en tiempo real (en navegador o ventana dedicada)
4. Enviar comandos/instrucciones a Claude Code
5. Ver las respuestas de Claude Code
6. Detectar automáticamente el estado de Claude Code

### Estados redefinidos:

| Color | Estado | Significado | Gráfica |
|-------|--------|-------------|---------|
| 🔴 **ROJO** | `offline` | VS Code abierto, NO hay terminal Claude Code activo | Línea plana |
| 🔵 **AZUL** | `idle` | Terminal Claude Code iniciado, esperando comandos o confirmación del usuario | Línea casi plana |
| 🟢 **VERDE** | `running` | Claude Code está ejecutando/escribiendo/trabajando activamente | ECG heartbeat |

---

## 🏗️ ARQUITECTURA TÉCNICA NECESARIA

### Componentes a implementar:

```
┌─────────────────────────────────────────────────────────────┐
│              SENDELL DASHBOARD (Angular)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Project Card                                           │ │
│  │  ┌────────────────────────────────────────────┐        │ │
│  │  │  [sendell] - Estado: IDLE 🔵                │        │ │
│  │  │  Gráfica ECG ~~~~~~~                         │        │ │
│  │  │  Path: C:\...\sendell                       │        │ │
│  │  │  ┌────────────────┐  ┌──────────────────┐  │        │ │
│  │  │  │ Open Terminal  │  │  View Terminal   │  │        │ │
│  │  │  └────────────────┘  └──────────────────┘  │        │ │
│  │  └────────────────────────────────────────────┘        │ │
│  │                                                          │ │
│  │  Terminal Viewer (modal/panel)                         │ │
│  │  ┌────────────────────────────────────────────┐        │ │
│  │  │  $ claude                                    │        │ │
│  │  │  Claude Code v0.x.x                         │        │ │
│  │  │  > User: Fix the login bug                  │        │ │
│  │  │  > Claude: [thinking...]                    │        │ │
│  │  │  > Claude: Let me analyze...                │        │ │
│  │  │  ┌──────────────────────────────────────┐   │        │ │
│  │  │  │ Send command: [_______________] [>>] │   │        │ │
│  │  │  └──────────────────────────────────────┘   │        │ │
│  │  └────────────────────────────────────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket
┌───────────────────────▼─────────────────────────────────────┐
│            SENDELL BACKEND (Python)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Terminal Manager                                       │ │
│  │  - Detecta terminales Claude Code                      │ │
│  │  - Abre nuevos terminales                              │ │
│  │  - Envía comandos                                      │ │
│  │  - Captura output en tiempo real                       │ │
│  │  - Detecta estado (idle vs running)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               VS CODE (Workspace)                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Terminal 1: bash (user manual)                        │ │
│  │  Terminal 2: claude  ← CONTROLADO POR SENDELL          │ │
│  │  Terminal 3: npm run dev                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 INVESTIGACIÓN NECESARIA (Para Daniel)

### 1. **Abrir Terminal Programáticamente en VS Code**

**Pregunta clave:** ¿Cómo abrir un terminal específico (claude) en un proyecto VS Code desde Python/CLI?

**Opciones a investigar:**
- ✅ `code` CLI con argumentos de terminal
- ✅ Automatización con `pyautogui` (muy hacky, último recurso)
- ✅ Extension API de VS Code (si existiera forma de invocar desde fuera)
- ✅ Script shell que abre VS Code + terminal automáticamente

**Comando a probar:**
```bash
# ¿Esto funciona?
code /path/to/project --new-window --command "terminal.new" --command "terminal.sendText 'claude'"

# ¿O esto?
code /path/to/project && echo "claude" > /dev/tty
```

**Documentación a revisar:**
- VS Code CLI arguments: https://code.visualstudio.com/docs/editor/command-line
- Terminal automation: https://code.visualstudio.com/api/references/vscode-api#Terminal

---

### 2. **Detectar si un Terminal es Claude Code**

**Pregunta clave:** ¿Cómo saber si un terminal está ejecutando Claude Code?

**Métodos a investigar:**
- ✅ Nombre del proceso (psutil): ¿El proceso hijo es "claude"?
- ✅ Título del terminal (si está expuesto)
- ✅ Output parsing: Detectar "Claude Code" en las primeras líneas
- ✅ PID tracking: Comparar con procesos conocidos de Claude

**Script de prueba Python:**
```python
import psutil

# Encuentra terminales de VS Code
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if 'code' in proc.info['name'].lower():
        # Revisa procesos hijos
        children = proc.children(recursive=True)
        for child in children:
            if 'claude' in child.name().lower():
                print(f"Found Claude Code terminal: PID {child.pid}")
```

---

### 3. **Enviar Comandos a un Terminal Específico**

**Pregunta clave:** ¿Cómo enviar texto a un terminal ya abierto en VS Code?

**Opciones a investigar:**
- ✅ `tmux` / `screen` (si VS Code usa alguno)
- ✅ PTY (pseudo-terminal) manipulation
- ✅ VS Code Extension que expone API REST/WebSocket para control
- ✅ `xdotool` / `AutoHotkey` (hacky pero funcional)

**Conceptos clave:**
- **PTY (Pseudo-Terminal)**: ¿Claude Code usa PTY que podamos controlar?
- **Terminal ID**: ¿VS Code asigna IDs únicos a terminales?

**Documentación crítica:**
- Python `pty` module: https://docs.python.org/3/library/pty.html
- VS Code Terminal API: https://code.visualstudio.com/api/references/vscode-api#Terminal.sendText

---

### 4. **Capturar Output de Terminal en Tiempo Real**

**Pregunta clave:** ¿Cómo leer lo que Claude Code está escribiendo en el terminal?

**Opciones a investigar:**
- ✅ Shell Integration API de VS Code (si da acceso a output)
- ✅ PTY monitoring con Python
- ✅ Log file de Claude Code (si existe)
- ✅ Extension propia de VS Code que reenvía output vía WebSocket

**Conceptos clave:**
- **Stream capture**: Interceptar stdout/stderr del proceso
- **Buffer reading**: Leer últimas N líneas sin bloquear

**Script de prueba:**
```python
import subprocess

# ¿Podemos capturar output así?
process = subprocess.Popen(
    ['claude'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Lectura no bloqueante
import select
while True:
    ready, _, _ = select.select([process.stdout], [], [], 0.1)
    if ready:
        line = process.stdout.readline()
        print(f"Claude output: {line}")
```

---

### 5. **Detectar Estado de Claude Code (idle vs running)**

**Pregunta clave:** ¿Cómo saber si Claude está pensando/ejecutando vs esperando input?

**Indicadores posibles:**
- ✅ Output patterns: "[thinking]", "Working on", "Complete"
- ✅ CPU usage del proceso
- ✅ Presencia de prompt en última línea
- ✅ Timestamps entre líneas de output

**Regex patterns a testear:**
```python
import re

# Detectar estados
CLAUDE_THINKING = re.compile(r'\[thinking\]|\[working\]|Analyzing')
CLAUDE_WAITING = re.compile(r'> User:|Do you want to proceed')
CLAUDE_DONE = re.compile(r'Complete|Finished|Done')
```

---

## 📝 RESUMEN DE INVESTIGACIÓN REQUERIDA

Daniel debe investigar y documentar:

1. **Terminal Opening**: ¿Cómo abrir `claude` en un proyecto VS Code desde CLI/Python?
2. **Terminal Detection**: ¿Cómo detectar que un terminal específico es Claude Code?
3. **Command Sending**: ¿Cómo enviar texto a ese terminal?
4. **Output Capture**: ¿Cómo capturar lo que Claude escribe en tiempo real?
5. **State Detection**: ¿Cómo detectar si Claude está idle/running/waiting?

**Formato del documento de investigación:**
- Métodos probados (con código de ejemplo)
- Métodos que funcionan (con pros/cons)
- Método recomendado
- Dependencias necesarias (si hay)
- Limitaciones conocidas

---

## 🛠️ PLAN DE IMPLEMENTACIÓN (Post-Investigación)

### Fase 1: Terminal Control Backend (Python)

**Branch:** `feature/claude-terminal-control`

**Archivos a crear:**
```
src/sendell/claude_integration/
├── __init__.py
├── terminal_controller.py    # Abrir, enviar comandos, detectar
├── output_monitor.py          # Capturar output en tiempo real
├── state_detector.py          # idle/running/waiting
└── types.py                   # ClaudeTerminal, TerminalState, etc.
```

**Implementación:**
```python
# terminal_controller.py
class ClaudeTerminalController:
    def open_claude_in_project(self, project_path: str) -> ClaudeTerminal:
        """Abre terminal Claude Code en proyecto VS Code"""
        pass

    def send_command(self, terminal_id: str, command: str) -> bool:
        """Envía comando a terminal Claude Code"""
        pass

    def get_output(self, terminal_id: str, lines: int = 50) -> str:
        """Obtiene últimas N líneas de output"""
        pass

# state_detector.py
class ClaudeStateDetector:
    def detect_state(self, recent_output: str) -> TerminalState:
        """Detecta estado basándose en output reciente"""
        # idle, running, waiting_confirmation
        pass
```

---

### Fase 2: WebSocket Events (Python Backend)

**Branch:** `feature/claude-terminal-websocket`

**Archivos a modificar:**
```
src/sendell/web/websocket.py     # Agregar eventos de terminal
src/sendell/web/routes.py         # Endpoints REST para control
```

**Eventos WebSocket nuevos:**
```python
# Cliente → Servidor
{
    "type": "terminal_open",
    "project_path": "/path/to/project"
}

{
    "type": "terminal_send_command",
    "terminal_id": "abc123",
    "command": "Fix the login bug in auth.py"
}

# Servidor → Cliente
{
    "type": "terminal_output",
    "terminal_id": "abc123",
    "output": "Claude: Let me analyze the code...",
    "state": "running"
}

{
    "type": "terminal_state_change",
    "terminal_id": "abc123",
    "old_state": "running",
    "new_state": "waiting_confirmation"
}
```

---

### Fase 3: Dashboard UI (Angular)

**Branch:** `feature/claude-terminal-ui`

**Componentes a crear:**
```
sendell-dashboard/src/app/components/
├── terminal-viewer.component.ts      # Modal/panel de terminal
├── terminal-viewer.component.html
├── terminal-viewer.component.scss
└── terminal-control-buttons.component.ts
```

**Funcionalidades UI:**
1. Botón "Open Claude Terminal" en project card
2. Modal/panel que muestra terminal output
3. Input para enviar comandos
4. Indicador de estado (thinking spinner, etc.)
5. Auto-scroll para nuevo output

---

### Fase 4: State Detection & Graph Update

**Branch:** `feature/claude-state-integration`

**Lógica de estados:**
```typescript
// app.ts
private mapProjectsWithStatus(projects: Project[]): Project[] {
    return projects.map(project => {
        // Verificar si tiene terminal Claude activo
        const hasClaudeTerminal = this.hasClaudeTerminal(project);

        if (!hasClaudeTerminal) {
            return { ...project, status: 'offline' };
        }

        // Verificar estado del terminal
        const terminalState = this.getTerminalState(project.terminal_id);

        if (terminalState === 'running') {
            return { ...project, status: 'running' };
        } else {
            return { ...project, status: 'idle' };
        }
    });
}
```

---

## 🎯 TAREAS ORDENADAS (Roadmap)

### Hoy (Post-Push):
1. ✅ Commit actual
2. ✅ Push a remote
3. ✅ Merge a `main`
4. ✅ Daniel hace investigación de terminales

### Próxima sesión (Con investigación completa):
1. **Branch 1**: Implementar `ClaudeTerminalController` basado en findings
2. **Branch 2**: Agregar eventos WebSocket para control de terminal
3. **Branch 3**: Crear componente `TerminalViewer` en Angular
4. **Branch 4**: Integrar detección de estado con gráficas
5. **Branch 5**: Testing end-to-end completo

---

## ⚠️ RIESGOS Y CONSIDERACIONES

### Riesgo 1: No hay forma limpia de controlar terminales VS Code
**Probabilidad**: Media
**Mitigación**: Usar extension VS Code propia que expone WebSocket API

### Riesgo 2: Claude Code no expone estado claramente
**Probabilidad**: Alta
**Mitigación**: Usar heurísticas (output parsing, CPU usage, timing)

### Riesgo 3: Captura de output es muy lenta
**Probabilidad**: Baja
**Mitigación**: Buffer y throttling, mostrar solo últimas 100 líneas

### Riesgo 4: Múltiples Claude Code sessions simultáneas
**Probabilidad**: Media
**Mitigación**: Terminal ID único, tracking por proyecto

---

## 🚀 ENTREGABLES ESPERADOS

Al completar esta fase, Sendell Dashboard podrá:

✅ Detectar proyectos VS Code con/sin Claude Code
✅ Abrir Claude Code en un proyecto con un click
✅ Ver terminal Claude Code en tiempo real
✅ Enviar comandos a Claude Code
✅ Detectar automáticamente estado (offline/idle/running)
✅ Actualizar gráficas según actividad real de Claude

---

## 📚 DOCUMENTACIÓN A GENERAR

1. **TERMINAL_CONTROL_RESEARCH.md** (Daniel): Findings de investigación
2. **CLAUDE_INTEGRATION_API.md**: Documentación de API interna
3. **TERMINAL_VIEWER_GUIDE.md**: Cómo usar el viewer desde dashboard

---

**Próximo paso:** Daniel hace push, merge a main, y completa investigación de terminales. Luego próxima sesión implementamos basándose en findings.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
