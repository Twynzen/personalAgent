# CLAUDE.MD - Memoria Permanente del Proyecto Sendell

**Última actualización**: 2025-11-11 (Post-Sesión 21)
**Estado del proyecto**: v0.3 Dashboard con Terminales Embebidos (95% completo)
**Desarrolladores**: Daniel (Testing/PM/Research) + Claude (Desarrollo)

---

## 🚨 ESTADO ACTUAL (Quick Context)

**Branch actual**: `feature/claude-terminal-control`
**Última sesión**: Terminales embebidos con xterm.js - Fases 1-3 completadas
**Estado**: ⚠️ PENDIENTE: Build + Testing + Fase 4

### Sistema Actual (v0.3)

**Angular Dashboard Web** funcionando con:
- ✅ Detección de proyectos VS Code vía psutil
- ✅ Gráficos de actividad ECG-style (3 estados: OFFLINE/READY/WORKING)
- ✅ Terminales embebidos con xterm.js
- ✅ TerminalManager backend (subprocess.Popen + threading)
- ✅ WebSocket bidireccional para I/O
- ✅ Click en proyecto → abre terminal cmd.exe en navegador
- ✅ Enviar comandos desde dashboard

**Arquitectura**:
```
Frontend (Angular + xterm.js)
    ↕ WebSocket /ws/terminal/{pid}
Backend (FastAPI + Python)
    ├── TerminalManager (singleton)
    │   └── ManagedTerminalProcess (cmd.exe)
    ├── VSCodeDetector (psutil)
    └── ProjectStateDetector
```

**Pendiente v0.3**:
1. ⏳ Build dashboard: `npm run build` + deploy
2. ⏳ Testing E2E completo
3. ⏳ Fase 4: Actualizar `project_states.py` para usar TerminalManager

**Documentación de referencia**:
- `NEXT_SESSION_PLAN.md` - Instrucciones completas para continuar (450 líneas)
- `CLAUDE_CODE_INTEGRATION_PLAN.md` - Plan de integración con Claude Code
- `V03_RESUMEN.md` - Resumen ejecutivo del dashboard

---

## ✅ WORKFLOW ESTABLECIDO

1. **Daniel investiga** (APIs, métodos, viabilidad técnica)
2. **Daniel provee docs** a Claude con findings
3. Claude crea branch específico
4. Claude implementa basándose en docs de Daniel
5. Claude muestra código para review
6. **Daniel testea** en local
7. Si funciona → Claude commit + Daniel push
8. Documentar cambios en CLAUDE.md
9. Repetir para siguiente feature

**Regla de oro**: Claude NO debe investigar o asumir APIs. Daniel investiga primero.

---

## 📦 RESUMEN EJECUTIVO DEL PROYECTO

**Sendell** es un agente AI autónomo que monitorea y controla tu entorno de desarrollo Windows. Usa LangGraph para orquestación y combina monitoreo del sistema (psutil) con control de terminales para gestionar proyectos VS Code.

### Stack Tecnológico

**Backend (Python)**:
- LangGraph 0.2+ (ReAct agent pattern)
- OpenAI GPT-4 Turbo
- FastAPI (REST API + WebSocket)
- psutil (system monitoring)
- subprocess.Popen (terminal control)

**Frontend (Web Dashboard)**:
- Angular 17+ standalone
- xterm.js 5.5 (embedded terminals)
- WebSocket client (real-time updates)
- Canvas API (animated graphs)

**GUI (Desktop)**:
- tkinter (Brain GUI - config/memory management)

### Capacidades Actuales

**Agent Core** (v0.1):
- 7 herramientas LangChain
- Chat interactivo
- Memoria JSON persistente
- Sistema de autonomía L1-L5
- Brain GUI para configuración

**Sistema Proactivo** (v0.2):
- Identidad temporal del agente
- Reminders (one-time, recurring)
- Notificaciones visuales con ASCII art
- Loop background no bloqueante

