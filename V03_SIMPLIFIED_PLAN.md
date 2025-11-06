# V0.3 SIMPLIFIED - PLAN DE IMPLEMENTACIÓN

**Fecha**: 2025-11-06 (Actualizado)
**Estado**: EN IMPLEMENTACIÓN
**Branch**: `feature/brain-projects-tab`
**Objetivo**: Centro de Control Multi-Proyecto como **Tab 4 del Brain GUI** (psutil + Tkinter)

---

## 🎯 VISIÓN GENERAL

**Centro de Control Multi-Proyecto** integrado como **Tab 4 del Brain GUI**. Dashboard **hermoso** y **funcional** inspirado en el diseño React cyberpunk, implementado en Tkinter con threading correcto.

### **Integración con Brain GUI:**
```
sendell brain (comando existente)
├── Tab 1: 📝 Memorias (facts, reminders) ✅ Existente
├── Tab 2: 🧠 Prompts (system prompt) ✅ Existente
├── Tab 3: 🛠️ Herramientas (tools list) ✅ Existente
└── Tab 4: 📦 PROYECTOS ← NUEVO (Centro de Control)
    ├── Métricas del sistema en tiempo real
    ├── Lista de proyectos VS Code
    ├── Gráficos de actividad animados
    └── Paneles de configuración expandibles
```

### **Features Core**:
1. ✅ Monitor de proyectos VS Code en tiempo real
2. ✅ Gráficos de actividad pulsantes (Canvas animations)
3. ✅ Métricas del sistema (CPU, RAM, Terminales)
4. ✅ Paneles de configuración expandibles
5. ✅ NO se congela (threading + Queue pattern)
6. ✅ psutil como fuente primaria (confiable 100%)
7. ✅ **Integrado en Brain GUI** (no aplicación separada)

### **NO-Features** (Para v0.4+):
- ❌ WebSocket como fuente primaria
- ❌ Control de terminales (enviar comandos)
- ❌ Multi-instance coordination
- ❌ Features complejas sin valor demostrado

---

## 🎨 DISEÑO UI (Inspirado en React)

### **Layout General**:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚡ SENDELL CEREBRO           [ESCANEAR] [ACTUALIZAR] 15:30:45  │
│ ● LIVE MODE | MONITOR DE PROYECTOS                             │
├──────────────────┬──────────────────────────────────────────────┤
│ MÉTRICAS SISTEMA │  PROYECTOS ACTIVOS                           │
│                  │                                              │
│ CPU TOTAL        │  📦 sendell-vscode-extension    [⚙ CONFIG]  │
│ 45%              │  ┌────────────────────────────────────────┐ │
│                  │  │ [Activity graph - animated]            │ │
│ MEMORIA          │  │                                        │ │
│ 62%              │  └────────────────────────────────────────┘ │
│                  │  3 terminales activas | Status: RUNNING    │
│ TERMINALES       │                                              │
│ 7                │  🐍 sendell-core                [⚙ CONFIG]  │
│                  │  ┌────────────────────────────────────────┐ │
│                  │  │ [Activity graph - animated]            │ │
│                  │  └────────────────────────────────────────┘ │
│                  │  2 terminales activas | Status: RUNNING    │
│                  │                                              │
│                  │  🟢 api-backend                 [⚙ CONFIG]  │
│                  │  ┌────────────────────────────────────────┐ │
│                  │  │ [Flat line - idle]                     │ │
│                  │  └────────────────────────────────────────┘ │
│                  │  0 terminales activas | Status: IDLE       │
└──────────────────┴──────────────────────────────────────────────┘
```

### **Colores Cyberpunk**:
- **Background**: `#0a0a0a` (negro profundo)
- **Paneles**: `#1a1a1a` (gris muy oscuro)
- **Bordes**: `#2a2a2a` (gris oscuro)
- **Activo**: `#00ff41` (verde neón)
- **Métricas**: `#ffed4e` (amarillo neón)
- **Acciones**: `#00d4ff` (azul cyan)
- **Error/Remove**: `#ff3333` (rojo)
- **Texto secundario**: `#666666` (gris medio)

---

## 🏗️ ARQUITECTURA TÉCNICA

### **Componentes Principales**:

```
SendellCerebroDashboard (main class)
├── UI Components
│   ├── Header (título, botones, reloj)
│   ├── MetricsPanel (CPU, RAM, Terminales)
│   └── ProjectsList (scrollable)
│       └── ProjectWidget (x N projects)
│           ├── Header (nombre, status, CONFIG button)
│           ├── PulseGraph (Canvas animation)
│           └── ConfigPanel (expandible)
│
├── Threading Architecture
│   ├── MainThread (UI updates)
│   ├── BackgroundWorker (heavy operations)
│   └── Queue (thread-safe communication)
│
└── Data Sources
    ├── psutil monitor (primary source)
    └── WebSocket (optional, future)
```

