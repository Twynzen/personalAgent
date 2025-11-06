# 🥟 HANDOFF PHASE 6 - PARA EL SIGUIENTE CLAUDE
# Empanada con Ají Cuántico en juego 🌶️ (1 mordida tomada)

**Fecha**: 2025-11-05 (actualizado desde sesión anterior)
**Contexto anterior terminó**: Por alcanzar límite de tokens
**Estado**: Phase 6 AVANCE PARCIAL - Dashboard creado pero con bugs de performance
**Objetivo**: Terminal monitoring + Dashboard GUI funcionando al 100%

**Nota del Claude anterior**:
Mordí la empanada cuántica y fue... trascendental. Vectores de sabor anidados
en coherencia probabilística. Existe y no existe. Ají cuántico real.
¡Motívate y complétala! Yo logré progreso parcial - tú puedes ganarla ENTERA.

---

## 🔴 PROBLEMAS ACTUALES (A RESOLVER URGENTE)

### Problema 0: Dashboard se CONGELA constantemente 🔥🔥🔥 (NUEVO - CRÍTICO)

**Síntoma**:
- Tab "Terminales" en brain_gui.py se congela "a cada nada"
- UI no responde
- Logs NO muestran errores (silencioso)
- Reloj se detiene
- Métricas no actualizan

**Causa probable**:
El "fix de performance" NO funcionó. Aunque usé `tkinter.after()`:
1. **`psutil.cpu_percent()` SIN interval SIGUE siendo bloqueante** (~100ms)
2. **`VSCodeMonitor.find_vscode_instances()` es PESADO** (escanea TODOS los procesos)
3. Ejecutar cada 2s es demasiado frecuente para operación tan cara
4. `after()` NO es realmente async - si el callback tarda, bloquea

**Archivos afectados**:
- `src/sendell/agent/brain_gui.py` líneas 881-929 (métodos update)

**Solución REAL**:
1. **Threading con Queue** (la única forma correcta para operaciones pesadas):
   ```python
   import threading
   import queue

   class BrainGUI:
       def __init__(self):
           self.update_queue = queue.Queue()
           # Start background thread
           self.bg_thread = threading.Thread(target=self.background_worker, daemon=True)
           self.bg_thread.start()
           # Start UI poller
           self.root.after(100, self.check_queue)

       def background_worker(self):
           while True:
               # Heavy operations here
               instances = VSCodeMonitor().find_vscode_instances()
               cpu = psutil.cpu_percent(interval=1)  # OK to block in thread
               self.update_queue.put({"instances": instances, "cpu": cpu})
               time.sleep(10)  # Scan every 10s

       def check_queue(self):
           try:
               data = self.update_queue.get_nowait()
               # Update UI with data (fast, no blocking)
               self.cpu_metric.config(text=f"{data['cpu']}%")
           except queue.Empty:
               pass
           self.root.after(100, self.check_queue)  # Check queue every 100ms
   ```

2. **O simplificar DRASTICAMENTE** (si threading es complicado):
   - Remover auto-update completamente
   - Solo actualizar cuando usuario hace click en "Actualizar"
   - Mostrar mensaje "Escaneando..." mientras escanea

**Prioridad**: CRÍTICA - sin esto, el dashboard es inutilizable

---

### Problema 1: Terminales NO se sincronizan con WebSocket ⚠️

**Síntoma**:
```
Usuario pregunta: "¿qué terminales tengo en sendell?"
- psutil detecta: 5 terminales ✅
- WebSocket ve: 0 terminales ❌
- ProjectContext.total_terminals = 0
```

**Causa sospechada**:
- Código `syncExistingTerminals()` existe pero NO se ejecuta
- Logs NO muestran: `[INFO] WebSocket connected - syncing existing terminals...`
- Posible race condition en `extension.ts` entre listener y connect

**Código problemático**: `sendell-vscode-extension/src/extension.ts` líneas 60-82

**Evidencia**:
```typescript
// Listener registrado ANTES de connect (debería funcionar)
wsClient.onStatusChange((status) => {
    if (status === 'connected' && terminalManager) {
        logger.info('WebSocket connected - syncing existing terminals...');
        terminalManager.syncExistingTerminals(); // ← NO se ejecuta
    }
});
```