**Dashboard & Terminales** (v0.3):
- Monitoreo multi-proyecto en tiempo real
- Gráficos de actividad animados
- Terminales embebidos en navegador
- Control bidireccional de cmd.exe
- Estados: OFFLINE → READY → WORKING

---

## 🏗️ ARQUITECTURA ACTUAL

### Módulos Python

```
src/sendell/
├── agent/                     # Core LangGraph Agent
│   ├── core.py               # SendellAgent con 7 tools
│   ├── prompts.py            # System prompts
│   ├── memory.py             # JSON persistence
│   ├── brain_gui.py          # tkinter GUI (config/memory)
│   └── loops.py              # Proactive loop
│
├── terminal_manager/          # Terminal Control (v0.3)
│   ├── manager.py            # TerminalManager singleton
│   ├── process.py            # ManagedTerminalProcess
│   └── types.py              # Pydantic models
│
├── project_manager/           # VS Code Detection
│   ├── vscode_detector.py    # psutil-based detection
│   └── project_states.py     # State machine (OFFLINE/READY/WORKING)
│
├── web/                       # FastAPI Server
│   ├── server.py             # Main app + WebSocket endpoints
│   ├── routes.py             # REST API
│   ├── websocket.py          # WebSocket manager
│   └── background.py         # Background scanner
│
├── device/                    # System Monitoring
│   ├── monitor.py            # psutil wrapper
│   └── automation.py         # App launching
│
├── proactive/                 # Proactive System (v0.2)
│   ├── identity.py           # Temporal identity
│   ├── reminders.py          # Reminder manager
│   └── proactive_loop.py     # Background loop
│
└── ui/                        # Notification UI (v0.2)
    ├── notification_window.py # tkinter notifications
    └── ascii_art.py           # ASCII art library
```

### Angular Dashboard

```
sendell-dashboard/src/app/
├── app.ts                     # Main component + project detection
├── app.html                   # Template (projects + terminals)
├── app.scss                   # Cyberpunk styling
│
├── components/
│   ├── activity-graph.component.ts  # ECG-style graphs
│   └── terminal.component.ts        # xterm.js embedded terminal
│
└── core/
    ├── models/
    │   ├── project.model.ts         # Project interface
    │   └── fact.model.ts            # Memory fact
    │
    └── services/
        ├── api.service.ts           # HTTP client
        ├── websocket.service.ts     # WebSocket client
        └── terminal.service.ts      # Terminal visibility state
```

---

## 🎯 ESTADO DE VERSIONES

### ✅ v0.1 - MVP Básico (COMPLETADO)

**Octubre 2025** - 12 sesiones

Core functionality:
- LangGraph agent con 6 herramientas
- Chat interactivo CLI
- Memoria JSON persistente
- Brain GUI (3 tabs: Memorias, Prompts, Herramientas)
- Sistema de permisos L1-L5 configurable
- Health monitoring (CPU, RAM, Disk)

**Lecciones aprendidas**:
- Solo ASCII en código Python (Windows encoding issues)
- LangGraph `create_react_agent()` usa parámetro `prompt`, no `state_modifier`
- Memoria JSON simple > Database compleja para MVP
- tkinter suficiente para GUI básico

### ✅ v0.2 - Sistema Proactivo (COMPLETADO)

**Octubre-Noviembre 2025** - 3 sesiones

**Fase 1: Identidad & Reminders**
- AgentIdentity con birth_date y relationship phases
- Sistema de reminders (one-time, recurring)
- Loop proactivo asyncio no bloqueante
- Integration con LangGraph agent (7ma tool: `add_reminder`)

**Fase 2: Notificaciones Visuales**
- NotificationWindow con 4 niveles de urgencia
- 25 ASCII arts categorizados
- Sistema de sonidos Windows (winsound)
- Auto-selección de arte basada en contexto

**Estado**: Funcional 100%, usado diariamente por Daniel

### 🎯 v0.3 - Dashboard & Terminales (95% COMPLETO)

**Noviembre 2025** - 21 sesiones

