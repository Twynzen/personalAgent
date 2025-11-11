# 🔬 INVESTIGACIÓN: Control de Terminales Claude Code desde Sendell

**Investigador:** Daniel
**Fecha:** 2025-11-10
**Sistema Operativo:** Windows 10/11 (prioritario)
**Versión del Documento:** 2.0 - Contextualizado

---

## 🎯 CONTEXTO DEL PROYECTO

### ¿Qué es Sendell?

**Sendell** es tu asistente personal AI que orquesta y gestiona múltiples proyectos de desarrollo en tu máquina Windows. Piensa en Sendell como un "gerente de proyectos autónomo" que:

- Monitorea todos tus proyectos VS Code abiertos
- Detecta errores en terminales automáticamente
- Coordina trabajo entre múltiples sesiones de Claude Code
- Te muestra un dashboard visual con estado de cada proyecto
- Puede delegar tareas a Claude Code de forma inteligente

### El Dashboard Actual (Angular + FastAPI)

Ya tienes implementado:
- ✅ **Dashboard cyberpunk** que muestra proyectos detectados con psutil
- ✅ **Gráficos de actividad animados** con 3 estados:
  - 🔴 RED (offline): VS Code abierto, sin Claude terminal activo
  - 🔵 BLUE (idle): Claude terminal iniciado, esperando comandos
  - 🟢 GREEN (running): Claude activamente trabajando

Lo que **NO tienes** (y es el objetivo de esta investigación):
- ❌ Forma de **abrir** Claude terminal en un proyecto desde el dashboard
- ❌ Forma de **enviar comandos** a Claude desde Sendell
- ❌ Forma de **leer el output** que Claude va escribiendo
- ❌ Forma de **detectar estado real** (idle/running/waiting) de Claude

### Visión del Usuario Final

**Escenario ideal:**

1. Abres Sendell Dashboard en tu navegador
2. Ves lista de proyectos VS Code abiertos
3. Proyecto "sendell" tiene estado 🔴 OFFLINE (sin Claude)
4. Haces click en botón "▶ Start Claude Terminal"
5. 💥 Se abre terminal en VS Code, ejecuta `claude` automáticamente
6. Dashboard cambia a 🔵 IDLE (esperando comando)
7. Escribes en dashboard: "Fix the login bug in auth.py"
8. 💥 Sendell envía ese comando a Claude
9. Dashboard cambia a 🟢 RUNNING (detecta que Claude está trabajando)
10. Ves en tiempo real qué archivos está editando Claude
11. Claude termina → Dashboard vuelve a 🔵 IDLE

**Este es el flujo completo que queremos lograr.**

---

## 🎯 OBJETIVOS DE ESTA INVESTIGACIÓN

### Objetivo Principal

**Determinar la forma MÁS CONFIABLE de controlar terminales Claude Code desde Python en Windows**, con foco en:

1. **Control automatizado completo** (abrir → enviar → capturar → monitorear)
2. **Confiabilidad >90%** (no puede fallar aleatoriamente)
3. **No invasivo** (no debe interrumpir tu trabajo si estás usando Claude manualmente)
4. **Windows-first** (soporte para Windows 10/11 es lo prioritario)

### Casos de Uso Priorizados

**PRIORIDAD 1 (Must-have):**
- Abrir terminal Claude en proyecto específico desde Python
- Enviar comando de texto a terminal existente
- Detectar si Claude está activo en un terminal

**PRIORIDAD 2 (Should-have):**
- Capturar output de Claude en tiempo real
- Detectar estado de Claude (idle/running/waiting)

**PRIORIDAD 3 (Nice-to-have):**
- Cerrar terminal Claude programáticamente
- Pausar/resumir ejecución de Claude
- Gestionar múltiples Claude sessions simultáneas

### ¿Por qué esta investigación?

**Sendell necesita ser un "orquestador inteligente"**, no solo un monitor pasivo.

Imagina que tienes 4 proyectos abiertos:
- Proyecto A: Error de compilación → Sendell detecta y delega a Claude A: "Fix compilation error"
- Proyecto B: Tests fallando → Sendell delega a Claude B: "Fix failing tests"
- Proyecto C: Idle → Sendell no hace nada
- Proyecto D: Tu trabajando manualmente → Sendell solo observa

**Para lograr esto, Sendell DEBE poder controlar terminales Claude.**

---

## 🖥️ ESPECIFICACIONES TÉCNICAS

### Sistema Operativo

- **Principal:** Windows 10/11 (x64)
- **Terminal por defecto:** PowerShell 7+ o Windows Terminal
- **VS Code:** Última versión estable (1.95+)
- **Claude Code:** Instalado globalmente (`npm install -g @anthropics/claude-code`)

### Stack de Sendell

**Backend (Python 3.10+):**
- FastAPI (web server en puerto 8765)
- psutil (detección de procesos VS Code)
- asyncio (operaciones asíncronas)

**Frontend (Angular 20):**
- Dashboard en `http://localhost:8765`
- WebSocket para updates en tiempo real
- Canvas API para gráficos de actividad

### Restricciones Técnicas

**DEBE:**
- ✅ Funcionar en Windows 10/11 sin permisos de admin
- ✅ Ser confiable (>90% success rate)
- ✅ No interrumpir trabajo manual del usuario
- ✅ Soportar múltiples VS Code instances simultáneas

**NO DEBE:**
- ❌ Requerir instalación de software adicional complejo
- ❌ Usar técnicas "hacky" poco confiables (ej: screen scraping)
- ❌ Depender de APIs inestables o no documentadas
- ❌ Fallar silenciosamente (errors deben ser detectables)

---

## 📋 INVESTIGACIÓN 1: Abrir Terminal Claude Code Programáticamente

### 🎯 Objetivo Específico

**Desde Python, abrir un nuevo terminal en VS Code con `claude` ya ejecutándose.**

**Input esperado:**
```python
sendell.open_claude_terminal(
    project_path="C:\\Users\\Daniel\\Projects\\sendell",
    project_name="sendell"
)
```

**Output esperado:**
- Terminal nuevo aparece en VS Code del proyecto especificado
- Comando `claude` se ejecuta automáticamente
- Función retorna success/error
- (Bonus) Retorna ID o PID del terminal para referencia futura

---

### 🧪 Opción A: VS Code CLI (`code` command)

