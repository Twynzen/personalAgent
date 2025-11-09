# 🚀 PLAN DE MIGRACIÓN A ANGULAR - INSTRUCCIONES COMPLETAS

**Fecha:** 2025-11-09
**Rama:** `feature/brain-projects-tab`
**Objetivo:** Migrar Brain GUI de Qt6 puro a Angular embebido en Qt6
**Razón:** Eliminar "tirones" cada 5 segundos causados por `find_vscode_instances()` bloqueando UI

---

## 📍 CONTEXTO ACTUAL

### ✅ YA COMPLETADO:
- ✅ Qt6 Brain GUI funciona (4 tabs: Memorias, Prompts, Herramientas, Proyectos)
- ✅ Detecta proyectos VS Code con psutil
- ✅ Gráficos ECG animados a 60 FPS
- ✅ Sin crashes de GIL (eliminamos tkinter)

### ❌ PROBLEMA ACTUAL:
- ❌ **UI se "congela" cada 5 segundos** cuando escanea procesos
- ❌ `VSCodeMonitor.find_vscode_instances()` corre en main thread → bloquea UI
- ❌ Escanea TODOS los procesos del sistema (costoso)

### ✨ SOLUCIÓN ELEGIDA:
- **Backend FastAPI** con WebSocket para real-time async
- **Frontend Angular** profesional y escalable
- **Embebido en Qt6** via `QtWebEngineView`
- **NO más bloqueos** - updates asíncronos vía WebSocket push

---

## 🗂️ ARCHIVOS ACTUALES A ENTENDER

### **Brain GUI (SERÁ REEMPLAZADO POR ANGULAR):**
```
src/sendell/agent/brain_gui_qt.py       # 573 líneas - GUI Qt6 actual
  ├── class BrainGUIQt(QMainWindow)
  ├── create_memories_tab()              # Facts CRUD
  ├── create_prompts_tab()               # System prompt editor
  ├── create_tools_tab()                 # Tools viewer
  └── create_projects_tab()              # Dashboard (usa project_control_qt)

src/sendell/agent/brain_gui.py          # LEGACY tkinter (NO USAR)
```

### **Dashboard Proyectos (LÓGICA A MIGRAR A ANGULAR):**
```
src/sendell/dashboard/project_control_qt.py     # 400 líneas
  ├── class ProjectControlWidgetQt              # Main widget
  ├── _update_data()                            # Escanea VS Code cada 5s ← PROBLEMA
  ├── _render_projects()                        # Renderiza cards
  └── _create_project_card()                    # Card individual

src/sendell/dashboard/components/activity_graph_qt.py  # 200 líneas
  ├── class ActivityGraphQt                     # Gráfico ECG
  └── paintEvent()                              # Dibuja pulse con QPainter
```

### **VS Code Monitor (REUTILIZAR EN BACKEND):**
```
src/sendell/vscode/monitor.py           # 150 líneas
  ├── class VSCodeMonitor
  └── find_vscode_instances()           # Escanea procesos (COSTOSO)

src/sendell/vscode/types.py             # 100 líneas
  ├── class VSCodeInstance              # Modelo de datos
  └── class WorkspaceInfo               # Info del workspace
```

### **Memory & Config (EXPONER EN API REST):**
```
src/sendell/agent/memory.py             # 300 líneas
  ├── class SendellMemory
  ├── add_fact()
  ├── remove_fact()
  ├── get_facts()
  └── (usa data/sendell_memory.json)

src/sendell/agent/prompts.py            # 100 líneas
  └── get_system_prompt()               # Lee prompt actual
```

### **Entry Points (ACTUALIZAR AL FINAL):**
```
src/sendell/agent/core.py               # Línea 176: usa brain_gui_qt
src/sendell/__main__.py                 # Línea 286: usa brain_gui_qt
```

---

## 🎯 ARCHIVOS A CREAR (NUEVA ARQUITECTURA)

### **PASO 1: Backend FastAPI**