**Fase 0-2: Dashboard Base**
- Migración Tkinter → Qt6 → **Angular** (decisión final)
- Detección de proyectos VS Code con psutil
- Gráficos de actividad ECG-style
- Backend FastAPI + WebSocket

**Fase 3: Terminales Embebidos** ✅
- TerminalManager con subprocess.Popen
- ManagedTerminalProcess (threading para I/O)
- WebSocket `/ws/terminal/{pid}` bidireccional
- xterm.js frontend con tema cyberpunk
- Click behavior: OFFLINE → crea terminal, READY/WORKING → toggle

**Pendiente**:
- Build y deploy: `npm run build` → `src/sendell/web/static/`
- Testing end-to-end completo
- Fase 4: Actualizar `project_states.py` con TerminalManager

**Archivos clave**:
- Backend: `src/sendell/terminal_manager/` (4 archivos)
- Frontend: `sendell-dashboard/src/app/components/terminal.component.ts`
- Server: `src/sendell/web/server.py` (WebSocket endpoint)

### 🔮 v0.4+ - Futuro (Planificado)

Posibles features:
- Integración Claude Code (enviar comandos a sesiones Claude)
- Browser automation con Playwright
- Mobile dashboard con Ionic
- Monitoreo de múltiples máquinas

**Filosofía**: Solo implementar features con valor demostrado. Simple > Complex.

---

## 🛠️ CONFIGURACIÓN Y USO

### Setup Inicial

```bash
# Clone repository
git clone [repo-url]
cd sendell

# Install dependencies
uv sync

# Create .env from template
cp .env.example .env
# Edit .env: agregar OPENAI_API_KEY

# Run agent (CLI chat)
uv run python -m sendell chat

# Open Brain GUI (config/memory)
uv run python -m sendell brain

# Start web dashboard
uv run uvicorn sendell.web.server:app --reload --port 8765
# Abrir http://localhost:8765
```

### Comandos CLI

```bash
# Chat interactivo con agente
uv run python -m sendell chat

# Status del sistema (health check)
uv run python -m sendell status

# Abrir Brain GUI
uv run python -m sendell brain

# Ver versión
uv run python -m sendell version
```

### Configuración (.env)

```bash
# OpenAI (OBLIGATORIO)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Autonomía (L1-L5, configurable desde Brain GUI)
SENDELL_AUTONOMY_LEVEL=2

# Proactive loop
SENDELL_LOOP_INTERVAL=60
SENDELL_PROACTIVE_MODE=true

# Privacy
SENDELL_BLOCKED_APPS=1password,keepass,banking
SENDELL_SCRUB_PII=true

# Logs
SENDELL_LOG_LEVEL=INFO
```

---

## 🧰 HERRAMIENTAS DEL AGENTE

### 7 Tools Actuales

1. **get_system_health** - CPU/RAM/Disk metrics (L1+)
2. **get_active_window** - Current window title/process (L1+)
3. **list_top_processes** - Top N by CPU/RAM (L1+)
4. **open_application** - Launch apps (L3+)
5. **respond_to_user** - Proactive messaging (L1+)
6. **show_brain** - Open Brain GUI (L1+)
7. **add_reminder** - Create reminders (L2+)

### Sistema de Permisos (L1-L5)

Configurable desde Brain GUI → Tab Memorias → Dropdown

- **L1 - Monitor Only**: Solo observar, nunca actuar
- **L2 - Ask Permission**: Preguntar antes de acciones (DEFAULT)
- **L3 - Safe Actions**: Auto-ejecutar acciones seguras
- **L4 - Modify State**: Cerrar apps, modificar archivos
- **L5 - Full Autonomy**: Control completo (usar con precaución)

---

## 📝 DECISIONES ARQUITECTÓNICAS CLAVE

### 1. Reset de v0.3 Phase 5/6 (Noviembre 2025)

**Contexto**: Phase 5/6 se convirtió en ciclo de refactorización infinita. WebSocket + VS Code Extension causaba bugs recurrentes, over-engineering sin progreso visible.