**Hipótesis:** VS Code CLI tiene comandos para manipular terminales.

#### Experimentos a Realizar

**Paso 1: Explorar comandos disponibles**
```powershell
# Ver todos los comandos disponibles
code --help

# Buscar específicamente comandos relacionados con terminal
code --help | Select-String -Pattern "terminal"

# Buscar comandos de ejecución
code --help | Select-String -Pattern "execute|run|command"
```

**Paso 2: Probar abrir proyecto**
```powershell
# Abrir VS Code en proyecto específico
code "C:\Users\Daniel\Projects\sendell"

# ¿Abre en ventana nueva o usa ventana existente?
code --new-window "C:\Users\Daniel\Projects\sendell"
```

**Paso 3: Probar comandos de terminal (si existen)**
```powershell
# ¿Existe algo así?
code --command "workbench.action.terminal.new"

# ¿Se puede enviar texto al terminal?
code --command "workbench.action.terminal.sendSequence" --args '{"text":"claude\n"}'

# ¿Hay flag para ejecutar comando directamente?
code --execute "claude"
```

#### Script de Prueba Python

```python
import subprocess
import time

def test_vscode_cli():
    """Prueba abrir VS Code y ejecutar comando en terminal"""

    project_path = r"C:\Users\Daniel\Projects\sendell"

    # Paso 1: Abrir VS Code
    print(f"[1/3] Abriendo VS Code en {project_path}...")
    result = subprocess.run(
        ['code', project_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False

    print("✅ VS Code abierto")
    time.sleep(3)  # Esperar que VS Code cargue

    # Paso 2: Intentar abrir terminal
    print("[2/3] Intentando abrir terminal...")
    result = subprocess.run(
        ['code', '--command', 'workbench.action.terminal.new'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"⚠️ Comando no funcionó: {result.stderr}")
    else:
        print("✅ Comando aceptado")

    time.sleep(2)

    # Paso 3: Intentar enviar texto
    print("[3/3] Intentando ejecutar 'claude'...")
    # Aquí probar diferentes variaciones que encuentres

    return True

if __name__ == "__main__":
    test_vscode_cli()
```

#### Documentar Findings

**Comandos que funcionan:**
```
[Lista aquí cada comando que probaste y funcionó]
Ejemplo:
✅ code <path> - Abre VS Code en proyecto
✅ code --new-window <path> - Abre en ventana nueva
❌ code --command ... - No funciona / no existe
```

**Pros de este método:**
- [ ] Simple de implementar
- [ ] Confiable
- [ ] No requiere dependencias adicionales
- [ ] Soporta múltiples VS Code instances
- [ ] Otro: ___________

**Contras de este método:**
- [ ] No funciona para enviar comandos
- [ ] No permite control granular
- [ ] Timing issues (esperar que VS Code cargue)
- [ ] Otro: ___________

**Código Python funcional (si aplica):**
```python
# Si encontraste una forma que funciona, escribe código completo aquí
def open_claude_terminal_cli(project_path: str) -> bool:
    # Tu implementación
    pass
```

---

### 🧪 Opción B: VS Code Extension Privada

**Hipótesis:** Crear extensión TypeScript que exponga comando custom para Sendell.

#### ¿Por qué una Extensión?

Si la CLI no funciona, una extensión te da **control total**:
- Acceso a APIs completas de VS Code
- Puede crear/controlar terminales programáticamente
- Puede comunicarse con Sendell vía WebSocket o HTTP
- Es la forma "oficial" de extender VS Code

#### Arquitectura Propuesta

```
Sendell Python Backend (port 8765)
        ↕ HTTP REST API
VS Code Extension (TypeScript)
        ↕ VS Code Extension API
    Terminal Claude Code
```

#### Código TypeScript de Ejemplo

```typescript
// extension.ts
import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {

    // Comando 1: Abrir Claude terminal en proyecto activo
    let openClaudeCmd = vscode.commands.registerCommand(
        'sendell.openClaudeTerminal',
        async () => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace open');
                return;
            }

            // Crear terminal con Claude
            const terminal = vscode.window.createTerminal({
                name: 'Claude Code (Sendell)',
                cwd: workspaceFolder.uri.fsPath
            });

            terminal.show();
            terminal.sendText('claude');

            // Notificar a Sendell que terminal fue creado
            try {
                await axios.post('http://localhost:8765/api/terminal/opened', {
                    project: workspaceFolder.name,
                    terminalId: terminal.processId
                });
            } catch (error) {
                console.error('Failed to notify Sendell:', error);
            }
        }
    );

    context.subscriptions.push(openClaudeCmd);

    // Comando 2: Enviar texto a terminal Claude activo
    let sendTextCmd = vscode.commands.registerCommand(
        'sendell.sendToClaudeTerminal',
        async (text: string) => {
            // Buscar terminal de Claude
            const claudeTerminal = vscode.window.terminals.find(
                t => t.name.includes('Claude Code')
            );

            if (!claudeTerminal) {
                vscode.window.showErrorMessage('Claude terminal not found');
                return;
            }

            claudeTerminal.show();
            claudeTerminal.sendText(text);
        }
    );

    context.subscriptions.push(sendTextCmd);
}
```

#### Cómo Llamar desde Python

```python
import subprocess

# Opción 1: Via VS Code CLI (ejecuta comando de extensión)
def open_claude_via_extension(project_path: str):
    subprocess.run([
        'code',
        project_path,
        '--command', 'sendell.openClaudeTerminal'
    ])

# Opción 2: Via HTTP (extensión tiene web server)
import requests

def send_command_via_extension(project_name: str, command: str):
    response = requests.post('http://localhost:7777/execute', json={
        'project': project_name,
        'command': command
    })
    return response.json()
```

#### Experimentos a Realizar

**Paso 1: Verificar si vale la pena**
```powershell
# ¿La Opción A (CLI) no funcionó?
# ¿Necesitas control más granular?
# ¿Estás dispuesto a mantener una extensión?
```

**Paso 2: Crear extensión scaffold básica**
```bash
npm install -g yo generator-code
yo code  # Seleccionar "New Extension (TypeScript)"
```

**Paso 3: Probar API de Terminal**
```typescript
// Probar crear terminal
const terminal = vscode.window.createTerminal({ name: 'Test' });
terminal.show();
terminal.sendText('echo Hello');
```

