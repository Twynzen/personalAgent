# TERMINAL ISSUES - Bug Report & Analysis

**Fecha**: 2025-11-11
**Reportado por**: Daniel
**Estado**: 🔴 CRÍTICO - Implementación incorrecta
**Archivo de evidencia**: `Captura.png`

---

## 🐛 PROBLEMAS IDENTIFICADOS

### 1. **Terminal embebida EN LUGAR DE popup modal** ❌

**Problema crítico**: La terminal se está renderizando DENTRO del flujo del dashboard (embebida), NO como un popup/modal separado.

**Evidencia en Captura.png**:
- Terminal "experimentos - Terminal1" aparece integrada en el layout
- Terminal "sendell - Terminal" también integrada
- Ambas empujan el contenido hacia abajo
- NO hay modal/overlay/popup independiente

**Comportamiento esperado** ✅:
- Click en proyecto → Modal/popup aparece SOBRE el dashboard
- Modal flotante con backdrop oscuro
- Modal con z-index alto (encima de todo)
- Posición fija/absoluta, NO en el flujo del documento

**Comportamiento actual** ❌:
- Terminal se renderiza DEBAJO del project-card
- Forma parte del flujo normal del DOM
- Empuja otros proyectos hacia abajo
- Se ve como parte integrada del dashboard

**Código problemático** (`app.html` líneas 188-197):
```html
<!-- Embedded Terminal (shown below project card) -->
@if (terminalService.isTerminalOpen(project.pid)) {
  <app-terminal
    [projectPid]="project.pid"
    [workspacePath]="project.workspace_path"
    [projectName]="project.name"
  />
}
```

**Problema**: Terminal renderizada dentro del `@for` loop de proyectos → se integra en el flujo.

---

### 2. **WebSocket error: "Terminal 16276 not found"** ❌

**Evidencia en Captura.png**:
- Terminal "experimentos" muestra múltiples errores rojos
- `[Error: Terminal 16276 not found]` repetido ~10 veces
- Ocurre después de `[Connected to terminal]`

**Análisis**:
1. Terminal Component conecta WebSocket correctamente
2. WebSocket acepta conexión (`[Connected to terminal]`)
3. Backend intenta buscar terminal con PID 16276
4. TerminalManager NO encuentra el terminal (no existe en registry)

**Causa probable**:
- Terminal fue creada pero NO registrada en TerminalManager
- O terminal fue creada con ID diferente al PID del proyecto
- O terminal se creó, murió, y WebSocket sigue conectado

**Código relevante** (`server.py` línea 85-96):
```python
terminal_manager = get_terminal_manager()
command = message.get('data', '')

try:
    terminal_manager.send_command(terminal_id, command)
except Exception as e:
    logger.error(f"Error sending command: {e}")
    await websocket.send_json({
        'type': 'error',
        'message': str(e)  # "Terminal 16276 not found"
    })
```

**Problema**: `send_command()` lanza excepción porque `terminal_id` no existe en `self.terminals` dict.

---

### 3. **Loading spinner NO se muestra** ❌

**Evidencia en Captura.png**:
- NO hay spinner visible en ninguno de los proyectos
- Click en proyecto OFFLINE debería mostrar "Opening terminal..." con spinner

**Código esperado** (`app.html` líneas 141-146):
```html
@if (loadingProjectPid() === project.pid) {
  <div class="loading-overlay">
    <div class="loading-spinner-project"></div>
    <div class="loading-text-project">Opening terminal...</div>
  </div>
}
```

**Problema posible**:
1. CSS `.loading-overlay` no está definido o está mal posicionado
2. `loadingProjectPid` signal no se está seteando correctamente
3. Timing: spinner se limpia antes de que sea visible
4. Terminal se abre tan rápido que spinner no aparece

---

### 4. **Dos terminales abiertas simultáneamente en mismo proyecto** ⚠️

**Evidencia en Captura.png**:
- Proyecto "experimentos" tiene terminal abierta
- Proyecto "sendell" TAMBIÉN tiene terminal abierta

**Análisis**:
- Esto podría ser intencional (múltiples proyectos con terminales)
- PERO si es el MISMO proyecto, es un bug

**Necesita clarificación de Daniel**:
- ¿"experimentos" y "sendell" son proyectos diferentes?
- ¿O son el mismo proyecto con 2 terminales abiertas por error?

---

## 🔧 SOLUCIONES PROPUESTAS

### Solución 1: Terminal como Modal Popup ✅

**Cambios necesarios**:

1. **Crear `TerminalModalComponent`** (nuevo componente):
```typescript
@Component({
  selector: 'app-terminal-modal',
  template: `
    <div class="modal-backdrop" (click)="closeModal()">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <app-terminal
          [projectPid]="projectPid"
          [workspacePath]="workspacePath"
          [projectName]="projectName"
        />
      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.8);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .modal-content {
      width: 90vw;
      height: 80vh;
      max-width: 1200px;
      background: #0a0a0a;
      border: 2px solid #00ff00;
      box-shadow: 0 0 40px rgba(0, 255, 0, 0.5);
      border-radius: 8px;
      overflow: hidden;
    }
  `]
})
```

2. **Modificar `app.html`** para usar modal:
```html
<!-- Remove embedded terminal from @for loop -->
<!-- Move to root level with condition -->
@if (terminalService.currentTerminalPid()) {
  <app-terminal-modal
    [projectPid]="terminalService.currentTerminalPid()!"
    [workspacePath]="getCurrentProject().workspace_path"
    [projectName]="getCurrentProject().name"
    (close)="terminalService.closeTerminal()"
  />
}
```

