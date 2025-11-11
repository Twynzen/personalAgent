# INTEGRACIÓN FALTANTE: Chat → Dashboard

## Problema Identificado por Daniel ✅

El flujo debería ser:
```
Usuario: "Sendell, abre tu cerebro"
  ↓
Agente: usa tool open_dashboard()
  ↓
Navegador abre http://localhost:8765
  ↓
Dashboard funciona
```

**PERO** actualmente faltan 2 cosas:
1. ❌ Tool `open_dashboard()` no existe en el agente
2. ❌ Servidor web no se auto-inicia con `uv run python -m sendell chat`

---

## Solución 1: Agregar Tool `open_dashboard`

**Ubicación**: `src/sendell/agent/core.py` (en método `_create_tools`)

**Agregar después de `show_brain()`**:

```python
@tool
def open_dashboard() -> dict:
    """Open the Sendell Cerebro web dashboard in the default browser.

    This opens a visual web interface where Daniel can:
    - See all active VS Code projects
    - View project states (OFFLINE/READY/WORKING)
    - Open embedded terminals for each project
    - Monitor system metrics (CPU, RAM, terminals count)
    - View Claude Code terminals
    - Access real-time activity graphs

    The dashboard provides a comprehensive view of all development projects
    and allows direct interaction with terminals through the web interface.

    Use this when Daniel asks to:
    - "open dashboard"
    - "show cerebro"
    - "let me see my projects"
    - "open the visual interface"
    - "show me the web interface"

    Note: The dashboard server must be running (port 8765).
    If not running, it will be auto-started.

    Returns:
        dict: Success status and dashboard URL
    """
    import webbrowser
    import socket

    # Check if server is already running
    def is_server_running():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', 8765))
                return result == 0
        except:
            return False

    dashboard_url = "http://localhost:8765"

    try:
        # Check if server is running
        if not is_server_running():
            # Auto-start server
            logger.info("Dashboard server not running, attempting to start...")

            import subprocess
            import os

            # Start server in background
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            # Use CREATE_NO_WINDOW flag to hide cmd window
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                subprocess.Popen(
                    ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                    cwd=project_root,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                    cwd=project_root,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Wait a bit for server to start
            import time
            time.sleep(2)

            # Verify it started
            if not is_server_running():
                return {
                    "success": False,
                    "error": "Server failed to start",
                    "message": "Dashboard server failed to start. Please start manually with: uv run uvicorn sendell.web.server:app --port 8765"
                }

            logger.info("Dashboard server started successfully")

        # Open browser
        webbrowser.open(dashboard_url)

        return {
            "success": True,
            "url": dashboard_url,
            "message": f"Dashboard opened in browser at {dashboard_url}"
        }

    except Exception as e:
        logger.error(f"Failed to open dashboard: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to open dashboard: {str(e)}"
        }
```

**Luego, agregarlo a la lista de tools**:

Buscar la línea que dice:
```python
return [get_system_health, get_active_window, list_top_processes,
        open_application, respond_to_user, show_brain, add_reminder,
        list_vscode_instances]
```

Y agregar `open_dashboard`:
```python
return [get_system_health, get_active_window, list_top_processes,
        open_application, respond_to_user, show_brain, add_reminder,
        list_vscode_instances, open_dashboard]
```

---

## Solución 2: Auto-Iniciar Servidor con Chat

**Problema**: Cuando se ejecuta `uv run python -m sendell chat`, el servidor web NO se inicia automáticamente.

**Opción A - RECOMENDADA**: Iniciar servidor en `__main__.py` (comando `chat`)

**Ubicación**: `src/sendell/__main__.py`

**Modificar función `run_chat()`**:

```python
def run_chat():
    """Run interactive chat with Sendell (with proactive loop)."""
    import asyncio

    # Auto-start dashboard server
    logger.info("Starting dashboard server...")
    start_dashboard_server()

    # Rest of function...
    asyncio.run(_async_chat_with_proactive())

def start_dashboard_server():
    """Start dashboard server in background if not already running."""
    import socket
    import subprocess
    import os
    import time

    def is_server_running():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', 8765))
                return result == 0
        except:
            return False

    if is_server_running():
        logger.info("Dashboard server already running on port 8765")
        return

    logger.info("Starting dashboard server on port 8765...")

    project_root = os.path.dirname(os.path.dirname(__file__))

    try:
        if os.name == 'nt':  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            subprocess.Popen(
                ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                cwd=project_root,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  # Linux/Mac
            subprocess.Popen(
                ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Wait for server to start
        time.sleep(2)

        if is_server_running():
            logger.info("✅ Dashboard server started successfully")
            console.print("[green]✅ Dashboard server started on http://localhost:8765[/green]")
        else:
            logger.warning("Dashboard server may not have started correctly")

    except Exception as e:
        logger.error(f"Failed to start dashboard server: {e}")
        console.print(f"[yellow]⚠️  Failed to start dashboard server: {e}[/yellow]")
```

**Opción B - ALTERNATIVA**: Usar el tool `open_dashboard` que auto-inicia

Si no quieres modificar `__main__.py`, el tool `open_dashboard` ya tiene lógica para auto-iniciar el servidor cuando el agente lo invoca.

---

## Flujo Completo Después de la Implementación

### Escenario 1: Usuario pide abrir cerebro