#### Documentar Findings

**¿Es necesaria una extensión?**
- [ ] Sí, porque CLI no puede enviar comandos a terminal
- [ ] Sí, porque necesito detectar output en tiempo real
- [ ] No, porque CLI es suficiente
- [ ] Tal vez, depende de Opción C (automatización)

**Complejidad estimada:**
- [ ] Baja (2-3 horas setup + desarrollo)
- [ ] Media (1 día completo)
- [ ] Alta (varios días)

**Pros:**
- Control total de terminales
- Acceso a todas las APIs de VS Code
- Puede detectar cambios en archivos, git, etc.
- Comunicación bidireccional con Sendell

**Contras:**
- Requiere aprender VS Code Extension API
- Mantenimiento adicional
- Debugging más complejo
- Requiere packaging (.vsix) y distribución

---

### 🧪 Opción C: Automatización con Pyautogui/Keyboard

**Hipótesis:** Simular teclado para abrir terminal y escribir comando.

⚠️ **ADVERTENCIA:** Este método es "hacky" y debe ser **ÚLTIMA OPCIÓN** si A y B no funcionan.

#### ¿Cuándo Usar Este Método?

Úsalo SOLO si:
- ❌ VS Code CLI no tiene forma de enviar comandos a terminal
- ❌ No quieres crear/mantener una extensión
- ✅ Estás dispuesto a aceptar confiabilidad ~70-80%
- ✅ No te molesta que sea un poco lento (2-3 segundos)

#### Código de Ejemplo

```python
import subprocess
import time
import pyautogui
import win32gui
import win32con

def open_claude_terminal_automation(project_path: str, project_name: str):
    """
    Método hacky: automatización de teclado
    Confiabilidad estimada: 70-80%
    """

    # Paso 1: Abrir VS Code en proyecto
    print(f"[1/5] Abriendo VS Code en {project_path}...")
    subprocess.Popen(['code', project_path])
    time.sleep(3)  # Esperar que VS Code cargue

    # Paso 2: Encontrar ventana de VS Code
    print("[2/5] Buscando ventana de VS Code...")
    def find_vscode_window():
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if project_name in title and 'Visual Studio Code' in title:
                    windows.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)
        return windows[0] if windows else None

    vscode_hwnd = find_vscode_window()
    if not vscode_hwnd:
        print("❌ No se encontró ventana de VS Code")
        return False

    # Paso 3: Traer ventana al frente
    print("[3/5] Activando ventana...")
    win32gui.ShowWindow(vscode_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(vscode_hwnd)
    time.sleep(0.5)

    # Paso 4: Abrir terminal con Ctrl+Shift+`
    print("[4/5] Abriendo terminal...")
    pyautogui.hotkey('ctrl', 'shift', '`')
    time.sleep(1)

    # Paso 5: Escribir 'claude' y Enter
    print("[5/5] Ejecutando 'claude'...")
    pyautogui.write('claude', interval=0.05)
    pyautogui.press('enter')

    print("✅ Completado")
    return True
```

#### Dependencias Necesarias

```powershell
pip install pyautogui pywin32
```

#### Experimentos a Realizar

**Paso 1: Probar detección de ventana**
```python
# ¿Puedes encontrar la ventana correcta de VS Code?
# ¿Funciona con múltiples VS Code abiertos?
# ¿Qué pasa si VS Code está minimizado?
```

**Paso 2: Probar activación de ventana**
```python
# ¿SetForegroundWindow funciona siempre?
# ¿Qué pasa si usuario está usando mouse?
```

**Paso 3: Probar timing**
```python
# ¿3 segundos es suficiente para que VS Code cargue?
# ¿Qué pasa con máquinas lentas?
# ¿Necesitas esperar más en HDDs vs SSDs?
```

**Paso 4: Probar confiabilidad**
```python
# Ejecuta el script 10 veces seguidas
# ¿Cuántas veces funciona correctamente?
# ¿En qué casos falla?
```

#### Documentar Findings

**Tasa de éxito:**
- [ ] Alta (9-10/10 veces funciona)
- [ ] Media (7-8/10 veces funciona)
- [ ] Baja (<6/10 veces funciona)

**Casos de fallo detectados:**
```
[Lista aquí cada vez que falló y por qué]
Ejemplo:
❌ Falló porque usuario movió mouse durante ejecución
❌ Falló porque VS Code tardó más de 3 segundos en abrir
❌ Falló porque había múltiples ventanas VS Code
```

**Timing óptimo encontrado:**
```python
VS_CODE_OPEN_DELAY = 3  # segundos
WINDOW_ACTIVATION_DELAY = 0.5  # segundos
TERMINAL_OPEN_DELAY = 1  # segundos
COMMAND_TYPE_INTERVAL = 0.05  # segundos entre teclas
```

**Código funcional final (si aplica):**
```python
# Tu versión mejorada del código de automatización
def open_claude_terminal_automation_v2(project_path: str, project_name: str):
    # Con todos los ajustes y mejoras que descubriste
    pass
```

---

### 📊 Comparación de Opciones (Completa al terminar)

| Criterio | Opción A (CLI) | Opción B (Extension) | Opción C (Automation) |
|----------|----------------|----------------------|-----------------------|
| Confiabilidad | ? % | ? % | ? % |
| Velocidad | ? segundos | ? segundos | ? segundos |
| Complejidad | ? | ? | ? |
| Mantenimiento | ? | ? | ? |
| Soporte multi-window | ? | ? | ? |
| **RECOMENDADO** | ? | ? | ? |

**Método seleccionado:** [Escribe aquí cuál elegiste y por qué]

---

## 📋 INVESTIGACIÓN 2: Detectar Terminal Claude Code

### 🎯 Objetivo Específico

**Identificar QUÉ terminales de VS Code están ejecutando Claude Code actualmente.**

**Input esperado:**
```python
sendell.find_claude_terminals()
```

**Output esperado:**
```python
[
    {
        'pid': 12345,
        'project_path': 'C:\\Users\\Daniel\\Projects\\sendell',
        'project_name': 'sendell',
        'terminal_name': 'Claude Code (Sendell)',
        'status': 'idle'  # o 'running', 'waiting'
    },
    {
        'pid': 67890,
        'project_path': 'C:\\Users\\Daniel\\Projects\\myapp',
        'project_name': 'myapp',
        'terminal_name': 'powershell',
        'status': 'running'
    }
]
```

---

### 🧪 Método 1: Detección con psutil (Process Tree)

**Hipótesis:** Claude Code es un proceso hijo de los terminales de VS Code.

#### Árbol de Procesos Típico en Windows

```
Code.exe (VS Code principal)
├── Code.exe (GPU Process)
├── Code.exe (Extension Host)
└── WindowsTerminal.exe o powershell.exe
    └── node.exe (Claude Code CLI)
        └── claude.exe
