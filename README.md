# Sendell - Orquestador AI para Proyectos de Desarrollo

**Versión**: 0.3.0
**Estado**: Dashboard con Terminales Embebidos (Funcional)
**Desarrollador**: Daniel
**Co-Authored-By**: Claude (Anthropic)

---

## 🎯 ¿Qué es Sendell?

Sendell es un **agente AI autónomo** que monitorea y controla tu entorno de desarrollo Windows. Detecta proyectos VS Code abiertos, muestra su estado en tiempo real (OFFLINE/READY/WORKING) y proporciona terminales embebidos en un dashboard web para ejecutar comandos en cada proyecto.

**Casos de uso:**
- Monitorear múltiples proyectos simultáneamente
- Ejecutar comandos npm/git sin cambiar ventanas
- Ver actividad de proyectos en gráficos ECG-style
- Gestión proactiva con recordatorios y notificaciones

---

## 📋 Estado Actual del Proyecto

### ✅ Completado (v0.1 - v0.3)

#### Core Agent (v0.1)
- [x] Chat interactivo con GPT-4 via LangGraph
- [x] 8 herramientas funcionales (system health, procesos, apps, reminders, dashboard)
- [x] Sistema de memoria JSON persistente
- [x] Niveles de autonomía L1-L5 configurables
- [x] Brain GUI (tkinter) para gestionar memoria/prompts

#### Sistema Proactivo (v0.2)
- [x] AgentIdentity con fases temporales (birth → maturity)
- [x] ReminderManager (one-time, recurring, important)
- [x] Loop proactivo asyncio no bloqueante
- [x] NotificationWindow con ASCII art y sonidos

#### Dashboard & Terminales (v0.3)
- [x] **Angular Dashboard** web (localhost:8765)
- [x] **Detección multi-proyecto** VS Code via psutil
- [x] **Gráficos de actividad** ECG-style (Canvas API)
- [x] **Terminales embebidos** xterm.js con WebSocket bidireccional
- [x] **Estados de proyecto**: OFFLINE (rojo) → READY (azul) → WORKING (verde)
- [x] **TerminalManager** backend (subprocess.Popen + threading)
- [x] **Click behavior**: OFFLINE crea terminal, READY/WORKING toggle visibilidad
- [x] **Performance optimizations**: NgZone.runOutsideAngular, WebGL rendering
- [x] **Auto-reconnection** WebSocket con backoff exponencial
- [x] **Mejoras UX**: Encoding cp850, saltos de línea, filtro duplicados

### ⏸️ Incompleto / En Pausa

- [ ] VS Code Extension (iniciada, en `sendell-vscode-extension/`)
- [ ] PTY backend (investigado, no implementado - subprocess suficiente para casos básicos)
- [ ] Database completa (actualmente solo JSON files)
- [ ] Sub-agentes especializados (arquitectura planificada, no implementada)
- [ ] Integración Claude Code (concepto definido, sin implementar)

---

## 🚀 Inicio Rápido

### 1. Requisitos
- **OS**: Windows 10/11
- **Python**: 3.10+
- **Node.js**: 16+ (para dashboard)
- **API Key**: OpenAI GPT-4

### 2. Instalación

```bash
# Clonar repositorio
cd C:\Users\Daniel\Desktop\Daniel\sendell

# Instalar dependencias Python
uv sync

# Configurar environment
copy .env.example .env
notepad .env  # Agregar OPENAI_API_KEY

# Build Angular dashboard (si no está built)
cd sendell-dashboard
npm install
npm run build
cd ..
bash build-dashboard.sh
```

### 3. Uso Básico

```bash
# Iniciar chat con Sendell
uv run python -m sendell chat

# Dentro del chat, abrir dashboard:
You: open dashboard
```

El dashboard se abre en `http://localhost:8765` y muestra:
- Proyectos VS Code detectados automáticamente
- Estado de cada proyecto (OFFLINE/READY/WORKING)
- Gráficos de actividad en tiempo real
- Terminales embebidos (click en proyecto)

---

## 🎮 Comandos CLI

### `sendell chat` - Chat Interactivo (Principal)
```bash
uv run python -m sendell chat
```

**Ejemplos:**
```
You: how's my system?
Sendell: CPU 25%, RAM 89%, Disk 75%

You: open dashboard
Sendell: [Abre dashboard web en navegador]

You: remind me to commit code in 30 minutes
Sendell: [Crea reminder, notifica en 30 min]

You: show brain
Sendell: [Abre GUI de configuración]
```

### `sendell health` - System Check
```bash
uv run python -m sendell health
```
Output: Tabla con CPU%, RAM%, Disk%

### `sendell brain` - Configuración GUI
```bash
uv run python -m sendell brain
```