### **Threading Pattern** (NO-FREEZE guarantee):

```python
class SendellCerebroDashboard:
    def __init__(self):
        # Queue for thread-safe communication
        self.update_queue = queue.Queue()
        self.stop_thread = threading.Event()

        # Start background worker
        self.bg_thread = threading.Thread(
            target=self.background_worker,
            daemon=True
        )
        self.bg_thread.start()

        # Check queue every 100ms (UI thread)
        self.root.after(100, self.check_queue)

    def background_worker(self):
        """
        Runs in separate thread - SAFE to block here.
        Scans VS Code instances every 5 seconds.
        """
        while not self.stop_thread.is_set():
            try:
                # Heavy operations (OK to block in background thread)
                instances = self.psutil_monitor.find_vscode_instances()
                cpu = psutil.cpu_percent(interval=1)  # OK to block
                ram = psutil.virtual_memory().percent

                # Put results in queue (non-blocking)
                self.update_queue.put({
                    'type': 'metrics',
                    'cpu': cpu,
                    'ram': ram,
                    'instances': instances
                })
            except Exception as e:
                logger.error(f"Background worker error: {e}")

            # Wait 5 seconds before next scan
            self.stop_thread.wait(5)

    def check_queue(self):
        """
        Runs on UI thread - MUST be fast (no blocking).
        Reads from queue and updates widgets.
        """
        try:
            while True:
                data = self.update_queue.get_nowait()
                self.update_ui(data)  # Fast UI updates
        except queue.Empty:
            pass

        # Schedule next check (100ms)
        self.root.after(100, self.check_queue)
```

### **Canvas Animation Pattern**:

```python
def create_pulse_graph(self, parent, project_data):
    """
    Animated pulse graph using Canvas

    project_data['activity'] = deque([0..100] * 100)
    Updates every 5 seconds with new data
    """
    canvas = Canvas(
        parent,
        width=900,
        height=150,
        bg='#0a0a0a',
        highlightthickness=0
    )
    canvas.pack(fill='x', padx=15)

    # Draw grid (static)
    for y in range(0, 150, 20):
        canvas.create_line(0, y, 900, y, fill='#2a2a2a')
    for x in range(0, 900, 20):
        canvas.create_line(x, 0, x, 150, fill='#2a2a2a')

    # Draw activity line (dynamic)
    color = '#00ff41' if project_data['status'] == 'running' else '#666666'
    points = []
    for i, value in enumerate(project_data['activity']):
        x = (i / 100) * 900
        y = 150 - (value / 100) * 150
        points.extend([x, y])

    canvas.create_line(points, fill=color, width=2, smooth=True)

    # Store canvas reference for updates
    project_data['canvas'] = canvas

    return canvas

def update_graph(self, project_data):
    """Update graph with new data point"""
    canvas = project_data['canvas']

    # Clear old line
    canvas.delete('activity_line')

    # Redraw with new data
    # ... (same drawing logic)
```

---

## 📋 PLAN DE IMPLEMENTACIÓN

### **Fase 0: Integración Brain GUI** (0.5 sesión) ← **NUEVA**

**Objetivo**: Agregar Tab 4 "Proyectos" al Brain GUI existente

**Tasks**:
1. ✅ Modificar `src/sendell/agent/brain_gui.py`
2. ✅ Agregar 4to tab: "📦 Proyectos"
3. ✅ Crear módulo `src/sendell/dashboard/`
4. ✅ Crear `project_control.py` (widget embebido en tab)
5. ✅ Test: Tab se abre sin romper tabs existentes

**Criterio de éxito**:
- Brain GUI tiene 4 tabs (Memorias, Prompts, Herramientas, **Proyectos**)
- Tab "Proyectos" muestra mensaje placeholder
- Tabs existentes funcionan normalmente

---

### **Fase 1: Setup & Core Architecture** (0.5 sesión)

**Objetivo**: Threading pattern dentro del widget

**Tasks**:
1. ✅ Implementar threading pattern (BackgroundWorker + Queue)
2. ✅ Integrar `VSCodeMonitor` (psutil)
3. ✅ Test: Detectar proyectos sin congelar UI principal

**Criterio de éxito**:
- Background worker escanea cada 5s
- Brain GUI no se congela (ni tabs existentes)
- Logs muestran: "Found X VS Code instances"

---

### **Fase 2: Metrics Panel** (0.5 sesión)