```

#### Script de Detección

```python
import psutil
from pathlib import Path

def find_claude_processes():
    """
    Busca procesos de Claude Code y mapea a proyectos
    """
    claude_sessions = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid', 'cwd']):
        try:
            info = proc.info
            name = info['name'].lower()
            cmdline = ' '.join(info.get('cmdline', [])).lower()

            # ¿Es proceso relacionado con Claude?
            is_claude = (
                'claude' in name or
                'claude' in cmdline
            )

            if not is_claude:
                continue

            # Intentar obtener información del proceso
            try:
                cwd = proc.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cwd = None

            # Buscar proceso padre (terminal)
            parent_pid = info.get('ppid')
            parent_name = None
            parent_cwd = None

            if parent_pid:
                try:
                    parent = psutil.Process(parent_pid)
                    parent_name = parent.name()
                    parent_cwd = parent.cwd()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Construir sesión
            session = {
                'pid': info['pid'],
                'name': info['name'],
                'cmdline': info.get('cmdline', []),
                'cwd': cwd or parent_cwd,
                'parent_pid': parent_pid,
                'parent_name': parent_name
            }

            claude_sessions.append(session)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return claude_sessions

# Prueba esto con Claude Code abierto
if __name__ == "__main__":
    sessions = find_claude_processes()

    print(f"Encontradas {len(sessions)} sesiones de Claude Code:\n")

    for i, session in enumerate(sessions, 1):
        print(f"Sesión {i}:")
        print(f"  PID: {session['pid']}")
        print(f"  Nombre: {session['name']}")
        print(f"  CWD: {session['cwd']}")
        print(f"  Parent: {session['parent_name']} (PID {session['parent_pid']})")
        print(f"  Cmdline: {' '.join(session['cmdline'][:3])}...")
        print()
```

#### Experimentos a Realizar

**Paso 1: Abrir Claude en proyecto conocido**
```powershell
cd C:\Users\Daniel\Projects\sendell
claude
```

**Paso 2: Ejecutar script de detección**
```powershell
python detect_claude.py
```

**Paso 3: Documentar output**
```
[Copia aquí el output completo del script]
```

#### Preguntas a Responder

**1. ¿Qué procesos detecta?**
```
[Lista los nombres de procesos encontrados]
Ejemplo:
- node.exe
- claude.exe
- powershell.exe
```

**2. ¿Puedes obtener el CWD (directorio de trabajo)?**
- [ ] Sí, siempre
- [ ] Sí, a veces (depende de permisos)
- [ ] No, nunca

**3. ¿El CWD corresponde al proyecto correcto?**
- [ ] Sí, muestra `C:\Users\Daniel\Projects\sendell`
- [ ] No, muestra otra ruta
- [ ] Depende (especificar de qué)

**4. ¿Puedes identificar el proceso padre (terminal)?**
- [ ] Sí, es `powershell.exe`
- [ ] Sí, es `WindowsTerminal.exe`
- [ ] Sí, es `Code.exe`
- [ ] No puedo identificarlo

**5. ¿Funciona con múltiples Claude sessions?**
- [ ] Sí, detecta todas correctamente
- [ ] Sí, pero hay ambigüedad en mapeo a proyecto
- [ ] No, solo detecta una

---

### 🧪 Método 2: Detección con Window Title (Win32 API)

**Hipótesis:** VS Code incluye información del terminal en el título de ventana.

#### Script de Detección

```python
import win32gui
import win32process
import psutil

def find_vscode_windows():
    """
    Busca ventanas de VS Code y extrae info de terminales
    """
    vscode_windows = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)

        # ¿Es ventana de VS Code?
        if 'Visual Studio Code' not in title:
            return True

        # Obtener PID de la ventana
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # Extraer información del título
        # Ejemplo: "myproject - Visual Studio Code"
        # Ejemplo: "myfile.py - myproject - Visual Studio Code"

        vscode_windows.append({
            'hwnd': hwnd,
            'title': title,
            'pid': pid
        })

        return True

    win32gui.EnumWindows(callback, None)
    return vscode_windows

def analyze_vscode_terminals():
    """
    Analiza qué terminales están activos en cada VS Code
    """
    windows = find_vscode_windows()

    for window in windows:
        print(f"VS Code Window:")
        print(f"  Title: {window['title']}")
        print(f"  PID: {window['pid']}")

        # ¿El título menciona Claude?
        if 'claude' in window['title'].lower():
            print(f"  ✅ CLAUDE DETECTED in title")

        # Buscar procesos hijos
        try:
            parent = psutil.Process(window['pid'])
            children = parent.children(recursive=True)

            print(f"  Child processes ({len(children)}):")
            for child in children:
                print(f"    - {child.name()} (PID {child.pid})")
                if 'claude' in child.name().lower():
                    print(f"      ✅ CLAUDE PROCESS")
        except psutil.NoSuchProcess:
            print(f"  ⚠️ Process no longer exists")

        print()

if __name__ == "__main__":
    analyze_vscode_terminals()
```

#### Experimentos a Realizar

**Paso 1: Abrir VS Code con Claude**
```powershell
# Terminal 1
cd C:\Users\Daniel\Projects\sendell
code .
# Abrir terminal integrado, ejecutar: claude