Abre GUI tkinter con 3 tabs:
1. **Memorias**: Ver/editar facts, configurar autonomía L1-L5
2. **Prompts**: Editar system prompt de Sendell
3. **Herramientas**: Lista de 8 tools disponibles

### `sendell version`
```bash
uv run python -m sendell version
```

---

## 🧰 Las 8 Herramientas de Sendell

| # | Herramienta | Descripción | Autonomía Requerida |
|---|-------------|-------------|---------------------|
| 1 | `get_system_health` | CPU/RAM/Disk metrics | L1+ |
| 2 | `get_active_window` | Ventana activa actual | L1+ |
| 3 | `list_top_processes` | Top N procesos por CPU/RAM | L1+ |
| 4 | `open_application` | Abrir apps (notepad, chrome, vscode) | L3+ |
| 5 | `respond_to_user` | Enviar mensajes proactivos | L1+ |
| 6 | `show_brain` | Abrir Brain GUI | L1+ |
| 7 | `add_reminder` | Crear reminders (one-time, recurring) | L2+ |
| 8 | `open_dashboard` | Abrir dashboard web multi-proyecto | L1+ |

---

## 📊 Dashboard Web (v0.3)

### Características

**Proyectos Detectados:**
- Escanea procesos `Code.exe` con psutil
- Parsea workspace paths
- Muestra nombre + estado en cards

**Estados de Proyecto:**
- 🔴 **OFFLINE**: VS Code cerrado
- 🔵 **READY**: VS Code abierto, terminal idle
- 🟢 **WORKING**: Comando ejecutándose en terminal

**Gráficos de Actividad:**
- ECG-style animación
- Canvas API rendering
- Actualización en tiempo real vía WebSocket

**Terminales Embebidos:**
- Click en proyecto OFFLINE → Crea terminal nuevo
- Click en proyecto READY/WORKING → Toggle visibilidad
- xterm.js v5.5 con FitAddon, WebLinksAddon, WebglAddon
- WebSocket bidireccional para I/O
- Performance: NgZone.runOutsideAngular (200-300% mejora)
- Encoding cp850 (caracteres españoles correctos)
- Auto-reconnection con backoff exponencial
- Botones: Minimizar (`_`) + Cerrar (`×`)

### Tecnologías Dashboard

**Frontend:**
- Angular 17 (standalone components)
- xterm.js 5.5 (terminal emulation)
- Canvas API (gráficos)
- WebSocket client

**Backend:**
- FastAPI (REST API + WebSocket)
- subprocess.Popen (terminal control - cmd.exe)
- psutil (VS Code detection)
- Threading (I/O non-blocking)

---

## 🔧 Arquitectura del Proyecto

```
sendell/
├── src/sendell/
│   ├── agent/                      # Core LangGraph Agent
│   │   ├── core.py                # SendellAgent (8 tools)
│   │   ├── prompts.py             # System prompts
│   │   ├── memory.py              # JSON persistence
│   │   └── brain_gui.py           # tkinter GUI
│   │
│   ├── proactive/                  # Sistema Proactivo (v0.2)
│   │   ├── identity.py            # AgentIdentity (temporal phases)
│   │   ├── reminders.py           # ReminderManager
│   │   ├── proactive_loop.py      # Background asyncio loop
│   │   └── temporal_clock.py      # Time tracking
│   │
│   ├── ui/                         # Notificaciones (v0.2)
│   │   ├── notification_window.py # tkinter notifications
│   │   └── ascii_art.py           # ASCII art library (25 arts)
│   │
│   ├── web/                        # Dashboard Backend (v0.3)
│   │   ├── server.py              # FastAPI app + WebSocket
│   │   ├── routes.py              # REST endpoints
│   │   ├── websocket.py           # WebSocket manager
│   │   └── background.py          # Background scanner
│   │
│   ├── terminal_manager/           # Terminal Control (v0.3)
│   │   ├── manager.py             # TerminalManager singleton
│   │   ├── process.py             # ManagedTerminalProcess (subprocess)
│   │   └── types.py               # Pydantic models
│   │
│   ├── project_manager/            # VS Code Detection (v0.3)
│   │   ├── vscode_detector.py     # psutil-based detection
│   │   ├── project_states.py      # State machine (OFFLINE/READY/WORKING)
│   │   └── bridge.py              # bridge.json management
│   │
│   ├── device/                     # System Monitoring
│   │   ├── monitor.py             # psutil wrapper
│   │   ├── automation.py          # App launching
│   │   └── platform/
│   │       └── windows.py         # Windows APIs
│   │
│   ├── security/                   # Permisos y Validación
│   │   ├── permissions.py         # Sistema L1-L5
│   │   └── validator.py           # Input validation
│   │
│   └── utils/
│       ├── logger.py              # Logging con PII scrubbing
│       └── errors.py              # Excepciones custom
│
├── sendell-dashboard/              # Angular Frontend (v0.3)
│   ├── src/app/
│   │   ├── app.ts                 # Main component
│   │   ├── app.html               # Template (projects + terminals)
│   │   ├── app.scss               # Cyberpunk styling
│   │   ├── components/
│   │   │   ├── activity-graph.component.ts  # ECG graphs
│   │   │   ├── terminal.component.ts        # xterm.js wrapper
│   │   │   ├── terminal.component.html
│   │   │   └── terminal.component.scss
│   │   └── core/
│   │       ├── models/            # TypeScript interfaces
│   │       └── services/          # API, WebSocket, Terminal
│   │
│   └── dist/                      # Build output
│       └── sendell-dashboard/     # Deployed a src/sendell/web/static/
│
├── data/                           # Data Persistence
│   ├── sendell_memory.json        # Memoria del agente
│   └── .sendell/                  # Runtime data
│       ├── dashboard_server.pid
│       └── bridge.json            # Project states
│
└── docs/                           # Documentación
    ├── CLAUDE.md                  # Memoria permanente del proyecto
    ├── FASE1_TERMINAL_REFACTOR.md # Doc de refactor terminal
    └── research/
        └── angular-terminal-complete-guide.txt  # Investigación
```