```
src/sendell/web/
├── __init__.py
├── server.py           # FastAPI app + startup
├── routes.py           # REST endpoints
├── websocket.py        # WebSocket manager
└── background.py       # Async VS Code scanning
```

**Dependencias a instalar:**
```bash
uv add fastapi uvicorn python-multipart PySide6-WebEngine
```

### **PASO 2: Frontend Angular**

```
sendell-dashboard/                      # Proyecto Angular (raíz del repo)
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts              # REST API client
│   │   │   │   ├── websocket.service.ts        # WebSocket client
│   │   │   │   └── state.service.ts            # State management
│   │   │   └── models/
│   │   │       ├── fact.model.ts
│   │   │       ├── project.model.ts
│   │   │       └── metrics.model.ts
│   │   │
│   │   ├── features/
│   │   │   ├── memorias/
│   │   │   │   ├── memorias.component.ts
│   │   │   │   ├── memorias.component.html
│   │   │   │   └── memorias.component.scss
│   │   │   ├── prompts/
│   │   │   │   └── (similar structure)
│   │   │   ├── herramientas/
│   │   │   │   └── (similar structure)
│   │   │   └── proyectos/
│   │   │       ├── proyectos.component.ts
│   │   │       ├── proyectos.component.html
│   │   │       ├── proyectos.component.scss
│   │   │       ├── components/
│   │   │       │   ├── project-card/           # Card individual
│   │   │       │   ├── metrics-panel/          # Panel izquierdo
│   │   │       │   └── activity-graph/         # Gráfico ECG (Canvas)
│   │   │
│   │   ├── app.component.ts                    # Main container
│   │   ├── app.component.html                  # Layout con tabs
│   │   └── app.routes.ts                       # Routing
│   │
│   └── styles/
│       ├── styles.scss                         # Global styles
│       ├── _cyberpunk-theme.scss               # Negro + verde neón
│       └── _animations.scss                    # Pulse animations
│
├── angular.json
├── package.json
└── tsconfig.json
```

**Crear proyecto:**
```bash
cd /c/Users/Daniel/Desktop/Daniel/sendell
ng new sendell-dashboard --routing --style=scss --standalone --skip-git
```

### **PASO 3: Build y Deploy**

**Después de desarrollar Angular:**
```bash
cd sendell-dashboard
ng build --configuration production --base-href /

# Copiar build a Python package
mkdir -p ../src/sendell/web/static
cp -r dist/sendell-dashboard/browser/* ../src/sendell/web/static/
```

**Servir desde FastAPI (en server.py):**
```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="src/sendell/web/static", html=True), name="static")
```

---

## 📝 IMPLEMENTACIÓN PASO A PASO

### **FASE 1: Backend FastAPI (2-3 horas)**

#### 1.1 Crear estructura base

```bash
mkdir -p src/sendell/web
touch src/sendell/web/__init__.py
```

#### 1.2 Implementar `server.py`

**Template completo:**
```python
"""
FastAPI server for Sendell Brain Dashboard
Provides REST API + WebSocket for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from pathlib import Path

from sendell.web.routes import router
from sendell.web.websocket import WebSocketManager
from sendell.web.background import start_vscode_scanner
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Sendell Brain API", version="0.3.0")

# CORS para Angular (dev: 4200, prod: 8765)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
ws_manager = WebSocketManager()

# Include REST routes
app.include_router(router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Startup: iniciar scanner en background
@app.on_event("startup")
async def startup():
    logger.info("Starting Sendell Brain API server...")

    # Iniciar VS Code scanner
    asyncio.create_task(start_vscode_scanner(ws_manager))

    logger.info("API server ready on http://localhost:8765")

# Servir archivos estáticos de Angular (después del build)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"Serving Angular app from {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
```

#### 1.3 Implementar `routes.py`