# Terminal 2 (en otro proyecto)
cd C:\Users\Daniel\Projects\myapp
code .
# Abrir terminal integrado, ejecutar: npm run dev
```

**Paso 2: Ejecutar análisis**
```powershell
python analyze_windows.py
```

#### Preguntas a Responder

**1. ¿El título de ventana incluye info del terminal?**
```
[Copia aquí los títulos de ventana que viste]
Ejemplo:
"sendell - Visual Studio Code"
"sendell - claude - Visual Studio Code"
```

**2. ¿Puedes distinguir entre terminales activos?**
- [ ] Sí, el título cambia según terminal activo
- [ ] No, el título es genérico

**3. ¿Los procesos hijos incluyen Claude?**
- [ ] Sí, veo `node.exe` o `claude.exe` como hijo
- [ ] No, no aparecen como hijos directos
- [ ] Solo aparecen si el terminal está en foreground

---

### 📊 Comparación de Métodos (Completa al terminar)

| Criterio | psutil (Process Tree) | Win32 (Window Title) |
|----------|------------------------|----------------------|
| Confiabilidad | ? % | ? % |
| Info disponible | CWD, PID, cmdline | Title, PID |
| Permisos necesarios | ? | ? |
| Múltiples sessions | ? | ? |
| **RECOMENDADO** | ? | ? |

**Método seleccionado:** [Escribe aquí cuál elegiste y por qué]

---

## 📋 INVESTIGACIÓN 3: Enviar Comandos a Terminal

### 🎯 Objetivo Específico

**Enviar texto (comando) a un terminal Claude Code ya abierto.**

**Input esperado:**
```python
sendell.send_to_claude_terminal(
    project_name="sendell",
    command="Fix the login bug in auth.py"
)
```

**Output esperado:**
- Comando aparece en terminal Claude
- Claude recibe el mensaje y comienza a trabajar
- Función retorna success/error

---

### 🧪 Método 1: Via VS Code Extension (Recomendado)

**Hipótesis:** Extensión puede usar `terminal.sendText()` API.

#### Código TypeScript

```typescript
// En tu extensión VS Code
export function sendToClaudeTerminal(text: string): boolean {
    // Buscar terminal de Claude
    const claudeTerminal = vscode.window.terminals.find(
        t => t.name.includes('Claude') || t.name.includes('claude')
    );

    if (!claudeTerminal) {
        vscode.window.showErrorMessage('Claude terminal not found');
        return false;
    }

    // Activar terminal (traer al frente)
    claudeTerminal.show();

    // Enviar texto
    claudeTerminal.sendText(text, true);  // true = agregar newline

    return true;
}
```

#### Llamar desde Python

```python
import subprocess

def send_command_via_extension(project_path: str, command: str):
    """
    Requiere extensión VS Code con comando custom
    """
    # Opción 1: Via CLI (ejecutar comando de extensión)
    result = subprocess.run([
        'code',
        project_path,
        '--command', 'sendell.sendToTerminal',
        '--args', f'["{command}"]'
    ], capture_output=True, text=True)

    return result.returncode == 0

# Uso
success = send_command_via_extension(
    'C:\\Users\\Daniel\\Projects\\sendell',
    'Fix login bug'
)
```

#### Experimentos a Realizar

**Paso 1: Implementar comando en extensión**
- Ver código TypeScript de arriba
- Agregar a `extension.ts`
- Recargar extensión en VS Code

**Paso 2: Probar desde Python**
```python
# ¿El comando llega a Claude?
# ¿Claude comienza a ejecutar?
# ¿Funciona con múltiples terminales Claude?
```

#### Documentar Findings

**¿Funciona?**
- [ ] Sí, funciona perfectamente
- [ ] Sí, pero con limitaciones: ___________
- [ ] No funciona porque: ___________

**Código funcional final:**
```python
# Tu implementación que funciona
def send_to_claude(project: str, command: str):
    pass
```

---

### 🧪 Método 2: Automatización con Pyautogui (Fallback)

**Hipótesis:** Si extensión no funciona, simular teclado.

⚠️ **Solo usar si Método 1 no funciona.**

#### Script de Ejemplo

```python
import pyautogui
import win32gui
import win32con
import time

def send_via_automation(project_name: str, command: str):
    """
    Método hacky: activar ventana + escribir
    """
    # Paso 1: Encontrar ventana VS Code
    def find_window():
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if project_name in title and 'Visual Studio Code' in title:
                    windows.append(hwnd)
            return True
        win32gui.EnumWindows(callback, None)
        return windows[0] if windows else None

    hwnd = find_window()
    if not hwnd:
        return False

    # Paso 2: Activar ventana
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # Paso 3: Click en terminal (asumir que está visible)
    # Esto es MUY frágil...

    # Paso 4: Escribir comando
    pyautogui.write(command, interval=0.05)
    pyautogui.press('enter')

    return True
```

**Problemas conocidos de este método:**
- ❌ No sabe si terminal Claude está activo
- ❌ Puede escribir en lugar equivocado si terminal no está visible
- ❌ Depende de layout de ventana
- ❌ Falla si usuario mueve mouse

**Solo documentar este método si Método 1 no funcionó.**

---

## 📋 INVESTIGACIÓN 4: Capturar Output de Terminal

### 🎯 Objetivo Específico

**Leer el texto que Claude va escribiendo en el terminal en tiempo real.**

**Input esperado:**
```python
sendell.get_claude_output(project_name="sendell", lines=20)
```

**Output esperado:**
```python
{
    'project': 'sendell',
    'output': [
        "I'll help you fix the login bug.",
        "Let me read the auth.py file first.",
        "Read(auth.py)",
        "I found the issue on line 42...",
        "Edit(auth.py:42)"
    ],
    'timestamp': '2025-11-10T15:30:00'
}
```

---

### 🧪 Método 1: VS Code Extension con Shell Integration API

**Hipótesis:** VS Code tiene API para leer output de terminales.

#### Investigación Preliminar

**Documentación oficial:**
- https://code.visualstudio.com/api/references/vscode-api#Terminal
- https://code.visualstudio.com/api/references/vscode-api#TerminalShellIntegration

**APIs Relevantes:**
```typescript
// Terminal.shellIntegration
interface TerminalShellIntegration {
    // Ejecuta comando y captura output
    executeCommand(command: string): TerminalShellExecutionResult;
}