3. **Actualizar `TerminalService`**:
```typescript
export class TerminalService {
  private currentTerminalPid = signal<number | null>(null);

  openTerminal(pid: number) {
    this.currentTerminalPid.set(pid);
  }

  closeTerminal() {
    this.currentTerminalPid.set(null);
  }

  currentTerminalPid() {
    return this.currentTerminalPid();
  }
}
```

---

### Solución 2: Fix WebSocket "Terminal not found" ✅

**Problema root cause**: Terminal NO se registra antes de WebSocket conectar.

**Flujo actual** (INCORRECTO):
1. Click → `openTerminal()` llamado
2. Backend crea terminal (`TerminalManager.create_terminal()`)
3. **Frontend inmediatamente conecta WebSocket**
4. WebSocket intenta usar terminal que aún no existe
5. Error: "Terminal not found"

**Flujo correcto** (FIX):
1. Click → `openTerminal()` llamado
2. Backend crea terminal Y ESPERA a que esté READY
3. Backend retorna `terminal_id` + `status: "ready"`
4. **Frontend espera respuesta antes de conectar WebSocket**
5. WebSocket conecta solo cuando terminal está ready

**Cambios necesarios**:

1. **Backend `routes.py`** - Esperar a terminal ready:
```python
@router.post("/projects/open-terminal")
async def open_terminal(request: OpenTerminalRequest):
    terminal_manager = get_terminal_manager()

    terminal_id = terminal_manager.create_terminal(
        project_pid=request.project_pid,
        workspace_path=request.workspace_path,
        project_name=request.project_name
    )

    # WAIT for terminal to be ready
    terminal = terminal_manager.get_terminal(terminal_id)
    timeout = 5  # seconds
    start_time = time.time()

    while not terminal.is_running():
        if time.time() - start_time > timeout:
            raise HTTPException(500, "Terminal failed to start")
        await asyncio.sleep(0.1)

    return {
        "terminal_id": terminal_id,
        "status": "ready",  # ← GARANTIZAR que está ready
        "pid": terminal.process_pid
    }
```

2. **Frontend `app.ts`** - Esperar respuesta ANTES de conectar WebSocket:
```typescript
onProjectClick(project: Project) {
  if (project.state === 'offline') {
    this.loadingProjectPid.set(project.pid);

    this.api.openTerminal(project.workspace_path, project.pid, project.name).subscribe({
      next: (result) => {
        // WAIT for backend confirmation before opening modal
        if (result.status === 'ready') {
          // NOW open terminal modal (WebSocket conectará DESPUÉS)
          this.terminalService.openTerminal(project.pid);
          this.loadingProjectPid.set(null);
        }
      },
      error: (err) => {
        console.error('Error creating terminal:', err);
        this.loadingProjectPid.set(null);
      }
    });
  }
}
```

---

### Solución 3: Fix Loading Spinner ✅

**Problema**: CSS no está correctamente definido o posicionado.

**Cambios necesarios en `app.scss`**:

```scss
.project-card {
  position: relative; // ← CRÍTICO para que loading-overlay funcione

  &.loading {
    pointer-events: none;
    opacity: 0.6;
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner-project {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 255, 0, 0.2);
  border-top: 4px solid #00ff00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text-project {
  margin-top: 1rem;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## 📋 PLAN DE ACCIÓN

### Prioridad 1 (CRÍTICO) 🔴
1. ✅ Implementar terminal como modal popup (Solución 1)
2. ✅ Fix WebSocket timing issue (Solución 2)

### Prioridad 2 (ALTA) 🟡
3. ✅ Fix loading spinner CSS (Solución 3)
4. ✅ Testing end-to-end completo

### Prioridad 3 (MEDIA) 🟢
5. ⏳ Cleanup: Remover terminal embebida del flujo
6. ⏳ Agregar close button funcional en modal
7. ⏳ Keyboard shortcuts (ESC para cerrar modal)

---

## 🧪 TESTING CHECKLIST

Después de implementar soluciones:

- [ ] Click en proyecto OFFLINE → Modal aparece SOBRE dashboard
- [ ] Modal tiene backdrop oscuro
- [ ] Click fuera de modal → cierra modal
- [ ] Botón X → cierra modal
- [ ] WebSocket conecta DESPUÉS de terminal ready
- [ ] NO más errores "Terminal not found"
- [ ] Loading spinner visible durante creación
- [ ] Spinner desaparece cuando modal abre
- [ ] Terminal funciona: `dir`, `npm install`, etc.
- [ ] Múltiples proyectos pueden tener modales (uno a la vez)

---

## 📝 NOTAS ADICIONALES

**Decisión de diseño**:
- UN modal a la vez (no múltiples modales simultáneos)
- Modal cubre toda la pantalla con backdrop
- ESC key para cerrar modal (agregar en v0.4)

**Performance**:
- Modal con lazy loading (solo renderizar cuando abierto)
- WebSocket cierra cuando modal cierra
- Terminal process sigue vivo en backend (no matar al cerrar modal)

**UX**:
- Animación smooth al abrir/cerrar modal (opcional)
- Focus trap dentro de modal (accesibilidad)
- Backdrop click para cerrar (intuitivo)

---

**Próximos pasos**:
1. Implementar Soluciones 1-3
2. Testing exhaustivo
3. Commit cuando funcione 100%

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