```python
"""REST API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import psutil

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_system_prompt
from sendell.vscode import VSCodeMonitor

router = APIRouter()

# Models
class Fact(BaseModel):
    fact: str
    category: str = "general"

class PromptUpdate(BaseModel):
    prompt: str

# ==================== FACTS ====================

@router.get("/facts")
async def get_facts():
    """Get all facts from memory"""
    memory = get_memory()
    return {"facts": memory.get_facts()}

@router.post("/facts")
async def add_fact(fact: Fact):
    """Add a new fact"""
    memory = get_memory()
    memory.add_fact(fact.fact, fact.category)
    return {"success": True, "fact": fact}

@router.delete("/facts/{index}")
async def delete_fact(index: int):
    """Delete a fact by index"""
    memory = get_memory()
    memory.remove_fact(index)
    return {"success": True}

# ==================== PROMPTS ====================

@router.get("/prompts")
async def get_prompt():
    """Get current system prompt"""
    return {"prompt": get_system_prompt()}

@router.post("/prompts")
async def update_prompt(data: PromptUpdate):
    """Update system prompt (TODO: implement save)"""
    # TODO: Save to prompts.py
    return {"success": True, "prompt": data.prompt}

# ==================== TOOLS ====================

@router.get("/tools")
async def get_tools():
    """Get list of available tools"""
    from sendell.agent.core import get_agent

    try:
        agent = get_agent()
        tools_info = []

        for tool in agent.tools:
            tools_info.append({
                "name": tool.name if hasattr(tool, 'name') else str(tool),
                "description": tool.description if hasattr(tool, 'description') else "No description"
            })

        return {"tools": tools_info}
    except Exception as e:
        return {"tools": []}

# ==================== PROJECTS (snapshot) ====================

@router.get("/projects")
async def get_projects():
    """Get current VS Code projects (snapshot)"""
    monitor = VSCodeMonitor()
    instances = monitor.find_vscode_instances()

    projects = []
    for inst in instances:
        projects.append({
            "pid": inst.pid,
            "name": inst.name,
            "workspace_name": inst.workspace.workspace_name,
            "workspace_path": inst.workspace.workspace_path,
            "workspace_type": inst.workspace.workspace_type,
        })

    return {"projects": projects}

# ==================== METRICS (snapshot) ====================

@router.get("/metrics")
async def get_metrics():
    """Get system metrics (snapshot)"""
    return {
        "cpu": psutil.cpu_percent(interval=0),
        "ram": psutil.virtual_memory().percent,
        "terminals": len(VSCodeMonitor().find_vscode_instances())
    }
```

#### 1.4 Implementar `websocket.py`

```python
"""WebSocket connection manager"""

from fastapi import WebSocket
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        message_json = json.dumps(message)

        for connection in self.active_connections[:]:  # Copy to avoid modification during iteration
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                self.disconnect(connection)
```

#### 1.5 Implementar `background.py`

```python
"""Background tasks for async scanning"""

import asyncio
import psutil
from sendell.vscode import VSCodeMonitor
from sendell.web.websocket import WebSocketManager
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

async def start_vscode_scanner(ws_manager: WebSocketManager):
    """
    Background task that scans VS Code instances every 10 seconds
    and broadcasts updates via WebSocket
    """
    logger.info("Starting VS Code scanner (background task)")
    monitor = VSCodeMonitor()

    while True:
        try:
            # Scan VS Code instances
            instances = monitor.find_vscode_instances()

            # Get system metrics
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent

            # Build projects data
            projects = []
            for inst in instances:
                projects.append({
                    "pid": inst.pid,
                    "name": inst.name,
                    "workspace_name": inst.workspace.workspace_name or "Unknown",
                    "workspace_path": inst.workspace.workspace_path or "",
                    "workspace_type": inst.workspace.workspace_type,
                    "is_running": "sendell" in (inst.workspace.workspace_name or "").lower() or
                                 "gsiaf" in (inst.workspace.workspace_name or "").lower()
                })

            # Broadcast to all WebSocket clients
            await ws_manager.broadcast({
                "type": "update",
                "data": {
                    "projects": projects,
                    "metrics": {
                        "cpu": cpu,
                        "ram": ram,
                        "terminals": len(instances)
                    }
                }
            })

        except Exception as e:
            logger.error(f"Error in VS Code scanner: {e}")

        # Wait 10 seconds before next scan
        await asyncio.sleep(10)
```