interface TerminalShellExecutionResult {
    // Stream de output
    stream: AsyncIterable<string>;
    // Exit code
    exitCode: Thenable<number | undefined>;
}
```

#### Código TypeScript de Ejemplo

```typescript
// En tu extensión
async function captureClaudeOutput(terminal: vscode.Terminal): Promise<string[]> {
    const integration = terminal.shellIntegration;

    if (!integration) {
        console.error('Shell integration not available');
        return [];
    }

    const outputLines: string[] = [];

    // Leer stream de output
    // (Requiere investigar API exacta)

    return outputLines;
}
```

#### Experimentos a Realizar

**Paso 1: Verificar disponibilidad de API**
```typescript
// En tu extensión
const terminal = vscode.window.activeTerminal;
console.log('Has shellIntegration:', !!terminal?.shellIntegration);
```

**Paso 2: Probar captura de output**
- Ejecutar comando en terminal
- Ver si puedes capturar output

#### Documentar Findings

**¿Shell Integration está disponible?**
- [ ] Sí, en VS Code versión: ___________
- [ ] No, no existe esta API
- [ ] Existe pero no funciona como esperaba

**¿Puedes capturar output?**
- [ ] Sí, en tiempo real
- [ ] Sí, pero con delay de: ___________ segundos
- [ ] No, la API no lo permite

**Código funcional (si aplica):**
```typescript
// Tu implementación que funciona
async function captureOutput(): Promise<string[]> {
    // ...
}
```

---

### 🧪 Método 2: Log File de Claude Code

**Hipótesis:** Claude Code guarda logs en algún archivo.

#### Directorios a Explorar

```powershell
# Posibles ubicaciones en Windows
$env:APPDATA\Claude\
$env:LOCALAPPDATA\Claude\
$env:USERPROFILE\.claude\
$env:USERPROFILE\.config\claude\

# Logs de VS Code
$env:APPDATA\Code\logs\
$env:USERPROFILE\.vscode\extensions\

# Temporal
$env:TEMP\claude-*
```

#### Script de Búsqueda

```python
import os
from pathlib import Path

def find_claude_logs():
    """Busca archivos de log de Claude Code"""

    search_paths = [
        Path(os.environ['APPDATA']) / 'Claude',
        Path(os.environ['LOCALAPPDATA']) / 'Claude',
        Path(os.environ['USERPROFILE']) / '.claude',
        Path(os.environ['USERPROFILE']) / '.config' / 'claude',
        Path(os.environ['APPDATA']) / 'Code' / 'logs',
        Path(os.environ['TEMP']),
    ]

    log_files = []

    for search_path in search_paths:
        if not search_path.exists():
            continue

        print(f"Searching in: {search_path}")

        # Buscar archivos .log
        for log_file in search_path.rglob('*.log'):
            print(f"  Found: {log_file.name}")
            log_files.append(log_file)

        # Buscar archivos con 'claude' en el nombre
        for file in search_path.rglob('*claude*'):
            if file.is_file() and file.suffix in ['.log', '.txt', '.json']:
                print(f"  Found: {file.name}")
                log_files.append(file)

    return log_files

if __name__ == "__main__":
    print("Buscando logs de Claude Code...\n")
    logs = find_claude_logs()

    if not logs:
        print("❌ No se encontraron archivos de log")
    else:
        print(f"\n✅ Encontrados {len(logs)} archivos")

        # Mostrar primeras líneas de cada log
        for log in logs[:3]:  # Solo primeros 3
            print(f"\n--- {log.name} ---")
            try:
                with open(log, 'r', encoding='utf-8', errors='ignore') as f:
                    print(f.read(500))  # Primeros 500 caracteres
            except Exception as e:
                print(f"Error leyendo archivo: {e}")
```

#### Experimentos a Realizar

**Paso 1: Ejecutar script de búsqueda**
```powershell
python find_logs.py
```

**Paso 2: Si encuentras logs, analizar formato**
```
[Copia aquí ejemplo de contenido del log]
```

**Paso 3: Verificar actualización en tiempo real**
```python
# Ejecutar Claude Code
# Ver si archivo de log se actualiza
# ¿Cuánto delay hay?
```

#### Documentar Findings

**¿Encontraste archivos de log?**
- [ ] Sí, ubicación: ___________
- [ ] No, Claude Code no parece guardar logs

**Si encontraste logs:**

**Formato del log:**
```
[Copia aquí ejemplo de 10-20 líneas]
```

**¿Se actualiza en tiempo real?**
- [ ] Sí, inmediatamente
- [ ] Sí, con delay de: ___________ segundos
- [ ] No, solo al cerrar Claude

**¿Es parseable?**
- [ ] Sí, formato estructurado (JSON, XML, etc.)
- [ ] Sí, pero formato custom (texto plano)
- [ ] No, formato binario o ilegible

**Código para leer logs (si aplica):**
```python
def read_claude_output_from_log(project_name: str, lines: int = 20):
    # Tu implementación
    pass
```

---

### 📊 Comparación de Métodos (Completa al terminar)

| Criterio | Shell Integration API | Log Files |
|----------|------------------------|-----------|
| Disponibilidad | ? | ? |
| Tiempo real | ? | ? |
| Confiabilidad | ? | ? |
| Complejidad | ? | ? |
| **RECOMENDADO** | ? | ? |

**Método seleccionado:** [Escribe aquí cuál elegiste y por qué]

---

## 📋 INVESTIGACIÓN 5: Detectar Estado de Claude

### 🎯 Objetivo Específico

**Saber en qué estado está Claude en tiempo real.**

**Estados posibles:**
- 🔵 `idle`: Esperando comando del usuario
- 🟢 `running`: Ejecutando tarea (escribiendo código, leyendo archivos)
- 🟡 `waiting_confirmation`: Esperando que usuario confirme acción

**Input esperado:**
```python
sendell.get_claude_state(project_name="sendell")
```

**Output esperado:**
```python
{
    'state': 'running',  # idle, running, waiting_confirmation
    'confidence': 0.95,  # 0.0 - 1.0
    'indicators': ['cpu_high', 'recent_output_contains_Edit']
}
```

---

### 🧪 Método 1: Análisis de Output (Regex Patterns)

**Hipótesis:** El texto que escribe Claude tiene patrones detectables.

#### Experimento Manual

**Paso 1: Observar output de Claude en diferentes estados**

Abre Claude Code y ejecuta varios comandos. **Copia EXACTAMENTE** lo que muestra:

**Cuando Claude está IDLE (esperando):**
```
[Copia aquí 5-10 líneas de output cuando Claude está esperando]
Ejemplo:
>
```

**Cuando Claude está RUNNING (trabajando):**
```
[Copia aquí 5-10 líneas de output cuando Claude está trabajando]
Ejemplo:
I'll help you with that.

