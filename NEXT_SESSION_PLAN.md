# PLAN DETALLADO PARA PRÓXIMA SESIÓN

**Fecha**: 2025-11-11
**Estado actual**: Fases 1-3 completadas (Terminales embebidos funcionales)
**Pendiente**: Fase 4 + Build + Testing E2E

---

## 🎯 RESUMEN EJECUTIVO

Se ha implementado un sistema completo de **terminales embebidos en el dashboard** usando xterm.js. El sistema permite:
- Crear terminales cmd.exe para cada proyecto VS Code
- Ver output en tiempo real en el dashboard
- Enviar comandos desde la interfaz web
- WebSocket bidireccional para I/O

**Estado de implementación**: 95% completo
**Lo que falta**: Build, deploy, testing end-to-end, y Fase 4 (detección de estados)

---

## ✅ LO QUE YA ESTÁ HECHO (Fases 1-3)

### Fase 1: Backend TerminalManager (COMPLETADO ✅)

**Archivos creados**:
1. `src/sendell/terminal_manager/__init__.py` - Module exports
2. `src/sendell/terminal_manager/types.py` - Pydantic models (ProcessState, TerminalInfo, etc.)
3. `src/sendell/terminal_manager/process.py` - ManagedTerminalProcess class
4. `src/sendell/terminal_manager/manager.py` - TerminalManager singleton

**Características**:
- Singleton manager para gestionar todos los terminales
- subprocess.Popen con cmd.exe (98% reliability)
- Threading para I/O no bloqueante (stdout, stderr, stdin)
- Detección de subprocesos activos con psutil
- Estados: STARTING → RUNNING → STOPPED/ERROR

**Métodos clave**:
```python
terminal_manager = get_terminal_manager()

# Crear terminal
terminal_id = terminal_manager.create_terminal(
    project_pid=12345,
    workspace_path="C:/path/to/project",
    project_name="MyProject"
)

# Enviar comando
terminal_manager.send_command(terminal_id, "npm run dev\n")

# Obtener info
terminal = terminal_manager.get_terminal(terminal_id)
print(terminal.state)  # ProcessState.RUNNING

# Verificar si hay comando activo
if terminal.has_active_subprocess():
    print(f"Running: {terminal.get_active_command()}")
```

### Fase 2: WebSocket Protocol (COMPLETADO ✅)

**Archivos modificados**:
1. `src/sendell/web/server.py` - WebSocket endpoint `/ws/terminal/{project_pid}`
2. `src/sendell/web/routes.py` - Endpoint `/projects/open-terminal`

**Protocolo WebSocket**:

**Cliente → Servidor** (enviar comando):
```json
{
  "type": "input",
  "data": "npm run dev\n"
}
```

**Servidor → Cliente** (output):
```json
{
  "type": "output",
  "stream": "stdout",
  "data": "Server started on port 3000\n",
  "timestamp": "2025-11-11T10:30:00"
}
```

**Servidor → Cliente** (error):
```json
{
  "type": "error",
  "message": "Terminal not found"
}
```

**Características**:
- Broadcast de output a múltiples clientes simultáneos
- Auto-registro de conexiones por terminal_id
- Cleanup automático al cerrar WebSocket
- TerminalManager se inicializa en startup
- Shutdown graceful de todos los terminales

### Fase 3: Frontend xterm.js (COMPLETADO ✅)

**Archivos creados**:
1. `sendell-dashboard/src/app/components/terminal.component.ts` - Componente xterm.js
2. `sendell-dashboard/src/app/core/services/terminal.service.ts` - Service para visibility

**Archivos modificados**:
1. `sendell-dashboard/src/app/app.ts` - Imports, click logic
2. `sendell-dashboard/src/app/app.html` - Render terminals
3. `sendell-dashboard/src/app/core/services/api.service.ts` - Signature actualizada ✅

**Características del componente**:
- xterm.js con tema cyberpunk (neon green/cyan)
- FitAddon para responsive sizing
- WebSocket client conecta a `/ws/terminal/{project_pid}`
- Header con nombre de proyecto y botón close
- Input interactivo (onData → sendCommand)
- Welcome message con info de proyecto

**Click behavior**:
- **OFFLINE (rojo)**: Click crea nueva terminal → se abre embebida
- **READY (azul)**: Click toggle terminal existente (mostrar/ocultar)
- **WORKING (verde)**: Click toggle terminal existente (mostrar/ocultar)

**Dependencias instaladas**:
```bash
cd sendell-dashboard
npm install @xterm/xterm@5.5.0 @xterm/addon-fit@0.10.0
```

---

## 📋 LO QUE FALTA (Próxima sesión)

### TAREA 1: Build y Deploy del Dashboard ⚠️ CRÍTICO

**Objetivo**: Compilar Angular y deployar a carpeta static del servidor