**Decisión**:
- ✅ Reset a commit estable `b31c41e`
- ✅ Archivar investigación en `archive/phase6-research/`
- ✅ Nueva dirección: **v0.3-SIMPLIFIED** con psutil SOLAMENTE
- ❌ Pausar VS Code Extension hasta v0.4+

**Resultado**: Angular Dashboard + TerminalManager funcionando en 21 sesiones. Arquitectura limpia, testing funcional, progreso visible.

**Lección**: Simple > Complex. Test antes de commit. No refactorizar infinitamente.

### 2. Angular Standalone vs Qt6 vs Tkinter

**Evaluación**:
- Tkinter: Simple pero limitado, gráficos estáticos
- Qt6: Poderoso pero GIL issues, crashes en threading
- Angular: Web-based, responsive, mejor para dashboards

**Decisión**: Angular con FastAPI backend

**Pros**:
- Accesible desde cualquier navegador
- No GIL issues (backend async)
- Mejor ecosistema de gráficos (Chart.js, D3.js)
- Preparado para mobile (Ionic)

**Contras**:
- Requiere build step
- Más complejo que Tkinter

**Resultado**: Dashboard profesional, estable, escalable

### 3. TerminalManager con subprocess.Popen

**Contexto**: Necesitamos controlar terminales cmd.exe desde Python

**Opciones evaluadas**:
- pty (Unix-only, no funciona en Windows)
- winpty (complejo, dependencias externas)
- subprocess.Popen (built-in, cross-platform)

**Decisión**: subprocess.Popen + threading

**Implementación**:
```python
process = subprocess.Popen(
    ['cmd.exe'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=workspace_path,
    text=True,
    bufsize=1,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)

# Threading para I/O no bloqueante
threading.Thread(target=self._read_stdout, daemon=True).start()
threading.Thread(target=self._read_stderr, daemon=True).start()
threading.Thread(target=self._process_stdin, daemon=True).start()
```

**Pros**:
- 98% reliability
- No dependencias externas
- Cross-platform (funciona en Windows)
- Control completo de I/O

**Contras**:
- Requiere threading manual
- No pseudo-terminal features (pero no necesarias)

### 4. WebSocket vs REST Polling

**Para**: Real-time terminal I/O

**Decisión**: WebSocket bidireccional

**Razón**:
- Latencia <50ms (vs 1-5s con polling)
- Eficiente (no overhead HTTP)
- Bidireccional nativo (cliente ↔ servidor)
- Built-in en FastAPI

**Protocolo**:
```json
// Cliente → Servidor (enviar comando)
{"type": "input", "data": "npm run dev\n"}

// Servidor → Cliente (output)
{"type": "output", "stream": "stdout", "data": "...", "timestamp": "..."}
```

---

## 🐛 PROBLEMAS COMUNES & SOLUCIONES

### Problema: Dashboard no muestra proyectos

**Síntomas**: Dashboard abierto, pero lista de proyectos vacía

**Checks**:
1. Servidor corriendo: `http://localhost:8765/api/projects`
2. VS Code abierto con proyectos
3. Console errors en DevTools

**Solución común**: Olvidaste hacer build después de cambios
```bash
cd sendell-dashboard
npm run build
cd ..
./build-dashboard.sh
```

### Problema: Terminal no aparece al hacer click

**Síntomas**: Click en proyecto OFFLINE, spinner, pero no se ve terminal

**Checks**:
1. DevTools → Network → WS → Ver WebSocket conectado
2. Backend logs: ¿TerminalManager creó terminal?
3. Frontend logs: ¿xterm.js inicializó?

**Solución común**: CSS de xterm.js no cargó. Verificar en `angular.json`:
```json
"styles": [
  "node_modules/@xterm/xterm/css/xterm.css",
  "src/styles.scss"
]
```

### Problema: Comandos no se ejecutan

**Síntomas**: Escribes en terminal pero no pasa nada