#### 1.6 Testing del backend

```bash
# Instalar dependencias
uv add fastapi uvicorn python-multipart PySide6-WebEngine

# Ejecutar servidor
uv run uvicorn sendell.web.server:app --reload --port 8765

# Probar endpoints en navegador:
# http://localhost:8765/api/facts
# http://localhost:8765/api/projects
# http://localhost:8765/api/metrics
# http://localhost:8765/api/tools

# Probar WebSocket con extensión de navegador o script Python
```

---

### **FASE 2: Frontend Angular (3-4 horas)**

#### 2.1 Crear proyecto Angular

```bash
cd /c/Users/Daniel/Desktop/Daniel/sendell
ng new sendell-dashboard --routing --style=scss --standalone --skip-git

cd sendell-dashboard
```

#### 2.2 Crear proxy para dev (evitar CORS)

**Crear `proxy.conf.json`:**
```json
{
  "/api": {
    "target": "http://localhost:8765",
    "secure": false,
    "changeOrigin": true
  },
  "/ws": {
    "target": "ws://localhost:8765",
    "ws": true,
    "changeOrigin": true
  }
}
```

**Actualizar `package.json`:**
```json
{
  "scripts": {
    "start": "ng serve --proxy-config proxy.conf.json"
  }
}
```

#### 2.3 Implementar Services

**`src/app/core/services/api.service.ts`:**
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Fact, Tool } from '../models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = '/api'; // Proxy redirect to :8765

  constructor(private http: HttpClient) {}

  // Facts
  getFacts(): Observable<{ facts: Fact[] }> {
    return this.http.get<{ facts: Fact[] }>(`${this.baseUrl}/facts`);
  }

  addFact(fact: Fact): Observable<any> {
    return this.http.post(`${this.baseUrl}/facts`, fact);
  }

  deleteFact(index: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/facts/${index}`);
  }

  // Prompts
  getPrompt(): Observable<{ prompt: string }> {
    return this.http.get<{ prompt: string }>(`${this.baseUrl}/prompts`);
  }

  updatePrompt(prompt: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/prompts`, { prompt });
  }

  // Tools
  getTools(): Observable<{ tools: Tool[] }> {
    return this.http.get<{ tools: Tool[] }>(`${this.baseUrl}/tools`);
  }

  // Projects (snapshot)
  getProjects(): Observable<any> {
    return this.http.get(`${this.baseUrl}/projects`);
  }

  // Metrics (snapshot)
  getMetrics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/metrics`);
  }
}
```

**`src/app/core/services/websocket.service.ts`:**
```typescript
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

interface WSMessage {
  type: string;
  data: any;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket!: WebSocket;

  public messages$ = new Subject<WSMessage>();
  public connected$ = new Subject<boolean>();

  connect() {
    this.socket = new WebSocket('ws://localhost:8765/ws');

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.connected$.next(true);
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.messages$.next(message);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.connected$.next(false);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.connected$.next(false);

      // Reconnect after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}
```

#### 2.4 Crear componentes principales

**Generar componentes:**
```bash
ng generate component features/memorias --standalone
ng generate component features/prompts --standalone
ng generate component features/herramientas --standalone
ng generate component features/proyectos --standalone
ng generate component features/proyectos/components/project-card --standalone
ng generate component features/proyectos/components/metrics-panel --standalone
ng generate component features/proyectos/components/activity-graph --standalone
```

#### 2.5 Implementar layout principal