---

## 🎨 Sistema de Niveles de Autonomía

Configurable en `sendell brain` → Tab Memorias → Dropdown

| Nivel | Nombre | Comportamiento |
|-------|--------|---------------|
| **L1** | Monitor Only | Solo observa, nunca actúa |
| **L2** | Ask Permission | **DEFAULT** - Pide permiso para TODO |
| **L3** | Safe Actions | Auto-ejecuta acciones seguras (abrir apps) |
| **L4** | Modify State | Puede cerrar apps, modificar archivos |
| **L5** | Full Autonomy | Autonomía completa (⚠️ usar con precaución) |

---

## 🧠 Sistema de Memoria

### Ubicación
`data/sendell_memory.json`

### Estructura
```json
{
  "facts": [
    {
      "fact": "Daniel trabaja en AI",
      "category": "work",
      "confidence": 1.0,
      "source": "conversation",
      "timestamp": "2025-11-14T10:00:00"
    }
  ],
  "preferences": {
    "favorite_apps": ["vscode"],
    "work_hours": "14:00-18:00"
  },
  "identity": {
    "birth_date": "2025-10-28T15:30:00",
    "age_days": 16,
    "phase": "ADOLESCENCE"
  },
  "reminders": [
    {
      "id": "rem_001",
      "content": "Commit code",
      "trigger_time": "2025-11-14T14:30:00",
      "type": "one_time",
      "actions": ["visual_notification", "sound"]
    }
  ],
  "conversations": [...],
  "sessions": [...]
}
```

### Gestión
- **Leer/Editar**: `sendell brain` → Tab Memorias
- **Agregar fact**: Botón "Agregar Fact" en GUI
- **Eliminar**: Seleccionar + botón "Eliminar"

---

## 🔐 Privacidad y Seguridad

### ❌ Lo que Sendell NUNCA hace
- Leer contenido de ventanas (solo títulos)
- Monitorear apps bloqueadas (`SENDELL_BLOCKED_APPS`)
- Guardar contraseñas
- Enviar datos a terceros (excepto OpenAI API)
- Ejecutar comandos destructivos sin permiso (L1-L2)

### ✅ Lo que Sendell SÍ hace
- Scrubbing de PII en logs (emails, teléfonos, tarjetas)
- Validación de inputs con Pydantic
- Ejecución segura (`subprocess` sin `shell=True`)
- Logs de auditoría de todas las acciones
- Respeto a niveles de autonomía configurados

---

## 🐛 Troubleshooting

### Dashboard no muestra proyectos
**Causa**: VS Code no detectado o server no corriendo

**Solución**:
```bash
# Verificar VS Code abierto con proyectos
# Verificar server: http://localhost:8765/api/projects
# Restart server si necesario
```

### Terminal no aparece al hacer click
**Causa**: WebSocket no conecta o CSS no cargó

**Solución**:
```bash
# Hard refresh navegador
Ctrl + Shift + R

# Verificar build actualizado
cd sendell-dashboard
npm run build
cd ..
bash build-dashboard.sh
```

### Caracteres raros en terminal (ñ, á, é)
**Estado**: ✅ **RESUELTO** en v0.3 (encoding cp850)

### "ModuleNotFoundError"
```bash
uv sync --all-extras
```