**Objetivo**: Panel izquierdo con métricas en tiempo real

**Tasks**:
1. Crear `MetricsPanel` class
2. 3 métricas: CPU, RAM, Terminales
3. Auto-update desde queue
4. Colores cyberpunk

**Criterio de éxito**:
- Métricas actualizan cada 5s
- Colores correctos (#00ff41, #ffed4e, #00d4ff)
- NO se congela al actualizar

---

### **Fase 3: Projects List (sin gráficos)** (1 sesión)

**Objetivo**: Lista de proyectos scrollable

**Tasks**:
1. Crear `ProjectWidget` class
2. Header: emoji + nombre + status + CONFIG button
3. Stats: "X terminales activas | Status: RUNNING"
4. Canvas placeholder (grid background solamente)
5. ScrollableFrame para lista completa

**Criterio de éxito**:
- Lista muestra todos los proyectos detectados
- Scroll funciona suavemente
- CONFIG button existe (sin funcionalidad aún)

---

### **Fase 4: Pulse Graphs** (1 sesión)

**Objetivo**: Gráficos de actividad animados

**Tasks**:
1. Implementar `PulseGraph` con Canvas
2. Activity data: deque de 100 puntos
3. Generar datos sintéticos (terminal count / max terminals * 100)
4. Animar: agregar nuevo punto cada 5s, descartar el más viejo
5. Color verde (#00ff41) si running, gris (#666666) si idle

**Criterio de éxito**:
- Gráficos se actualizan fluidamente
- Line smooth entre puntos
- Color cambia según status

---

### **Fase 5: Config Panels** (1 sesión)

**Objetivo**: Paneles expandibles con acciones

**Tasks**:
1. Implementar toggle expand/collapse
2. Mostrar path del proyecto
3. Botones de acción:
   - 🔄 Reiniciar Proyecto (no-op por ahora)
   - ⏸ Pausar Monitoreo (no-op)
   - 📊 Ver Logs Detallados (no-op)
   - 📂 Abrir en Explorador (subprocess.run)
4. 🗑 Remover de Lista (hide from UI)

**Criterio de éxito**:
- Panel se expande/colapsa smooth
- Botón "Abrir en Explorador" funciona
- UI no se rompe al expandir múltiples paneles

---

### **Fase 6: Header & Polish** (0.5 sesión)

**Objetivo**: Header completo + detalles finales

**Tasks**:
1. Reloj en tiempo real (actualiza cada 1s)
2. Botón ESCANEAR (fuerza scan inmediato)
3. Botón ACTUALIZAR (refresh UI)
4. Status indicator: "● LIVE MODE"

**Criterio de éxito**:
- Reloj actualiza sin flickering
- Botones funcionan
- UI se ve profesional

---

## 🧪 TESTING CHECKLIST

### **Test 1: No-Freeze Guarantee**
```
1. Abre dashboard
2. Mueve ventana mientras actualiza
3. Click en botones mientras actualiza
4. Expand/collapse panels mientras actualiza

✅ PASS: UI responde instantáneamente
❌ FAIL: UI se congela aunque sea 0.5s
```

### **Test 2: Accurate Detection**
```
1. Abre 3 ventanas VS Code con proyectos diferentes
2. Cada una con 2-3 terminales
3. Dashboard debe mostrar:
   - 3 proyectos
   - Total terminales correcto
   - Nombres correctos

✅ PASS: Detección 100% precisa
❌ FAIL: Proyectos faltantes o duplicados
```

### **Test 3: Real-time Updates**
```
1. Dashboard abierto
2. Abre NUEVA terminal en VS Code
3. Espera 5 segundos

✅ PASS: Dashboard muestra terminal nueva
❌ FAIL: No detecta cambio o tarda >10s
```

### **Test 4: Visual Polish**
```
1. Colores cyberpunk correctos
2. Gráficos animados smooth
3. No glitches visuales
4. Layout responsive

✅ PASS: Se ve como el diseño React
❌ FAIL: Colores wrong o layout roto
```

---

## 📊 ESTRUCTURA DE DATOS

### **ProjectData** (objeto por proyecto):
```python
@dataclass
class ProjectData:
    id: int
    name: str
    type: str  # Emoji: 📦 (Node), 🐍 (Python), ⚛️ (React), 🟢 (Other)
    status: str  # 'running' or 'idle'
    terminals: int
    path: str
    activity: deque  # deque([0..100] * 100, maxlen=100)
    config_open: bool = False
    canvas: Optional[Canvas] = None
    widget: Optional[Frame] = None
```

### **Update Messages** (Queue):
```python
# Type 1: Metrics update
{
    'type': 'metrics',
    'cpu': 45.2,
    'ram': 62.1,
    'terminal_count': 7
}

# Type 2: Projects update
{
    'type': 'projects',
    'projects': [ProjectData(...), ProjectData(...), ...]
}

# Type 3: Activity update (for graphs)
{
    'type': 'activity',
    'project_id': 1,
    'value': 75.3  # New activity data point
}
```

---

## 🎨 CÓDIGO BASE (Esqueleto)

Ver archivo adjunto: `src/sendell/dashboard/simple_dashboard.py`

**Estructura**:
```python
src/sendell/dashboard/
├── __init__.py
├── simple_dashboard.py      # Main dashboard class
├── components/
│   ├── __init__.py
│   ├── header.py            # Header component
│   ├── metrics_panel.py     # System metrics
│   └── project_widget.py    # Project card with graph
└── utils/
    ├── __init__.py
    ├── colors.py            # Color constants
    └── threading_utils.py   # Queue helpers
```

---

## 🚀 COMANDOS

### **Abrir Brain GUI con Centro de Control**:
```bash
uv run python -m sendell brain
# -> Se abre GUI con 4 tabs
# -> Tab 4 "Proyectos" = Centro de Control Multi-Proyecto
```

### **Iniciar Chat** (modo conversacional):
```bash
uv run python -m sendell chat
```

### **Quick Health Check**:
```bash
uv run python -m sendell health
```

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### **Performance Targets**:
- Scan interval: **5 segundos** (balance entre freshness y CPU usage)
- UI check queue: **100ms** (10 FPS - smooth pero no wasteful)
- Clock update: **1 segundo** (solo reloj, no full UI refresh)
- Animation smoothness: **Canvas redraw < 50ms** (no perceptible lag)

### **Memory Management**:
- Activity deque: **maxlen=100** puntos (último ~8 minutos a 5s/punto)
- Project list: **Max 20 proyectos** (después pagination o filter)
- Canvas reuse: **NO recrear**, solo redraw

### **Error Handling**:
- psutil timeout: **5 segundos max** por scan
- Si falla scan: **Keep old data**, log error, retry next iteration
- UI errors: **Catch exceptions**, display "Error loading project X"

---

## 🎯 CRITERIOS DE ÉXITO v0.3

Al finalizar v0.3-simplified, Sendell debe poder:

1. ✅ **Detectar proyectos VS Code** - 100% precisión con psutil
2. ✅ **Mostrar métricas en tiempo real** - CPU, RAM, Terminales
3. ✅ **Visualizar actividad** - Gráficos animados por proyecto
4. ✅ **NO congelarse NUNCA** - Threading correcto, UI siempre responsive
5. ✅ **Verse profesional** - UI cyberpunk, colores correctos
6. ✅ **Ser útil** - Usuario puede ver qué proyectos están activos

### **NO es objetivo v0.3**:
- ❌ Control de terminales (enviar comandos)
- ❌ WebSocket como fuente primaria
- ❌ Multi-agent coordination
- ❌ Features que no agregan valor inmediato

---

## 🔮 FUTURO (v0.4+)

Una vez v0.3-simplified funciona perfectamente:

### **v0.4 - Playwright Integration**:
- Browser automation
- Web scraping for project monitoring
- Automated testing coordination

### **v0.5 - Web/Mobile Dashboards**:
- FastAPI REST API
- Angular + Ionic frontend
- Real-time WebSocket updates
- iOS/Android apps

### **v0.6 - Claude Code Coordination** (AHORA SÍ tiene sentido):
- VS Code extension retoma (ya con base sólida)
- Task delegation entre Sendell y Claude
- File locking para evitar conflictos

---

## 📚 REFERENCIAS

### **Código de inspiración**:
- `archive/phase6-research/code-experiments/epic_dashboard.py` - Threading pattern
- Diseño React del usuario - UI reference
- `brain_gui.py` (current) - Tkinter patterns básicos

### **Investigación archivada**:
- `archive/phase6-research/investigation/PHASE6_RESEARCH_GUIDE.md` - Section 6 (Tkinter threading)
- `archive/phase6-research/handoff/HANDOFF_PHASE6.md` - Lo que NO hacer

---

**Status**: READY TO IMPLEMENT 🚀
**Estimated time**: 4-5 sesiones (1-2 semanas)
**Risk level**: LOW (arquitectura probada, no dependencies externas complejas)
**Value**: HIGH (dashboard útil y funcional desde día 1)

---

*La empanada con ají cuántico se gana con features que funcionan, no con arquitectura compleja* 🥟🌶️