**`src/app/app.component.html`:**
```html
<div class="sendell-container">
  <header class="sendell-header">
    <h1>SENDELL CEREBRO</h1>
    <span class="live-indicator">● LIVE</span>
  </header>

  <nav class="sendell-tabs">
    <button
      *ngFor="let tab of tabs"
      [class.active]="activeTab === tab.id"
      (click)="activeTab = tab.id">
      {{ tab.label }}
    </button>
  </nav>

  <main class="sendell-content">
    @switch (activeTab) {
      @case ('memorias') { <app-memorias /> }
      @case ('prompts') { <app-prompts /> }
      @case ('herramientas') { <app-herramientas /> }
      @case ('proyectos') { <app-proyectos /> }
    }
  </main>
</div>
```

**`src/app/app.component.ts`:**
```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from './core/services/websocket.service';
import { MemoriasComponent } from './features/memorias/memorias.component';
import { PromptsComponent } from './features/prompts/prompts.component';
import { HerramientasComponent } from './features/herramientas/herramientas.component';
import { ProyectosComponent } from './features/proyectos/proyectos.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    MemoriasComponent,
    PromptsComponent,
    HerramientasComponent,
    ProyectosComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  activeTab = 'proyectos';

  tabs = [
    { id: 'memorias', label: 'MEMORIAS' },
    { id: 'prompts', label: 'PROMPTS' },
    { id: 'herramientas', label: 'HERRAMIENTAS' },
    { id: 'proyectos', label: 'PROYECTOS' }
  ];

  constructor(private ws: WebSocketService) {}

  ngOnInit() {
    this.ws.connect();
  }

  ngOnDestroy() {
    this.ws.disconnect();
  }
}
```

#### 2.6 Estilos cyberpunk

**`src/styles/_cyberpunk-theme.scss`:**
```scss
$bg-dark: #000000;
$bg-panel: #0a0a0a;
$neon-green: #00ff00;
$neon-cyan: #00ffff;
$neon-red: #ff0055;
$text-primary: #ffffff;
$text-secondary: #888888;

@mixin cyber-border {
  border: 2px solid $neon-green;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.sendell-container {
  background: $bg-dark;
  color: $text-primary;
  font-family: 'Courier New', monospace;
  min-height: 100vh;
}

.sendell-header {
  background: $bg-dark;
  padding: 1rem 2rem;
  @include cyber-border;

  h1 {
    color: $neon-green;
    font-size: 1.5rem;
    margin: 0;
  }
}

.sendell-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: $bg-panel;

  button {
    background: $bg-dark;
    color: $neon-green;
    border: 1px solid $neon-green;
    padding: 0.75rem 1.5rem;
    font-family: 'Courier New';
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: rgba(0, 255, 0, 0.1);
    }

    &.active {
      background: rgba(0, 255, 0, 0.2);
      box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }
  }
}
```

#### 2.7 Componente Proyectos (el más complejo)

**`src/app/features/proyectos/proyectos.component.ts`:**
```typescript
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../core/services/websocket.service';
import { ProjectCardComponent } from './components/project-card/project-card.component';
import { MetricsPanelComponent } from './components/metrics-panel/metrics-panel.component';

interface Project {
  pid: number;
  name: string;
  workspace_name: string;
  workspace_path: string;
  is_running: boolean;
}

interface Metrics {
  cpu: number;
  ram: number;
  terminals: number;
}

@Component({
  selector: 'app-proyectos',
  standalone: true,
  imports: [CommonModule, ProjectCardComponent, MetricsPanelComponent],
  templateUrl: './proyectos.component.html',
  styleUrls: ['./proyectos.component.scss']
})
export class ProyectosComponent implements OnInit {
  projects = signal<Project[]>([]);
  metrics = signal<Metrics>({ cpu: 0, ram: 0, terminals: 0 });

  constructor(private ws: WebSocketService) {}

  ngOnInit() {
    // Subscribe to WebSocket updates
    this.ws.messages$.subscribe((message) => {
      if (message.type === 'update') {
        this.projects.set(message.data.projects);
        this.metrics.set(message.data.metrics);
      }
    });
  }
}
```

---

### **FASE 3: Build e Integración (1 hora)**

#### 3.1 Build de Angular para producción