Let me read the file first.
Read(src/auth.py)

Now I'll edit it.
Edit(src/auth.py:42)
```

**Cuando Claude está WAITING (esperando confirmación):**
```
[Copia aquí 5-10 líneas de output cuando Claude espera confirmación]
Ejemplo:
This will modify 3 files. Do you want to proceed?
[y/n]:
```

#### Patrones Regex a Desarrollar

Basándote en lo que copiaste arriba, crea patrones:

```python
import re
from typing import Literal

ClaudeState = Literal['idle', 'running', 'waiting_confirmation']

PATTERNS = {
    'idle': [
        re.compile(r'^>\s*$'),  # Prompt vacío
        re.compile(r'Ready for your next command'),
        # Agrega más patrones que viste
    ],

    'running': [
        re.compile(r'\b(Read|Write|Edit|Bash)\('),  # Tools de Claude
        re.compile(r"I'll|I'm|Let me"),  # Frases de Claude
        re.compile(r'Analyzing|Processing|Working on'),
        # Agrega más patrones que viste
    ],

    'waiting_confirmation': [
        re.compile(r'Do you want to proceed\?'),
        re.compile(r'\[y/n\]:'),
        re.compile(r'Should I continue\?'),
        # Agrega más patrones que viste
    ]
}

def detect_claude_state(recent_output: str) -> tuple[ClaudeState, float]:
    """
    Detecta estado basándose en últimas líneas de output

    Returns:
        (state, confidence)
    """
    scores = {
        'idle': 0.0,
        'running': 0.0,
        'waiting_confirmation': 0.0
    }

    # Contar matches de cada patrón
    for state, patterns in PATTERNS.items():
        for pattern in patterns:
            if pattern.search(recent_output):
                scores[state] += 1.0

    # Estado con más matches
    if sum(scores.values()) == 0:
        return ('idle', 0.5)  # Default con baja confianza

    max_state = max(scores, key=scores.get)
    confidence = scores[max_state] / sum(scores.values())

    return (max_state, confidence)
```

#### Script de Prueba

```python
# Casos de prueba con outputs reales que copiaste
test_cases = [
    {
        'output': """
>
""",
        'expected': 'idle'
    },
    {
        'output': """
I'll help you fix the login bug.

Let me read the file first.
Read(src/auth.py)
""",
        'expected': 'running'
    },
    {
        'output': """
This will modify 3 files:
- src/auth.py
- src/login.py
- tests/test_auth.py

Do you want to proceed? [y/n]:
""",
        'expected': 'waiting_confirmation'
    }
]

for i, case in enumerate(test_cases, 1):
    state, confidence = detect_claude_state(case['output'])
    correct = '✅' if state == case['expected'] else '❌'
    print(f"Test {i}: {correct} Detected={state} Expected={case['expected']} (confidence={confidence:.2f})")
```

#### Experimentos a Realizar

**Paso 1: Copiar outputs reales** (ver arriba)

**Paso 2: Desarrollar patrones regex**

**Paso 3: Probar con casos reales**
```python
# Ejecuta script de prueba
# ¿Cuántos casos detecta correctamente?
# Accuracy: ___/10
```

**Paso 4: Ajustar patrones**
```python
# Si falló algún caso, ajustar regex
# Repetir hasta tener accuracy >90%
```

#### Documentar Findings

**Patrones finales que funcionan:**
```python
PATTERNS = {
    'idle': [
        # Tus patrones
    ],
    'running': [
        # Tus patrones
    ],
    'waiting_confirmation': [
        # Tus patrones
    ]
}
```

**Accuracy conseguida:**
- [ ] Alta (>90% de casos correctos)
- [ ] Media (70-90% de casos correctos)
- [ ] Baja (<70% de casos correctos)

**Casos difíciles encontrados:**
```
[Lista aquí outputs que fueron difíciles de clasificar]
```

---

### 🧪 Método 2: CPU/Memory Usage (Complementario)

**Hipótesis:** CPU alto = Claude trabajando, CPU bajo = idle.

#### Script de Monitoreo

```python
import psutil
import time

def monitor_claude_resources(pid: int, duration: int = 10):
    """
    Monitorea CPU y memoria de proceso Claude
    """
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"❌ Proceso {pid} no existe")
        return

    print(f"Monitoreando PID {pid} por {duration} segundos...\n")
    print("Time | CPU%  | RAM(MB) | State (manual)")
    print("-" * 45)

    for i in range(duration):
        cpu = proc.cpu_percent(interval=1)
        mem = proc.memory_info().rss / 1024 / 1024  # MB

        print(f"{i+1:4d}s | {cpu:5.1f} | {mem:7.1f} | [escribe aquí qué estaba haciendo Claude]")
        time.sleep(1)

if __name__ == "__main__":
    # Encuentra PID de Claude
    for proc in psutil.process_iter(['pid', 'name']):
        if 'claude' in proc.info['name'].lower():
            print(f"Encontrado Claude: PID {proc.info['pid']}")

            # Monitorear
            monitor_claude_resources(proc.info['pid'], duration=30)
            break
```

#### Experimentos a Realizar

**Paso 1: Ejecutar monitoreo mientras usas Claude**

1. Inicia script de monitoreo
2. En Claude:
   - 10 segundos IDLE (no hacer nada)
   - 10 segundos RUNNING (pedirle algo complejo)
   - 10 segundos WAITING (pedirle confirmación y no responder)
3. En cada segundo, anota manualmente qué estaba haciendo Claude

**Paso 2: Analizar correlación**
```
[Pega aquí el output del script]
```

**Análisis:**
- CPU en IDLE: promedio ___%, rango ___-___%
- CPU en RUNNING: promedio ___%, rango ___-___%
- CPU en WAITING: promedio ___%, rango ___-___%

#### Documentar Findings

**¿CPU es indicador confiable?**
- [ ] Sí, hay clara diferencia entre estados
- [ ] Parcialmente, ayuda pero no es suficiente solo
- [ ] No, CPU es muy variable

**Umbrales sugeridos (si aplica):**
```python
CPU_IDLE_THRESHOLD = ___  # % debajo de esto = idle
CPU_RUNNING_THRESHOLD = ___  # % arriba de esto = running
```

**Código para detección híbrida (Regex + CPU):**
```python
def detect_state_hybrid(output: str, cpu_percent: float) -> ClaudeState:
    # Tu implementación combinando ambos métodos
    pass