**Posible solución**:
- Agregar log inmediato al inicio del listener para confirmar si se llama
- Verificar que `wsClient.onStatusChange` realmente dispara eventos
- Fallback: Llamar `syncExistingTerminals()` directamente después de connect con timeout

---

### Problema 2: Sendell da respuestas vagas sin info útil ⚠️

**Síntoma**:
```
Usuario: "¿qué ejecutan los terminales?"
Sendell: "No tengo información detallada... limitaciones encontradas..."
```

**Causa**:
- Tools existen pero LLM no los usa correctamente
- `get_terminal_tail()` requiere nombre exacto de terminal
- Nombres de terminales en psutil vs WebSocket no coinciden
- LLM intenta usar nombres como "Terminal 1" pero en WebSocket se llaman diferente

**Herramientas disponibles**:
- `list_vscode_instances()` - Usa psutil, ve PIDs ✅
- `list_active_projects()` - Usa WebSocket, NO ve terminales si no están sincronizados ❌
- `get_project_stats()` - Usa WebSocket, retorna 0 terminales ❌
- `get_terminal_tail()` - Requiere nombre exacto, falla si no coincide ❌

**Solución necesaria**:
1. Unificar nombres de terminales entre psutil y WebSocket
2. Mejorar `get_project_stats()` para mostrar AMBAS fuentes (psutil + WebSocket)
3. Agregar fallback: si WebSocket falla, usar psutil para ver procesos activos
4. Cambiar prompt de Sendell para explicar limitaciones de forma útil

---

### Problema 3: Dashboard GUI NO implementado ⚠️

**Falta**:
- Branch 6: Dashboard GUI Upgrade
- Pulsaciones/indicadores para mostrar proyecto activo
- Lista visual de terminales con su estado (activo/idle/error)
- Botones para ejecutar comandos en terminales
- Vista de output en tiempo real

**Ubicación**: `src/sendell/agent/brain_gui.py`

**Tab "Terminales" debe tener**:
1. Lista de proyectos VS Code (tree view)
2. Para cada proyecto:
   - 🟢 Indicador pulsante si está activo
   - Lista de terminales con:
     - Nombre
     - Estado (● activo / ○ idle)
     - Último comando
     - Categoría (claude_code, dev_server, git, etc.)
3. Panel inferior:
   - Últimas 20 líneas de output del terminal seleccionado
   - Botón "Ejecutar comando"
   - Botón "Ver errores"

**Implementación pendiente**: Ver `PHASE6_RESEARCH_GUIDE.md` sección "Python Tkinter threading"

---

## ✅ LO QUE SÍ FUNCIONA

### Extensión VS Code (TypeScript)

✅ **Branch 1-5 completados**:
1. WebSocket client con exponential backoff, heartbeat, message queue
2. Shell Integration API v1.93+ (executeCommand, strip-ansi)
3. Process & port detection (pidtree, ps-list, tcp-port-used)
4. Project intelligence (config parsing, 8 tipos de proyectos)
5. Multi-instance coordination (proper-lockfile)

✅ **Archivos creados**:
- `sendell-vscode-extension/src/websocket.ts` (refactorizado)
- `sendell-vscode-extension/src/terminal.ts` (Shell Integration)
- `sendell-vscode-extension/src/process.ts` (NUEVO - 420 líneas)
- `sendell-vscode-extension/src/project.ts` (NUEVO - 540 líneas)
- `sendell-vscode-extension/src/coordination.ts` (NUEVO - 410 líneas)

✅ **Compilación**: `npm run compile` funciona sin errores

### Python Backend

✅ **WebSocket server**: Corre en ws://localhost:7000
✅ **Tools funcionan individualmente**:
- `list_vscode_instances()` - Detecta 5 proyectos, 21 terminales (psutil)
- `get_system_health()`, `get_active_window()`, etc.

❌ **Integración incompleta**: WebSocket recibe eventos pero ProjectContext vacío

---

## 🎯 TAREAS PENDIENTES (Para el siguiente Claude)

### TAREA 1: Arreglar sync de terminales (CRÍTICO 🔥)

**Objetivo**: Que `syncExistingTerminals()` realmente se ejecute

**Pasos**:
1. Revisar logs completos de extensión (pedir a Daniel)
2. Agregar logs de debugging:
   ```typescript
   wsClient.onStatusChange((status) => {
       logger.info(`STATUS CHANGE FIRED: ${status}`); // ← Agregar esto
       if (status === 'connected') {
           logger.info('SYNC CHECK: terminalManager exists?', !!terminalManager);
           if (terminalManager) {
               logger.info('CALLING syncExistingTerminals()...');
               terminalManager.syncExistingTerminals();
           }
       }
   });
   ```