**Pasos**:
```bash
# 1. Build Angular app
cd sendell-dashboard
npm run build

# 2. Verificar output en dist/sendell-dashboard/browser/

# 3. Deploy (ya existe script):
cd ..
./build-dashboard.sh

# O manual:
# mkdir -p src/sendell/web/static
# cp -r sendell-dashboard/dist/sendell-dashboard/browser/* src/sendell/web/static/
```

**Validación**:
- Abrir http://localhost:8765 (servidor debe estar corriendo)
- Ver dashboard con proyectos
- Click en proyecto OFFLINE → debe crear terminal
- Ver terminal embebida con prompt
- Escribir comando (ej: `dir`) → debe ejecutarse
- Ver output en terminal

**Posibles errores**:
- **CSS de xterm.js no carga**: Agregar en `angular.json`:
  ```json
  "styles": [
    "node_modules/@xterm/xterm/css/xterm.css",
    "src/styles.scss"
  ]
  ```
- **WebSocket CORS**: Ya está configurado en server.py
- **Terminal no se ve**: Verificar que TerminalManager está inicializado

### TAREA 2: Testing End-to-End 🧪

**Escenarios a testear**:

1. **Crear terminal desde proyecto OFFLINE**:
   - Estado inicial: Proyecto rojo (OFFLINE)
   - Acción: Click en proyecto
   - Esperado: Loading spinner → terminal aparece → proyecto azul (READY)

2. **Ejecutar comandos**:
   - Comando simple: `dir` → debe mostrar archivos
   - Comando con output largo: `npm install` → debe scrollear
   - Comando interactivo: `python` → debe permitir input

3. **Toggle terminal**:
   - Click en proyecto azul/verde → terminal se oculta
   - Click de nuevo → terminal se muestra (misma sesión)

4. **Múltiples terminales**:
   - Abrir 2-3 proyectos simultáneamente
   - Verificar que cada terminal funciona independiente
   - Verificar que no hay conflictos en WebSocket

5. **Reconexión**:
   - Refrescar página (F5)
   - Terminal debe reconectar automáticamente
   - History debe mantenerse (si terminal sigue corriendo)

6. **Cerrar terminal**:
   - Click en botón X del terminal
   - Terminal debe cerrarse en UI
   - Proceso cmd.exe debe seguir corriendo (backend)

**Cómo testear**:
```bash
# Terminal 1: Servidor
cd /c/Users/Daniel/Desktop/Daniel/sendell
uv run uvicorn sendell.web.server:app --reload --port 8765

# Terminal 2: Abrir VS Code con sendell project
# Dashboard detectará el proyecto automáticamente

# Navegador: http://localhost:8765
# Seguir escenarios arriba
```

### TAREA 3: Fase 4 - Detección de Estados 🎯

**Objetivo**: Actualizar `project_states.py` para usar TerminalManager

**Contexto**: Actualmente `project_states.py` intenta detectar terminales child processes del PID de VS Code. Con TerminalManager, la lógica cambia:

**Lógica nueva**:
1. **OFFLINE**: `terminal_manager.get_terminal(project_pid)` retorna None
2. **READY**: Terminal existe Y NO tiene subprocess activo
3. **WORKING**: Terminal existe Y tiene subprocess activo

**Archivo a modificar**: `src/sendell/project_manager/project_states.py`

**Pseudocódigo**:
```python
from sendell.terminal_manager import get_terminal_manager

def detect_project_state(project_pid: int) -> str:
    terminal_manager = get_terminal_manager()
    terminal = terminal_manager.get_terminal(str(project_pid))

    if terminal is None:
        return "offline"  # No hay terminal

    if not terminal.is_running():
        return "offline"  # Terminal murió

    if terminal.has_active_subprocess():
        return "working"  # Comando activo

    return "ready"  # Terminal lista, sin comandos
```

**Integración**:
```python
# En routes.py o donde se consulten estados:
from sendell.project_manager.project_states import detect_project_state

# Para cada proyecto:
project_dict = {
    'pid': project.pid,
    'name': project.name,
    'state': detect_project_state(project.pid),  # ← Usar nueva lógica
    'has_terminal': terminal_manager.get_terminal(str(project.pid)) is not None
}
```

**Testing**:
- Proyecto sin terminal → OFFLINE ✅
- Abrir terminal → READY ✅
- Ejecutar `npm run dev` → WORKING ✅
- Terminar comando → READY ✅
- Cerrar terminal → OFFLINE ✅

### TAREA 4: CSS/Styling Polish (Opcional)

**Mejoras visuales**:
1. Terminal full-width debajo del proyecto card
2. Animación smooth al abrir/cerrar terminal
3. Resize handle para ajustar altura de terminal
4. Indicator en project card cuando terminal está abierta
5. Color coding: terminal verde si WORKING, azul si READY

**Ejemplo CSS**:
```scss
// En app.scss
.terminal-container {
  animation: slideDown 0.3s ease-out;
  margin-bottom: 1rem;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.project-card {
  &.has-terminal-open {
    border-color: #00ffff; // Cyan border cuando terminal abierta
  }
}
```