### "OpenAI API Key invalid"
```bash
# Verificar .env tiene API key correcta
notepad .env
```

---

## 📝 Configuración (.env)

```bash
# OpenAI (OBLIGATORIO)
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview

# Autonomía (configurable desde Brain GUI)
SENDELL_AUTONOMY_LEVEL=2

# Loop proactivo
SENDELL_LOOP_INTERVAL=60
SENDELL_PROACTIVE_MODE=true

# Privacidad
SENDELL_BLOCKED_APPS=1password,keepass,banking
SENDELL_SCRUB_PII=true

# Logs
SENDELL_LOG_LEVEL=INFO
```

---

## 🗺️ Roadmap

### ✅ v0.1 - Core Agent (Completado)
- Chat interactivo con LangGraph + GPT-4
- 6 herramientas básicas
- Brain GUI (tkinter)
- Sistema de memoria JSON
- Niveles de autonomía L1-L5

### ✅ v0.2 - Sistema Proactivo (Completado)
- AgentIdentity con fases temporales
- ReminderManager (one-time, recurring)
- Loop proactivo asyncio
- Notificaciones visuales con ASCII art

### ✅ v0.3 - Dashboard & Terminales (Completado)
- Angular Dashboard web
- Detección multi-proyecto VS Code
- Gráficos de actividad ECG-style
- Terminales embebidos xterm.js
- TerminalManager backend
- Estados OFFLINE/READY/WORKING

### 🔜 v0.4 - Orquestación Agéntica (Próximo)
- [ ] Sub-agentes especializados (GitMonitor, NPM Watcher, etc.)
- [ ] Bridge.json expandido (agents, tasks, timeline)
- [ ] Task queue + progress tracking
- [ ] Database de progreso (JSON files estructurados)
- [ ] Panel de estado de agentes en dashboard

### 🔮 v0.5 - Integración Claude Code (Futuro)
- [ ] API local de Claude Code
- [ ] Protocolo de comunicación agente ↔ agente (JSON)
- [ ] Task assignment automático
- [ ] Progress reporting en tiempo real
- [ ] Timeline de eventos (JSONL append-only)

### 🚀 v1.0 - Producción (Largo Plazo)
- [ ] PTY backend para terminal real (vim, nano, htop support)
- [ ] Database PostgreSQL/SQLite
- [ ] Multi-dispositivo (Windows + macOS + Linux)
- [ ] Servidor MCP completo
- [ ] Sistema de plugins

---

## 📚 Documentación Adicional

- **`CLAUDE.md`**: Memoria permanente del proyecto (actualizada cada sesión)
- **`TUTORIAL.md`**: Tutorial de uso paso a paso
- **`docs/FASE1_TERMINAL_REFACTOR.md`**: Documentación detallada del refactor de terminales (4500+ palabras)
- **`docs/research/angular-terminal-complete-guide.txt`**: Investigación completa sobre integración xterm.js + Angular

---

## 💡 Stack Tecnológico

### Backend
- **Agent Framework**: LangGraph (ReAct pattern)
- **LLM**: OpenAI GPT-4 Turbo
- **API Server**: FastAPI + Uvicorn
- **System Monitoring**: psutil
- **Windows APIs**: pywin32
- **Terminal Control**: subprocess.Popen + threading
- **WebSocket**: FastAPI native WebSocket

### Frontend
- **Framework**: Angular 17 (standalone components)
- **Terminal**: xterm.js 5.5 + addons (Fit, WebLinks, Webgl)
- **Real-time**: WebSocket client
- **Graphics**: Canvas API (ECG graphs)
- **Styling**: SCSS (cyberpunk theme)

### Database
- **Current**: JSON files (`sendell_memory.json`, `bridge.json`)
- **Future**: PostgreSQL/SQLite para producción

### Tools
- **Package Manager**: uv (Python), npm (Angular)
- **GUI**: tkinter (Brain GUI)
- **Notifications**: tkinter + winsound
- **CLI**: Typer + Rich

---

## 🤝 Contribuir

Sendell es un proyecto personal de Daniel. Para sugerencias o reportar bugs:

1. Crear issue en el repositorio
2. Describir problema/feature claramente
3. Incluir logs si es bug (`SENDELL_LOG_LEVEL=DEBUG`)

---

## 📄 Licencia

Proyecto personal de uso privado.
Código generado con asistencia de Claude (Anthropic).

---

## 🙏 Créditos

**Desarrollador**: Daniel
**AI Assistant**: Claude (Anthropic)
**Versión**: 0.3.0
**Última actualización**: Noviembre 2025

---

**🤖 Co-Authored-By: Claude <noreply@anthropic.com>**