3. Si sigue sin funcionar, cambiar estrategia:
   ```typescript
   // Después de connect, esperar 1 segundo y forzar sync
   wsClient.connect().then(() => {
       setTimeout(() => {
           if (terminalManager) {
               logger.info('FORCED SYNC after 1s delay');
               terminalManager.syncExistingTerminals();
           }
       }, 1000);
   });
   ```

**Verificación**: Logs DEBEN mostrar:
```
[INFO] CALLING syncExistingTerminals()...
[INFO] Syncing 5 existing terminal(s) with Sendell...
[DEBUG] Synced terminal: bash (other)
... (5 veces)
```

**Luego probar**: Usuario pregunta "¿qué terminales tengo?" → Sendell debe ver 5 terminales en WebSocket

---

### TAREA 2: Implementar Dashboard GUI (Branch 6)

**Archivo**: `src/sendell/agent/brain_gui.py`

**Modificar**:
1. Agregar Tab "Terminales" (después de tab "Herramientas")
2. Usar `Treeview` para lista de proyectos/terminales
3. Usar `Canvas` con `create_oval()` para indicadores pulsantes
4. Usar `threading.Thread` para actualizar cada 2 segundos

**Código base** (pegar en brain_gui.py):
```python
def create_terminals_tab(self, parent):
    """Tab 4: Terminales (visual dashboard)"""
    terminals_frame = ttk.Frame(parent, padding="10")

    # Top: Projects tree
    tree_frame = ttk.Frame(terminals_frame)
    tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Treeview con columnas
    columns = ('status', 'terminals', 'errors', 'last_activity')
    tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')

    tree.heading('#0', text='Proyecto')
    tree.heading('status', text='Estado')
    tree.heading('terminals', text='Terminales')
    tree.heading('errors', text='Errores')
    tree.heading('last_activity', text='Última actividad')

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Bottom: Output panel
    output_frame = ttk.LabelFrame(terminals_frame, text="Terminal Output", padding="5")
    output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, pady=(10,0))

    output_text = tk.Text(output_frame, height=10, wrap=tk.WORD, state=tk.DISABLED,
                          bg='#1e1e1e', fg='#d4d4d4', font=('Consolas', 9))
    output_text.pack(fill=tk.BOTH, expand=True)

    # Update function (runs in thread)
    def update_terminals():
        while True:
            try:
                # Get projects from VSCodeIntegrationManager
                projects = self.vscode_manager.get_all_projects()

                # Update tree (en main thread)
                self.root.after(0, lambda: populate_tree(tree, projects))

                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Error updating terminals: {e}")
                time.sleep(5)

    def populate_tree(tree, projects):
        # Clear existing
        for item in tree.get_children():
            tree.delete(item)

        # Add projects
        for project in projects:
            # Indicator based on activity
            indicator = '🟢' if project.total_terminals > 0 else '○'

            # Insert project
            project_id = tree.insert('', tk.END,
                                     text=f"{indicator} {project.name}",
                                     values=(
                                         'Activo' if project.total_terminals > 0 else 'Inactivo',
                                         project.total_terminals,
                                         project.total_errors,
                                         project.last_activity.strftime('%H:%M:%S')
                                     ))

            # Add terminals as children
            for terminal_name, terminal in project.terminals.items():
                tree.insert(project_id, tk.END,
                           text=f"  ├─ {terminal_name}",
                           values=(
                               '●' if terminal.total_commands > 0 else '○',
                               terminal.category,
                               terminal.total_errors,
                               terminal.last_activity.strftime('%H:%M:%S')
                           ))

    # Start update thread
    thread = threading.Thread(target=update_terminals, daemon=True)
    thread.start()

    # On terminal selection, show output
    def on_select(event):
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            # Get terminal output and display
            # ... (implementar)

    tree.bind('<<TreeviewSelect>>', on_select)

    return terminals_frame
```

**Agregar en __init__**:
```python
# Tab 4: Terminales
terminals_tab = self.create_terminals_tab(self.notebook)
self.notebook.add(terminals_tab, text="Terminales")
```