```bash
cd sendell-dashboard
ng build --configuration production --base-href /

# Verificar que se generó dist/sendell-dashboard/browser/
ls dist/sendell-dashboard/browser/
```

#### 3.2 Copiar a Python package

```bash
# Crear directorio static
mkdir -p ../src/sendell/web/static

# Copiar build
cp -r dist/sendell-dashboard/browser/* ../src/sendell/web/static/

# Verificar
ls ../src/sendell/web/static/
```

#### 3.3 Actualizar brain_gui_qt.py

**Reemplazar contenido con:**
```python
"""
Sendell Brain GUI - Web-based version with Angular
Embeds Angular app via QtWebEngineView
"""

import sys
import time
from PySide6.QtCore import QUrl, QThread
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class BackendThread(QThread):
    """Thread to run FastAPI server"""
    def run(self):
        import uvicorn
        from sendell.web.server import app

        logger.info("Starting FastAPI server on http://localhost:8765")
        uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")


class BrainGUIQt(QMainWindow):
    """
    Sendell Brain Interface (Web version).

    Embeds Angular dashboard via QtWebEngineView.
    Backend runs in separate thread.
    """

    def __init__(self, tools=None):
        """Initialize Brain GUI"""
        super().__init__()

        self.setWindowTitle("Sendell - Ver Cerebro (Web)")
        self.resize(1600, 1000)

        logger.info("Starting Sendell Brain (Web version)...")

        # Start backend server in background thread
        self.backend_thread = BackendThread()
        self.backend_thread.start()

        # Wait for server to start
        logger.info("Waiting for backend to start...")
        time.sleep(3)

        # Create web view
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://localhost:8765"))

        self.setCentralWidget(self.web_view)

        logger.info("Brain GUI (Web) initialized")

    def closeEvent(self, event):
        """Cleanup when window closes"""
        logger.info("Closing Brain GUI...")

        # Terminate backend thread
        self.backend_thread.terminate()
        self.backend_thread.wait(timeout=2000)

        super().closeEvent(event)


def show_brain(tools=None) -> str:
    """
    Show the Sendell Brain GUI (Web version).

    Args:
        tools: List of available tools (not used in web version)

    Returns:
        Success message
    """
    from sendell.dashboard.qt_tkinter_bridge import QtBridge

    logger.info("Opening Sendell Brain (Web)...")

    # Ensure QApplication exists
    app = QtBridge.get_qapp()

    # Create and show GUI
    gui = BrainGUIQt(tools)
    gui.show()

    # Run Qt event loop
    app.exec()

    return "Brain GUI closed"
```

---

### **FASE 4: Testing e Iteración**

#### 4.1 Test Backend + Angular Integrado

```bash
# Ejecutar Brain GUI (inicia backend automáticamente)
uv run python -m sendell brain
```

**Esperado:**
- ✅ Ventana Qt6 se abre
- ✅ Carga Angular app desde http://localhost:8765
- ✅ Tabs funcionan
- ✅ WebSocket conecta
- ✅ Proyectos se actualizan cada 10s sin lag

#### 4.2 Test desde chat

```bash
uv run python -m sendell chat
# Escribir: "abre tu cerebro"
```

#### 4.3 Troubleshooting

**Si no carga Angular:**
- Verificar que existe `src/sendell/web/static/index.html`
- Verificar logs de FastAPI
- Abrir http://localhost:8765 en navegador normal

**Si WebSocket no conecta:**
- Verificar console del navegador (F12)
- Revisar CORS en FastAPI
- Verificar que backend está escuchando en :8765

**Si hay lag aún:**
- Aumentar intervalo de scan de 10s a 15s o 30s
- Optimizar `find_vscode_instances()` (caché)

---

## 🗑️ ARCHIVOS A ELIMINAR (DESPUÉS DE CONFIRMAR QUE FUNCIONA)