```

---

### 📊 Método Recomendado Final

Basándote en tus experimentos, elige:

| Método | Confiabilidad | Complejidad | Speed |
|--------|---------------|-------------|-------|
| Regex solo | ? | ? | ? |
| CPU solo | ? | ? | ? |
| Híbrido | ? | ? | ? |

**Método seleccionado:** [Escribe aquí]

**Justificación:** [Por qué elegiste ese método]

**Código final implementable:**
```python
def detect_claude_state_final(
    project_name: str,
    recent_output: str = None,
    process_pid: int = None
) -> tuple[ClaudeState, float]:
    """
    Tu implementación final que realmente funciona
    """
    pass
```

---

## 📊 RESUMEN EJECUTIVO DE INVESTIGACIÓN

### Checklist de Objetivos

Al completar esta investigación, debes poder responder:

**1. Abrir Terminal Claude**
- [ ] ✅ Código funcional implementado
- [ ] ✅ Confiabilidad >90%
- [ ] ✅ Funciona con múltiples VS Code
- [ ] ✅ Tiempo de ejecución: ___ segundos

**2. Detectar Terminal Claude**
- [ ] ✅ Código funcional implementado
- [ ] ✅ Retorna PID, project path, terminal name
- [ ] ✅ Funciona con múltiples sessions
- [ ] ✅ Confiabilidad: ____%

**3. Enviar Comandos**
- [ ] ✅ Código funcional implementado
- [ ] ✅ Comando llega a Claude correctamente
- [ ] ✅ Funciona con terminales en background
- [ ] ✅ Error handling implementado

**4. Capturar Output**
- [ ] ✅ Código funcional implementado
- [ ] ✅ Lectura en tiempo real o <1s delay
- [ ] ✅ Retorna últimas N líneas
- [ ] ✅ Formato parseable

**5. Detectar Estado**
- [ ] ✅ Código funcional implementado
- [ ] ✅ Accuracy >90%
- [ ] ✅ Distingue idle/running/waiting
- [ ] ✅ Retorna confidence score

---

## 🎯 ENTREGABLES

### Documento de Resultados

Crea archivo: `TERMINAL_CONTROL_RESEARCH_RESULTS.md`

**Estructura esperada:**
```markdown
# Resultados de Investigación: Control de Terminales Claude Code

## Resumen Ejecutivo
[3-5 párrafos explicando qué funcionó y qué no]

## Método Seleccionado para Cada Objetivo

### 1. Abrir Terminal
**Método elegido:** [VS Code CLI / Extension / Automation]
**Justificación:** [Por qué]
**Código:**
```python
# Código funcional completo
```
**Limitaciones conocidas:**
- [Lista]

### 2. Detectar Terminal
[Mismo formato]

### 3. Enviar Comandos
[Mismo formato]

### 4. Capturar Output
[Mismo formato]

### 5. Detectar Estado
[Mismo formato]

## Dependencias Necesarias
```
pyautogui==0.9.54  # si aplica
pywin32==306
psutil==5.9.6
```

## Próximos Pasos para Implementación
1. [Lista de pasos para integrar en Sendell]
2. [...]

## Riesgos y Mitigaciones
- **Riesgo 1:** [Descripción]
  - **Mitigación:** [Solución]
```

### Código Funcional

Crea archivo: `sendell_terminal_controller.py`

```python
"""
Sendell Terminal Controller
Código funcional resultado de investigación
"""

# Todos los métodos funcionales que desarrollaste
```

---

## 💡 TIPS FINALES

### Durante la Investigación

1. **Documenta TODO**, incluso fallos
   - Los errores son aprendizaje valioso
   - Sendell necesita conocer limitaciones

2. **Prioriza confiabilidad sobre features**
   - Mejor 3 métodos confiables que 5 poco confiables
   - 90% confiabilidad es el mínimo aceptable

3. **Piensa en mantenimiento**
   - ¿Este método seguirá funcionando en 6 meses?
   - ¿Qué pasa si VS Code actualiza?

4. **Prueba casos edge**
   - Múltiples VS Code abiertos
   - Proyecto sin nombre claro
   - Claude Code crashea mid-execution
   - Usuario trabaja manualmente mientras Sendell monitorea

5. **No te frustres**
   - Esto es investigación exploratoria
   - Algunos métodos NO funcionarán, es normal
   - Si algo no funciona, prueba siguiente opción

### Criterios de Éxito

**Investigación exitosa si:**
- ✅ Tienes al menos 1 método confiable por objetivo
- ✅ Código funciona >90% de las veces
- ✅ Entiendes limitaciones y edge cases
- ✅ Documentaste findings claramente

**Investigación requiere más trabajo si:**
- ❌ Métodos funcionan <70% de las veces
- ❌ No estás seguro de por qué funciona/falla
- ❌ No probaste con casos reales
- ❌ Documentación incompleta

---

## 🎉 SIGUIENTE FASE

Una vez completes esta investigación, el siguiente paso será:

**Implementación en Sendell (3-4 sesiones):**

1. **Sesión 1:** Integrar detección de terminales Claude en backend
2. **Sesión 2:** Implementar control (abrir/enviar comandos)
3. **Sesión 3:** Agregar captura de output y detección de estado
4. **Sesión 4:** Actualizar dashboard para mostrar controles

**Con tu investigación completa, podremos implementar TODO esto de forma eficiente.**

---

## 📚 RECURSOS ÚTILES

### Documentación Oficial
- VS Code CLI: https://code.visualstudio.com/docs/editor/command-line
- VS Code Extension API: https://code.visualstudio.com/api
- Claude Code: https://claude.ai/code
- psutil: https://psutil.readthedocs.io/
- pywin32: https://github.com/mhammond/pywin32

### Comunidad
- VS Code Discord: https://aka.ms/vscode-discord
- Stack Overflow: Tag `visual-studio-code`

### Contacto
Si encuentras blockers críticos, documenta:
- Qué intentaste
- Qué error obtuviste
- Qué alternativas evaluaste

**Claude (yo) te ayudaré a implementar basándose en tu investigación.**

---

**¡Éxito con la investigación! 🔬🚀**