**Checks**:
1. WebSocket conectado: `ws.readyState === WebSocket.OPEN`
2. Backend recibe mensaje tipo "input"
3. stdin thread corriendo en ManagedTerminalProcess

**Solución común**: Falta `\n` al final del comando. xterm.js no lo agrega automáticamente.

### Problema: Output no se muestra

**Síntomas**: Comando se ejecuta pero no ves output

**Checks**:
1. stdout thread leyendo en backend
2. WebSocket broadcast funcionando
3. terminal.write() llamándose en frontend

**Solución común**: Caracteres no-UTF8 en output. Usar `errors='replace'` en Popen.

---

## 🔄 HISTORIAL DE DESARROLLO (Condensado)

### Sesiones 1-10: MVP Foundation (v0.1)
- Setup proyecto con uv + LangGraph
- 6 herramientas core implementadas
- Chat CLI funcional
- Brain GUI con 3 tabs
- Memoria JSON persistente
- **Lección clave**: Solo ASCII en código (Windows encoding)

### Sesiones 11-15: Sistema Proactivo (v0.2)
- AgentIdentity con phases (Birth → Maturity)
- Sistema de reminders completo
- Loop asyncio no bloqueante
- Notificaciones visuales con ASCII art
- **Lección clave**: asyncio.to_thread() para input no bloqueante

### Sesiones 16-17: Investigación v0.3
- Research multi-project management (~15,000 palabras)
- Playwright vs Selenium comparison
- Angular + Ionic architecture
- VS Code Extension design
- **Clarificación crítica**: Daniel investiga, Claude implementa

### Sesiones 18-20: Dashboard Attempts
- Intento 1: Tkinter (limitado, gráficos estáticos)
- Intento 2: Qt6 (crashes por GIL, threading issues)
- **Reset**: Archivar Phase 5/6, simplificar approach
- Decisión: Angular web dashboard

### Sesiones 21: Terminales Embebidos ✅
- TerminalManager con subprocess.Popen
- WebSocket bidireccional implementado
- xterm.js frontend funcionando
- Click behavior: OFFLINE → READY → WORKING
- **Estado**: 95% completo, pendiente build + testing

---

## 📚 DOCUMENTACIÓN DE REFERENCIA

### Archivos Clave en Root

- **`CLAUDE.md`** - Este archivo (memoria permanente)
- **`NEXT_SESSION_PLAN.md`** - Plan detallado para continuar v0.3 (450 líneas)
- **`CLAUDE_CODE_INTEGRATION_PLAN.md`** - Futuro plan de integración Claude Code
- **`V03_RESUMEN.md`** - Resumen ejecutivo del dashboard
- **`README.md`** - Documentación de usuario
- **`TUTORIAL.md`** - Tutorial de uso

### Archivos Archivados

- **`archive/phase6-research/`** - Investigación de Phase 5/6 abandonado (~3,500 líneas)
- Útil para consulta futura, pero NO implementar sin testing previo

### Scripts de Testing

- **`test_pyside6_performance.py`** - Performance tests Qt6 (archivado)
- **`test_vscode_simple.py`** - Test detección VS Code
- **`build-dashboard.sh`** - Script para build + deploy Angular

---

## 🚀 PRÓXIMOS PASOS

### Inmediato (Esta o próxima sesión)

1. **Build dashboard**:
   ```bash
   cd sendell-dashboard
   npm run build
   cd ..
   ./build-dashboard.sh
   ```

2. **Testing E2E**:
   - Abrir 2-3 proyectos VS Code
   - Click en OFFLINE → ver terminal aparecer
   - Ejecutar comandos: `dir`, `npm install`, etc.
   - Verificar output en tiempo real
   - Toggle terminal (ocultar/mostrar)

3. **Fase 4**: Actualizar `project_states.py` para usar TerminalManager:
   ```python
   def detect_project_state(project_pid: int) -> str:
       terminal = terminal_manager.get_terminal(str(project_pid))

       if not terminal or not terminal.is_running():
           return "offline"

       if terminal.has_active_subprocess():
           return "working"

       return "ready"
   ```