```bash
$ uv run python -m sendell chat
[Dashboard server auto-inicia en background]

Sendell > Hola! How can I help?

You > abre tu cerebro

Sendell > [invoca tool open_dashboard()]
✅ Dashboard opened in browser at http://localhost:8765

[Navegador se abre automáticamente]
[Dashboard muestra proyectos VS Code]
```

### Escenario 2: Servidor ya está corriendo

```bash
# Terminal 1:
$ uv run uvicorn sendell.web.server:app --port 8765
[Servidor ya corriendo]

# Terminal 2:
$ uv run python -m sendell chat
[Detecta que servidor ya está corriendo, no inicia otro]

You > abre dashboard

Sendell > [invoca tool open_dashboard()]
✅ Dashboard opened in browser at http://localhost:8765

[Navegador se abre]
```

### Escenario 3: Usuario interactúa con terminales

```bash
You > qué proyectos tengo abiertos?

Sendell > [invoca tool list_vscode_instances()]
Tienes 3 proyectos abiertos:
1. sendell (C:\Users\Daniel\Desktop\Daniel\sendell)
2. proyecto-x (C:\Users\Daniel\Desktop\proyectos\proyecto-x)
3. mi-app (C:\Users\Daniel\Desktop\mi-app)

You > abre el cerebro para verlos mejor

Sendell > [invoca tool open_dashboard()]
✅ Dashboard opened in browser

[En el dashboard, usuario ve los 3 proyectos]
[Click en proyecto OFFLINE → terminal se abre embebida]
[Escribe comandos en terminal embebida]
```

---

## Testing del Flujo Completo

### Test 1: Auto-start desde chat

```bash
# 1. Asegurarse que NO hay servidor corriendo
ps aux | grep uvicorn  # Linux/Mac
tasklist | findstr uvicorn  # Windows
# Si hay, matar proceso

# 2. Iniciar chat
uv run python -m sendell chat

# 3. Verificar que servidor se inició
# Debería ver mensaje: "✅ Dashboard server started on http://localhost:8765"

# 4. Abrir navegador manualmente
# http://localhost:8765
# Debería cargar dashboard
```

### Test 2: Tool open_dashboard

```bash
# 1. Chat corriendo
uv run python -m sendell chat

# 2. Pedir al agente
You > abre tu cerebro
You > abre el dashboard
You > muéstrame la interfaz web

# 3. Verificar
# - Tool se invoca
# - Navegador se abre automáticamente
# - Dashboard carga correctamente
```

### Test 3: Flujo completo con terminales

```bash
# 1. Iniciar chat (servidor auto-inicia)
uv run python -m sendell chat

# 2. Listar proyectos
You > qué proyectos tengo?

# 3. Abrir dashboard
You > abre el cerebro

# 4. En dashboard
# - Ver proyectos listados
# - Click en proyecto OFFLINE
# - Ver terminal embebida
# - Escribir: dir
# - Ver output en terminal
```

---

## Implementación Paso a Paso

### Paso 1: Agregar tool open_dashboard
```bash
# 1. Editar core.py
nano src/sendell/agent/core.py

# 2. Agregar función open_dashboard después de show_brain
# (ver código arriba)

# 3. Agregar a lista de tools
# (ver código arriba)
```

### Paso 2: Auto-start servidor
```bash
# OPCIÓN A: Modificar __main__.py
nano src/sendell/__main__.py

# Agregar función start_dashboard_server()
# Llamarla en run_chat() al inicio

# OPCIÓN B: Confiar en open_dashboard tool
# No modificar __main__.py
# Servidor se inicia cuando agente invoca open_dashboard
```

### Paso 3: Testing
```bash
# 1. Build dashboard (si no lo hiciste)
cd sendell-dashboard
npm run build
cd ..
./build-dashboard.sh

# 2. Test chat + auto-start
uv run python -m sendell chat

# 3. Test tool
You > abre dashboard
```

---

## Decisión: ¿Opción A o B?

### Opción A (Auto-start en __main__.py)
**Pros**:
- Servidor siempre disponible cuando usas chat
- No depende de que usuario pida abrir dashboard
- Mejor UX (transparente)

**Contras**:
- Consume recursos aunque usuario no use dashboard
- Proceso extra corriendo en background

### Opción B (Auto-start en tool)
**Pros**:
- Solo inicia cuando se necesita
- Menor consumo de recursos si no se usa
- Código más concentrado en un lugar

**Contras**:
- Delay de 2s la primera vez que usuario pide dashboard
- Depende de que agente invoque el tool

### RECOMENDACIÓN: Opción A

Daniel probablemente querrá el dashboard disponible siempre que use el chat. Es mejor tener el servidor corriendo desde el inicio.

---

## Archivos a Modificar

1. ✅ `src/sendell/agent/core.py` - Agregar tool `open_dashboard()`
2. ✅ `src/sendell/__main__.py` - Agregar auto-start de servidor (Opción A)
3. ⏳ Testing manual para verificar flujo completo

---

## Próximos Pasos (En Orden)

1. ✅ Implementar tool `open_dashboard` en core.py
2. ✅ Implementar auto-start en __main__.py
3. ⏳ Build dashboard: `cd sendell-dashboard && npm run build`
4. ⏳ Deploy: `./build-dashboard.sh`
5. ⏳ Test flujo completo desde chat
6. ⏳ Commit todo junto

**Estimación**: 30 minutos implementación + 15 minutos testing = 45 minutos total