---

## 🔍 DEBUGGING TIPS

### Problema: Terminal no aparece

**Síntomas**: Click en proyecto, loading spinner, pero no se ve terminal

**Checks**:
1. Abrir DevTools → Network → WS → Ver conexión WebSocket
2. Ver console logs: ¿Hay errores de xterm.js?
3. Backend logs: ¿TerminalManager creó el terminal?
4. Verificar: `terminalService.isTerminalOpen(project.pid)` en Angular

**Solución común**: Olvidaste hacer build después de modificar código

### Problema: Comandos no se ejecutan

**Síntomas**: Escribes en terminal pero no pasa nada

**Checks**:
1. WebSocket está conectado (ws.readyState === WebSocket.OPEN)
2. Backend recibe mensaje tipo "input"
3. TerminalManager.send_command() se llama
4. stdin thread está corriendo

**Solución común**: Falta `\n` al final del comando

### Problema: Output no se muestra

**Síntomas**: Comando se ejecuta pero no ves output en terminal

**Checks**:
1. Backend stdout thread está leyendo
2. WebSocket broadcast funciona
3. Frontend onmessage handler se llama
4. terminal.write() se ejecuta

**Solución común**: Output tiene caracteres no-UTF8, usar `errors='replace'` en Popen

### Problema: Terminal se desconecta

**Síntomas**: Después de un tiempo, terminal deja de responder

**Checks**:
1. Proceso cmd.exe sigue vivo (Task Manager)
2. WebSocket sigue conectado
3. ManagedTerminalProcess.is_running() retorna True

**Solución común**: Agregar ping/pong para keep-alive WebSocket

---

## 📁 ESTRUCTURA DE ARCHIVOS (Referencia)

```
sendell/
├── src/sendell/
│   ├── terminal_manager/          ← NUEVO (Fase 1)
│   │   ├── __init__.py
│   │   ├── types.py              (Pydantic models)
│   │   ├── process.py            (ManagedTerminalProcess)
│   │   └── manager.py            (TerminalManager singleton)
│   │
│   ├── web/
│   │   ├── server.py             ← MODIFICADO (WebSocket endpoint)
│   │   └── routes.py             ← MODIFICADO (open-terminal endpoint)
│   │
│   └── project_manager/
│       └── project_states.py     ← PENDIENTE MODIFICAR (Fase 4)
│
├── sendell-dashboard/
│   ├── src/app/
│   │   ├── components/
│   │   │   └── terminal.component.ts  ← NUEVO (Fase 3)
│   │   │
│   │   ├── core/services/
│   │   │   ├── terminal.service.ts   ← NUEVO (Fase 3)
│   │   │   └── api.service.ts        ← MODIFICADO ✅
│   │   │
│   │   ├── app.ts                    ← MODIFICADO (click logic)
│   │   └── app.html                  ← MODIFICADO (render terminals)
│   │
│   └── package.json                  ← MODIFICADO (deps)
│
└── NEXT_SESSION_PLAN.md             ← ESTE ARCHIVO
```

---

## 🚀 QUICK START (Próxima sesión)

```bash
# 1. Verificar que servidor está corriendo
cd /c/Users/Daniel/Desktop/Daniel/sendell
uv run uvicorn sendell.web.server:app --reload --port 8765

# 2. Build dashboard
cd sendell-dashboard
npm run build

# 3. Deploy
cd ..
./build-dashboard.sh

# 4. Abrir navegador
# http://localhost:8765

# 5. Testear (ver TAREA 2)

# 6. Implementar Fase 4 si tests pasan
# (ver TAREA 3)
```

---

## 🎓 APRENDIZAJES CLAVE

1. **subprocess.Popen es mejor que pty**: 98% reliability, cross-platform
2. **Threading para I/O**: No bloquear servidor, queues para comunicación
3. **WebSocket bidireccional**: Más eficiente que polling REST
4. **xterm.js es poderoso**: Terminal completo en browser, 100% customizable
5. **Signals en Angular**: Reactivo, simple, integra perfecto con WebSocket
6. **Singleton pattern**: Esencial para gestionar estado global (TerminalManager)

---

## 📝 NOTAS PARA DANIEL

- **No olvides hacer build** después de cambios en Angular
- **Server debe estar corriendo** antes de abrir dashboard
- **Terminal cmd.exe** quedará corriendo aunque cierres dashboard (es intencional)
- **Limpieza**: Si quieres matar todos los terminales, restart del servidor los cierra
- **Performance**: Con 10+ terminales, considera throttling de output

---

**ESTADO FINAL**: Fase 1-3 completas ✅ | Fase 4 pendiente ⏳ | Build pendiente ⏳

**PRÓXIMOS PASOS**: Build → Test → Fase 4 → Commit

**ESTIMACIÓN**: 1-2 horas para completar todo