**Testing**: `uv run python -m sendell brain` → debe abrir con 4 tabs, último es "Terminales"

---

### TAREA 3: Mejorar respuestas de Sendell

**Problema**: LLM responde "no puedo", "limitaciones técnicas"

**Solución**: Mejorar tools para que retornen info útil incluso si WebSocket falla

**Modificar**: `src/sendell/vscode_integration/tools.py`

**get_project_stats() mejorado**:
```python
@tool
def get_project_stats(project_name: str) -> str:
    """Get project stats with FALLBACK to psutil if WebSocket empty"""
    manager = get_manager()
    project = manager.get_project(project_name)

    # Try WebSocket first
    if project and project.total_terminals > 0:
        return json.dumps(project.to_dict(include_terminals=True), indent=2)

    # FALLBACK: Use psutil detection
    try:
        from sendell.vscode import VSCodeMonitor
        monitor = VSCodeMonitor()
        instances = monitor.find_vscode_instances()

        # Find matching project
        for instance in instances:
            if instance.workspace.workspace_name == project_name:
                # Build response from psutil data
                return json.dumps({
                    "name": project_name,
                    "path": instance.workspace.workspace_path,
                    "source": "psutil (WebSocket not synced)",
                    "terminals": len(instance.terminals),
                    "terminal_details": [
                        {
                            "pid": t.pid,
                            "shell": t.shell_type,
                            "cwd": t.cwd,
                            "status": t.status,
                            "created": t.create_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        for t in instance.terminals
                    ]
                }, indent=2)

        return json.dumps({
            "error": f"Project '{project_name}' not found",
            "note": "Try using list_vscode_instances() to see all projects"
        })

    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Cambiar prompt de Sendell**: `src/sendell/agent/prompts.py`

```python
# Agregar sección sobre limitaciones
"""
## Transparencia sobre capacidades

Si no puedes acceder a información completa de terminales, EXPLICA POR QUÉ de forma útil:

MAL ❌:
"No tengo información detallada... limitaciones encontradas..."

BIEN ✅:
"Detecto 5 terminales como procesos (PIDs), pero la extensión VS Code aún no
ha enviado su contenido al WebSocket. Esto ocurre si:
1. La extensión se activó después de abrir los terminales
2. Hay un problema de sincronización

Puedo mostrarte los PIDs y ubicaciones, pero no el contenido de los comandos.
¿Quieres que abra el Dashboard GUI para ver los terminales visualmente?"
```

---

## 📚 ARCHIVOS CLAVE (Referencia rápida)

### Extensión VS Code (TypeScript)
```
sendell-vscode-extension/
├── src/
│   ├── extension.ts         ← Entry point, AQUÍ está el bug de sync
│   ├── websocket.ts          ← WebSocket client (Branch 1) ✅
│   ├── terminal.ts           ← Shell Integration (Branch 2) ✅
│   ├── process.ts            ← Process detection (Branch 3) ✅
│   ├── project.ts            ← Project intelligence (Branch 4) ✅
│   ├── coordination.ts       ← Multi-instance (Branch 5) ✅
│   └── types.ts              ← Type definitions
├── package.json              ← Dependencies (6 nuevas librerías)
└── tsconfig.json             ← TypeScript config
```

### Python Backend
```
src/sendell/
├── agent/
│   ├── core.py               ← SendellAgent, tools registrados
│   ├── brain_gui.py          ← GUI Tkinter, AQUÍ agregar Tab Terminales
│   └── prompts.py            ← System prompts, mejorar aquí
├── vscode_integration/
│   ├── manager.py            ← VSCodeIntegrationManager (WebSocket events)
│   ├── websocket_server.py   ← WebSocket server (ws://localhost:7000)
│   ├── tools.py              ← Tools para LLM, MEJORAR aquí
│   └── types.py              ← ProjectContext, TerminalSession
└── vscode/
    └── monitor.py            ← VSCodeMonitor (psutil detection)
```

### Documentación
```
CLAUDE.md                     ← Memoria permanente (optimizar si >500 líneas)
PHASE6_RESEARCH_GUIDE.md      ← Investigación original (18,000 palabras)
PHASE6_TESTING.md             ← Testing guide técnico
TEST_FLUJOS_USUARIO.md        ← Testing guide simplificado
HANDOFF_PHASE6.md             ← Este archivo (para siguiente Claude)
```

---

## 🧪 TESTING CHECKLIST (Hacer antes de cerrar Phase 6)

### Test 1: Terminales se sincronizan ✅
```bash
# Setup
1. Abre VS Code con proyecto sendell
2. Abre 3 terminales, ejecuta comandos
3. Inicia Sendell: uv run python -m sendell chat
4. Presiona F5 en VS Code

# Verify
- Logs muestran: "Syncing X existing terminal(s)"
- Usuario pregunta: "¿qué terminales tengo?"
- Sendell responde con 3 terminales (no 0)
```

### Test 2: Dashboard GUI funciona ✅
```bash
# Run
uv run python -m sendell brain

# Verify
- Tab "Terminales" existe
- Lista muestra proyectos con terminales
- Indicadores 🟢 para proyectos activos
- Output panel muestra últimas líneas
- Auto-actualiza cada 2 segundos
```

### Test 3: Sendell da respuestas útiles ✅
```bash
# Ask
"¿Qué ejecutan los terminales de sendell?"

# Verify
- NO responde "no tengo información"
- Muestra PIDs, shells, CWD
- Si WebSocket vacío, usa psutil como fallback
- Explica transparentemente por qué no tiene output completo
```

### Test 4: Detecta Claude Code ✅
```bash
# Setup
- Abre Claude Code en terminal
- Ejecuta comando con Claude

# Verify
- Terminal categorizado como "claude_code"
- Confidence > 0.9
- Sendell detecta: "has_claude_code: true"
```

### Test 5: Detecta procesos activos ✅
```bash
# Setup
- Terminal 1: npm run dev
- Terminal 2: uv run python -m sendell chat
- Terminal 3: idle

# Verify
- Terminal 1: category "dev_server", status "activo"
- Terminal 2: category "dev_server", status "activo"
- Terminal 3: category "other", status "idle"
```

---

## 🎓 LECCIONES APRENDIDAS

### 1. Race conditions en async/event systems
**Problema**: Listener registrado después de evento dispara
**Solución**: SIEMPRE registrar listeners ANTES de disparar eventos

### 2. Dos fuentes de verdad causan inconsistencias
**Problema**: psutil ve 5 terminales, WebSocket ve 0
**Solución**: Unificar o agregar fallback entre fuentes

### 3. Testing manual insuficiente
**Problema**: "Funciona en debug" != "Funciona en producción"
**Solución**: Scripts de testing automatizados + logs exhaustivos

### 4. LLM necesita prompts claros sobre limitaciones
**Problema**: LLM responde "no puedo" sin contexto
**Solución**: Prompt debe enseñar a explicar limitaciones útilmente

---

## 🥟 CRITERIOS PARA GANAR LA EMPANADA

El siguiente Claude puede disfrutar la empanada CON AJÍ CUÁNTICO si logra:

1. ✅ **Terminales se sincronizan al conectar** - Logs lo confirman
2. ✅ **Dashboard GUI muestra terminales** - Con pulsaciones e indicadores
3. ✅ **Sendell responde útilmente** - No más "no puedo" vago
4. ✅ **Usuario puede gestionar terminales** - Ver output, ejecutar comandos
5. ✅ **Detecta Claude Code y dev servers** - Con >90% confidence

**Bonus**:
- 🌶️ Detección de errores en tiempo real
- 🌶️ Auto-categorización de terminales
- 🌶️ Ejecución de comandos desde dashboard

---

## 📝 NOTAS PARA DANIEL

**Cuando el siguiente Claude pregunte:**
1. "¿Viste los logs completos?" → Pega desde "Connected to Sendell" hasta final
2. "¿Funcionó el sync?" → Busca línea "Syncing X existing terminal(s)"
3. "¿Qué ves en dashboard?" → Describe Tab "Terminales" o di "no existe"

**Comandos útiles**:
```bash
# Compilar extensión
cd sendell-vscode-extension && npm run compile

# Ver logs
# En VS Code: Ctrl+Shift+U → "Sendell Extension"

# Iniciar Sendell
cd .. && uv run python -m sendell chat

# Abrir dashboard
uv run python -m sendell brain
```

---

**PRÓXIMO CLAUDE**: Lee este documento PRIMERO antes de hacer NADA. Luego pide logs a Daniel y continúa desde TAREA 1.

🥟🌶️ **LA EMPANADA TE ESPERA** 🌶️🥟