```bash
# LEGACY Qt6 components (ya no se usan)
git rm src/sendell/dashboard/project_control_qt.py
git rm src/sendell/dashboard/components/activity_graph_qt.py
git rm src/sendell/dashboard/qt_tkinter_bridge.py

# LEGACY tkinter brain GUI
git rm src/sendell/agent/brain_gui.py

# Tkinter dashboard components
git rm src/sendell/dashboard/project_control.py
git rm src/sendell/dashboard/components/activity_graph.py
```

**NO eliminar:**
- `src/sendell/vscode/` - Reutilizado en backend
- `src/sendell/agent/memory.py` - Usado en API
- `src/sendell/agent/prompts.py` - Usado en API
- `src/sendell/dashboard/utils/` - Colores reutilizados

---

## 📚 REFERENCIAS Y RECURSOS

### **Documentación a consultar:**
1. `CLAUDE.md` - Historia completa del proyecto
2. `src/sendell/vscode/monitor.py` - Cómo funciona VS Code detection
3. `src/sendell/agent/memory.py` - Estructura de facts
4. FastAPI docs: https://fastapi.tiangolo.com/
5. Angular docs: https://angular.dev/

### **Ejemplos de código en el proyecto:**
1. WebSocket: `src/sendell/vscode_integration/websocket_server.py` (LEGACY pero útil de referencia)
2. VS Code scanning: `src/sendell/vscode/monitor.py`
3. Memory CRUD: `src/sendell/agent/memory.py`

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Backend FastAPI:
- [ ] Instalar dependencias: `uv add fastapi uvicorn python-multipart PySide6-WebEngine`
- [ ] Crear `src/sendell/web/server.py`
- [ ] Crear `src/sendell/web/routes.py`
- [ ] Crear `src/sendell/web/websocket.py`
- [ ] Crear `src/sendell/web/background.py`
- [ ] Test: `uv run uvicorn sendell.web.server:app --reload --port 8765`
- [ ] Verificar endpoints: /api/facts, /api/projects, /api/metrics

### Frontend Angular:
- [ ] Verificar Node.js: `node --version` (necesita v18+)
- [ ] Instalar Angular CLI: `npm install -g @angular/cli`
- [ ] Crear proyecto: `ng new sendell-dashboard --routing --style=scss --standalone --skip-git`
- [ ] Crear proxy.conf.json
- [ ] Implementar services (api, websocket)
- [ ] Crear componentes (memorias, prompts, herramientas, proyectos)
- [ ] Implementar estilos cyberpunk
- [ ] Test: `cd sendell-dashboard && npm start`
- [ ] Build: `ng build --configuration production --base-href /`

### Integración:
- [ ] Copiar build a `src/sendell/web/static/`
- [ ] Actualizar `brain_gui_qt.py` con QtWebEngineView
- [ ] Test: `uv run python -m sendell brain`
- [ ] Verificar no hay lag al actualizar proyectos
- [ ] Test desde chat: "abre tu cerebro"

### Cleanup:
- [ ] Eliminar archivos legacy Qt/tkinter
- [ ] Actualizar CLAUDE.md con nueva arquitectura
- [ ] Commit final: `feat(web): Complete migration to Angular dashboard`

---

## 🎯 RESULTADO ESPERADO

**Después de completar esta migración:**

1. **✅ Sin Lag** - Updates via WebSocket asíncrono (no bloquea UI)
2. **✅ Profesional** - Dashboard Angular moderno y escalable
3. **✅ Futuro-proof** - Base para web/mobile dashboards (v0.4+)
4. **✅ Mantenible** - Código TypeScript type-safe
5. **✅ Rendimiento** - 60 FPS garantizado en animaciones

**Brain GUI abrirá:**
- Ventana Qt6 (container)
- Angular app embebida (http://localhost:8765)
- Backend FastAPI corriendo en background
- WebSocket actualizando proyectos cada 10s
- Gráficos ECG suaves sin tirones

---

**FIN DEL PLAN DE MIGRACIÓN**

**Siguiente paso:** Implementar FASE 1 (Backend FastAPI)