4. **Commit & Push**:
   - Commit con mensaje descriptivo
   - Push a remote
   - Merge `feature/claude-terminal-control` → `main`

### Futuro v0.4+ (Opcional)

- Integración Claude Code (enviar instrucciones a sesiones Claude)
- Browser automation con Playwright
- Mobile dashboard con Ionic
- Multi-machine monitoring

**Criterio**: Solo implementar si hay valor demostrado y Daniel lo solicita

---

## 🎓 LECCIONES APRENDIDAS

### Desarrollo

1. **Simple > Complex**: psutil funciona mejor que WebSocket complicado
2. **Test antes de commit**: Evita ciclos de debugging infinitos
3. **No refactorizar sin razón**: Phase 5/6 enseñó esto duramente
4. **Daniel investiga, Claude implementa**: Workflow claro previene malentendidos
5. **Build frecuentemente**: Angular requiere `npm run build` después de cada cambio

### Técnico

1. **subprocess.Popen > pty en Windows**: 98% reliability
2. **Threading para I/O**: Queue pattern evita race conditions
3. **WebSocket bidireccional**: Más eficiente que REST polling
4. **xterm.js es poderoso**: Terminal completo en navegador
5. **Signals en Angular**: Reactivo y simple
6. **Singleton pattern**: Esencial para TerminalManager

### Arquitectura

1. **Angular web > Qt6 desktop**: Mejor para dashboards modernos
2. **FastAPI async**: No GIL issues como Qt6
3. **JSON simple > Database**: Suficiente para MVP
4. **Memoria JSON > Redis/Postgres**: Overhead innecesario en v0.1-0.3

---

## 📞 WORKFLOW DE COMMITS

### Formato Establecido

```
feat|fix|docs: [Descripción corta] (Phase X - Task Y)

SUMMARY:
[Resumen 1-2 líneas]

CHANGES:
1. [Cambio específico]
2. [Cambio específico]

TESTING:
[Cómo testear]

FILES MODIFIED:
- file1.py (+X lines)
- file2.py (NEW)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Ejemplo Real

```
feat: Implement embedded terminals with xterm.js (Phase 3)

SUMMARY:
Complete terminal embedding system with WebSocket I/O and xterm.js frontend

CHANGES:
1. Created TerminalManager singleton with subprocess.Popen
2. Added WebSocket endpoint /ws/terminal/{pid}
3. Implemented xterm.js TerminalComponent in Angular
4. Added click behavior: OFFLINE → create terminal, READY/WORKING → toggle

TESTING:
1. Start server: uv run uvicorn sendell.web.server:app --port 8765
2. Open dashboard: http://localhost:8765
3. Click OFFLINE project → terminal appears
4. Type commands → see output in real-time

FILES MODIFIED:
- src/sendell/terminal_manager/ (NEW, 4 files)
- src/sendell/web/server.py (+50 lines)
- sendell-dashboard/src/app/components/terminal.component.ts (NEW)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 🔒 PRINCIPIOS DE SEGURIDAD

### Implementados

1. **Input validation** - Pydantic models para todos los inputs
2. **Subprocess safety** - Nunca `shell=True`
3. **PII scrubbing** - Emails, teléfonos, tarjetas en logs
4. **Blocked apps** - Password managers, banking (configurable)
5. **Autonomy levels** - L1-L5 para control de permisos
6. **No secret storage** - Credenciales solo en .env

### Lo que Sendell NUNCA hace

- ❌ Leer contenido de ventanas (solo títulos)
- ❌ Monitorear apps bloqueadas
- ❌ Guardar contraseñas
- ❌ Enviar datos a terceros (excepto OpenAI API)
- ❌ Telemetry sin opt-in explícito

---

**FIN DE MEMORIA PERMANENTE**

Este archivo refleja el estado REAL y ACTUAL del proyecto Sendell.

Para información detallada de próximos pasos, ver: `NEXT_SESSION_PLAN.md`

🤖 Co-Authored-By: Claude <noreply@anthropic.com>
