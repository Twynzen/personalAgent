# GUÍA DE TESTING FASE 6 - ESPAÑOL
# Sistema de Gestión Multi-Terminal Nivel Producción para VS Code

**Fecha**: 2025-11-04
**Base**: guidefase6refactorultraterminals.txt (investigación de 18,000 palabras)
**Implementación**: 5 Branches (~1,720 líneas de código)
**Dependencias**: 6 nuevas librerías NPM

---

## 📋 RESUMEN EJECUTIVO

Implementé un sistema de monitoreo de terminales y proyectos basado en tu investigación. Las 5 ramas completan el sistema descrito en `guidefase6refactorultraterminals.txt`:

| Branch | Qué hace | Implementé basándome en (tu investigación) |
|--------|----------|-------------------|
| **1. WebSocket Client** | Reconexión exponencial, heartbeat, cola de mensajes | Sección: "VS Code extension architecture enables reliable WebSocket coordination" |
| **2. Shell Integration** | API v1.93+ para ejecutar comandos y capturar output | Sección: "Shell Integration v1.93+ revolutionizes terminal command execution" |
| **3. Process & Port** | Detecta procesos hijo con pidtree, puertos con tcp-port-used | Sección: "Process enumeration and port detection require platform-specific approaches" |
| **4. Project Intelligence** | Auto-detecta tipo de proyecto (Node/Python/Rust/Go/etc.) | Sección: "Project detection algorithms must handle monorepos and framework diversity" |
| **5. Multi-Instance** | Coordinación entre ventanas VS Code con proper-lockfile | Sección: "File-based coordination with proper-lockfile handles multi-instance synchronization" |

---

## 🔍 VERIFICACIÓN: ¿Implementé lo correcto?

### ✅ Checklist contra tu investigación:

**WebSocket (tu investigación especificaba)**:
- ✅ Exponential backoff 1s → 60s cap
- ✅ Heartbeat cada 30s, timeout 35s
- ✅ Message queue máx 1000 mensajes
- ✅ Jitter 0-1000ms para evitar thundering herd

**Shell Integration (tu investigación especificaba)**:
- ✅ Usar executeCommand() en vez de sendText()
- ✅ Capturar output con execution.read()
- ✅ Strip ANSI codes con strip-ansi
- ✅ Fallback a sendText() si Shell Integration no disponible

**Process Detection (tu investigación especificaba)**:
- ✅ pidtree para jerarquía de procesos
- ✅ ps-list para info detallada
- ✅ tcp-port-used para detectar puertos
- ✅ Cache 5-10s TTL

**Project Intelligence (tu investigación especificaba)**:
- ✅ Detectar package.json → Node.js
- ✅ Detectar pyproject.toml → Python
- ✅ Detectar Cargo.toml → Rust
- ✅ Parsear scripts (prioridad: dev > start > serve)
- ✅ Extraer puertos de scripts con regex

**Multi-Instance (tu investigación especificaba)**:
- ✅ proper-lockfile con mkdir() atómico
- ✅ Stale timeout 10s, update 5s
- ✅ Coordination.json compartido

**Respuesta**: ✅ **SÍ, implementé TODO lo que investigaste**.

---

## 🚀 CÓMO TESTEAR (Paso a Paso en Español)

### PASO 1: PRE-REQUISITOS

Verifica que tengas:

```bash
# Node.js y NPM
node --version   # Debe ser v16+ o superior
npm --version    # Debe ser v8+ o superior

# Python (para Sendell server)
python --version # Debe ser 3.10+

# VS Code
code --version   # Debe ser 1.93.0 o superior (CRÍTICO para Shell Integration)
```

**⚠️ IMPORTANTE - Terminal en Windows**:
- ✅ **PowerShell** - Shell Integration FUNCIONA
- ✅ **Git Bash** - Shell Integration FUNCIONA
- ❌ **CMD (cmd.exe)** - Shell Integration NO FUNCIONA (tu doc lo menciona)

Cambia tu terminal por defecto en VS Code si usas CMD:
1. Ctrl+Shift+P → "Terminal: Select Default Profile"
2. Elige "PowerShell" o "Git Bash"

---

### PASO 2: INSTALACIÓN

Abre terminal en la carpeta de la extensión:

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell\sendell-vscode-extension
```

**Limpiar instalación previa** (opcional pero recomendado):
```bash
rm -rf node_modules
rm package-lock.json
```

**Instalar dependencias**:
```bash
npm install
```

**Verificar que se instalaron las 6 nuevas librerías**:
```bash
npm list strip-ansi pidtree ps-list tcp-port-used proper-lockfile
```

Debes ver:
```
sendell-extension@0.3.0
├── strip-ansi@7.1.0
├── pidtree@0.6.0
├── ps-list@8.1.1
├── tcp-port-used@1.0.2
└── proper-lockfile@4.1.2
```

**Compilar TypeScript**:
```bash
npm run compile
```

Debe compilar sin errores. Verifica que se creó `out/`:
```bash
ls out/
```

Debes ver archivos `.js` generados.

---

### PASO 3: VERIFICAR INTEGRIDAD

**3.1 Estructura de archivos**:
```bash
# Verifica que existan los 5 nuevos/modificados archivos
ls src/websocket.ts     # Modificado - Branch 1
ls src/terminal.ts      # Modificado - Branch 2
ls src/process.ts       # NUEVO - Branch 3
ls src/project.ts       # NUEVO - Branch 4
ls src/coordination.ts  # NUEVO - Branch 5
```

**3.2 Contar líneas** (aproximado):
```bash
# PowerShell
(Get-Content src/process.ts).Count       # ~420 líneas
(Get-Content src/project.ts).Count       # ~540 líneas
(Get-Content src/coordination.ts).Count  # ~410 líneas
```

**3.3 Verificar imports** (buscar strip-ansi en terminal.ts):
```bash
grep "strip-ansi" src/terminal.ts
```

Debe aparecer: `import stripAnsi from 'strip-ansi';`

---

### PASO 4: ABRIR EN MODO DEBUG

**4.1 Abrir extensión en VS Code**:
```bash
code .
```

**4.2 Presiona F5** (o Run → Start Debugging)

Debe abrirse una **nueva ventana de VS Code** con título:
```
[Extension Development Host]
```

**4.3 Verificar logs**:

En la ventana original (donde presionaste F5):
- Ve a **Output** panel (Ctrl+Shift+U)
- Selecciona "Sendell Extension" en el dropdown

Debes ver:
```
[INFO] Sendell extension activated
[INFO] WebSocket connecting to ws://localhost:7000...
```

---

### PASO 5: INICIAR SERVIDOR PYTHON

Abre terminal en la carpeta raíz del proyecto Sendell:

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
```

**Inicia el servidor WebSocket** (usa el comando que tengas configurado):
```bash
# Ejemplo (ajusta según tu setup):
uv run python -m sendell start
```

**Verifica conexión**:

En los logs de la extensión (Output panel), debes ver:
```
[INFO] WebSocket connected!
[INFO] Heartbeat started (ping every 30s)
```

---

## 🧪 TESTS FUNCIONALES (13 Tests)

### TEST 1: WebSocket Heartbeat (30s ping)

**Qué probar**: Sistema de heartbeat según tu investigación (ping 30s, pong 35s)

**Pasos**:
1. Extensión conectada al servidor (Test 5 completado)
2. Deja la conexión abierta por **2 minutos**
3. Observa los logs

**Resultado esperado**:
```
[DEBUG] Sending ping to server
[DEBUG] Pong received from server
... (cada 30 segundos)
```

**Si falla**: El WebSocket se desconecta por timeout.

---

### TEST 2: Exponential Backoff (1s → 60s)

**Qué probar**: Reconexión con backoff exponencial como especificas en tu doc

**Pasos**:
1. Detén el servidor Python (Ctrl+C)
2. Observa los logs de la extensión

**Resultado esperado**:
```
[INFO] WebSocket closed (code: 1006)
[INFO] Scheduling reconnect attempt 1/10 in 1000ms (base: 1000ms, jitter: 234ms)
[WARN] WebSocket connection failed
[INFO] Scheduling reconnect attempt 2/10 in 2567ms (base: 2000ms, jitter: 567ms)
[WARN] WebSocket connection failed
[INFO] Scheduling reconnect attempt 3/10 in 4891ms (base: 4000ms, jitter: 891ms)
... (delay aumenta: 8s, 16s, 32s, 60s cap)
```

**Verifica**:
- ✅ Delay se duplica cada intento (exponencial)
- ✅ Se agrega jitter random (0-1000ms)
- ✅ Se detiene en 60s máximo

**Vuelve a iniciar servidor** y verifica:
```
[INFO] WebSocket connected! (after X attempts)
```

---

### TEST 3: Message Queue (offline messages)

**Qué probar**: Cola de mensajes cuando WebSocket desconectado

**Pasos**:
1. Detén servidor Python
2. En la extensión, abre Command Palette (Ctrl+Shift+P)
3. Ejecuta comando: "Sendell: Show Connection Status"
4. Repite 5 veces
5. Inicia servidor Python

**Resultado esperado**:

Mientras desconectado:
```
[DEBUG] Message queued (1/1000)
[DEBUG] Message queued (2/1000)
...
```

Al reconectar:
```
[INFO] WebSocket connected!
[INFO] Processing queued messages (5 messages)
[DEBUG] Sent queued message 1/5
[DEBUG] Sent queued message 2/5
...
```

**Verifica**:
- ✅ Mensajes se almacenan en cola
- ✅ Se envían al reconectar
- ✅ Límite de 1000 mensajes

---

### TEST 4: Shell Integration - executeCommand()

**Qué probar**: API Shell Integration v1.93+ según tu investigación

**Pre-requisito**:
- ✅ VS Code 1.93.0+
- ✅ Terminal = PowerShell o Git Bash (NO cmd.exe)

**Pasos**:
1. En la ventana Extension Development Host, abre una terminal integrada
2. Espera a que aparezca el prompt (PS> o $)
3. En Command Palette: "Sendell: Execute Test Command"

**Resultado esperado**:
```
[INFO] Executing command with Shell Integration: echo "Hello Sendell"
[DEBUG] Output captured: Hello Sendell
[DEBUG] Exit code: 0
```

**Si sale error "Shell Integration not available"**:
- Verifica que NO estés usando cmd.exe
- Cambia a PowerShell: Ctrl+Shift+P → "Terminal: Select Default Profile"
- Cierra y vuelve a abrir terminal

---

### TEST 5: ANSI Stripping (strip-ansi)

**Qué probar**: Limpieza de códigos ANSI como mencionas en tu doc

**Pasos**:
1. En terminal integrada, ejecuta comando con colores:
```bash
# PowerShell
Write-Host "Test" -ForegroundColor Red

# Git Bash
echo -e "\033[31mTest\033[0m"
```

2. Observa logs de la extensión

**Resultado esperado**:
```
[DEBUG] Raw output: \x1b[31mTest\x1b[0m
[DEBUG] Clean output: Test
```

**Verifica**:
- ✅ Output limpio no tiene códigos \x1b
- ✅ Solo texto puro

---

### TEST 6: Process Detection (pidtree)

**Qué probar**: Detección de procesos hijo con pidtree

**Pasos**:
1. En terminal integrada, ejecuta proceso de larga duración:
```bash
# PowerShell
Start-Sleep -Seconds 60

# Git Bash
sleep 60
```

2. En Command Palette: "Sendell: List Child Processes"

**Resultado esperado**:
```
[INFO] Terminal PID: 12345
[INFO] Child processes found: 1
[DEBUG] Child PID: 12346 (sleep/Start-Sleep)
```

**Verifica**:
- ✅ Detecta proceso hijo (sleep)
- ✅ Muestra PID correcto

---

### TEST 7: Port Detection (tcp-port-used)

**Qué probar**: Detección de puertos en uso

**Pasos**:
1. Inicia un servidor local en puerto 3000:
```bash
# Node.js ejemplo
npx http-server -p 3000
```

2. En Command Palette: "Sendell: Check Port 3000"

**Resultado esperado**:
```
[INFO] Checking port 3000...
[INFO] Port 3000: IN USE
[DEBUG] Owner PID: 67890
```

**Detén el servidor** y vuelve a verificar:
```
[INFO] Port 3000: AVAILABLE
```

---

### TEST 8: Project Intelligence - Node.js

**Qué probar**: Auto-detección de tipo de proyecto (tu doc lista 8 tipos)

**Pasos**:
1. Abre una carpeta con `package.json` (por ejemplo, sendell-vscode-extension)
2. Command Palette: "Sendell: Analyze Project"

**Resultado esperado**:
```
[INFO] Parsing project: sendell-vscode-extension
[INFO] Detected type: nodejs
[INFO] Framework: None (or Vite/React/etc.)
[INFO] Scripts found: 5 (compile, watch, lint, etc.)
[INFO] Ports extracted: []
[INFO] Monorepo: false
```

**Verifica**:
- ✅ Detecta type: nodejs
- ✅ Lista scripts correctos
- ✅ Detecta framework si aplica

---

### TEST 9: Project Intelligence - Python

**Qué probar**: Detección de proyecto Python

**Pasos**:
1. Abre carpeta raíz de Sendell (tiene pyproject.toml)
2. Command Palette: "Sendell: Analyze Project"

**Resultado esperado**:
```
[INFO] Detected type: python
[INFO] Framework: uv (or Poetry/PDM)
[INFO] Ports: [7000] (if detects FastAPI/Django/Flask)
```

---

### TEST 10: Monorepo Detection

**Qué probar**: Detección de workspaces según tu investigación

**Si tienes un monorepo** (lerna.json, nx.json, pnpm-workspace.yaml):

**Resultado esperado**:
```
[INFO] Monorepo: true
[INFO] Workspace tool: Lerna/Nx/PNPM
```

---

### TEST 11: Multi-Instance Coordination

**Qué probar**: Coordinación con proper-lockfile entre ventanas

**Pasos**:
1. Abre **2 ventanas de VS Code**
2. En ambas, presiona F5 (2 Extension Development Hosts)
3. En ambas, ejecuta: "Sendell: Acquire Coordination Lock"

**Resultado esperado**:

**Ventana 1**:
```
[INFO] Acquiring lock for PID 12345...
[DEBUG] Lock acquired for PID 12345
```

**Ventana 2** (debería esperar o fallar):
```
[INFO] Acquiring lock for PID 67890...
[WARN] Lock already held by another instance, task skipped
[ERROR] Resource locked by another instance
```

**Ventana 1 suelta lock**:
```
[DEBUG] Lock released for PID 12345
```

**Ventana 2 reintenta**:
```
[DEBUG] Lock acquired for PID 67890
```

**Verifica**:
- ✅ Solo 1 instancia tiene lock a la vez
- ✅ Otras instancias esperan o fallan gracefully
- ✅ Lock se libera correctamente

---

### TEST 12: Cache TTL (5-10s)

**Qué probar**: Cache de procesos/puertos según tu doc (5-10s TTL)

**Pasos**:
1. Ejecuta "Sendell: List Processes" (genera cache)
2. Inmediatamente ejecuta de nuevo

**Resultado esperado**:
```
[DEBUG] Using cached process list (age: 0.5s)
```

**Espera 6 segundos** y ejecuta de nuevo:
```
[INFO] Cache expired, fetching fresh process list
```

**Verifica**:
- ✅ Cache se usa si <5s
- ✅ Se regenera si >5s

---

### TEST 13: Graceful Shutdown

**Qué probar**: Limpieza correcta al cerrar

**Pasos**:
1. Con extensión corriendo y conectada
2. Detén el debug (botón Stop o Shift+F5)

**Resultado esperado**:
```
[INFO] Extension deactivating...
[INFO] Stopping heartbeat
[INFO] Closing WebSocket connection
[INFO] Unregistering worker: PID 12345
[INFO] Extension deactivated gracefully
```

**Verifica**:
- ✅ Heartbeat se detiene
- ✅ WebSocket se cierra
- ✅ Worker se desregistra
- ✅ No quedan timers activos

---

## 🐛 TROUBLESHOOTING (Errores Comunes)

### Error 1: "Shell Integration not available"

**Causa**: Usando cmd.exe (tu investigación confirma que cmd.exe NO soporta Shell Integration)

**Solución**:
1. Ctrl+Shift+P → "Terminal: Select Default Profile"
2. Elige PowerShell o Git Bash
3. Cierra terminal actual y abre nueva

---

### Error 2: "UNMET DEPENDENCY" al hacer npm list

**Causa**: Dependencias no instaladas

**Solución**:
```bash
npm install
```

---

### Error 3: "Module not found: strip-ansi"

**Causa**: Versión incorrecta (la implementación requiere 7.1.0, no 6.x)

**Solución**:
```bash
npm uninstall strip-ansi
npm install strip-ansi@7.1.0
```

---

### Error 4: WebSocket no conecta (ECONNREFUSED)

**Causa**: Servidor Python no está corriendo

**Solución**:
```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv run python -m sendell start
```

---

### Error 5: "Lock timeout" en coordination

**Causa**: Lock huérfano de proceso crasheado

**Solución**:

Borra archivo de coordinación:
```bash
rm C:\Users\Daniel\AppData\Local\Temp\sendell\coordination.json
rm -rf C:\Users\Daniel\AppData\Local\Temp\sendell\coordination.json.lock
```

---

### Error 6: Process detection no funciona

**Causa**: Permisos insuficientes (Windows)

**Solución**:
- Ejecuta VS Code como Administrador (solo para testing)
- O acepta que algunos PIDs no serán detectables

---

## ✅ CHECKLIST FINAL

Marca cada test:

**Instalación**:
- [ ] Node.js v16+ instalado
- [ ] VS Code 1.93.0+ instalado
- [ ] Terminal = PowerShell o Git Bash (NO cmd.exe)
- [ ] npm install completado sin errores
- [ ] npm run compile completado sin errores
- [ ] 6 dependencias instaladas (strip-ansi, pidtree, ps-list, tcp-port-used, proper-lockfile, ws)

**Branch 1 - WebSocket**:
- [ ] Test 1: Heartbeat (ping 30s) funciona
- [ ] Test 2: Exponential backoff (1s → 60s) funciona
- [ ] Test 3: Message queue funciona

**Branch 2 - Shell Integration**:
- [ ] Test 4: executeCommand() funciona
- [ ] Test 5: ANSI stripping funciona

**Branch 3 - Process & Port**:
- [ ] Test 6: Process detection (pidtree) funciona
- [ ] Test 7: Port detection (tcp-port-used) funciona
- [ ] Test 12: Cache TTL (5-10s) funciona

**Branch 4 - Project Intelligence**:
- [ ] Test 8: Detecta Node.js (package.json)
- [ ] Test 9: Detecta Python (pyproject.toml)
- [ ] Test 10: Detecta monorepos (si aplica)

**Branch 5 - Multi-Instance**:
- [ ] Test 11: Coordination lock funciona
- [ ] Test 13: Graceful shutdown funciona

---

## 📊 REPORTE DE RESULTADOS

**Cuando termines los tests, reporta así**:

```
✅ Instalación: OK
✅ Branch 1 (WebSocket): OK - todos los tests pasaron
✅ Branch 2 (Shell Integration): OK - executeCommand funciona
⚠️ Branch 3 (Process): PARCIAL - pidtree funciona, pero port detection da error X
❌ Branch 4 (Project): FALLA - no detecta Python, error: [logs aquí]
✅ Branch 5 (Coordination): OK
```

**O simplemente**:
- ✅ "funciona todo" → Yo hago merge
- ⚠️ "funciona pero X está raro" → Describes X con logs
- ❌ "no funciona: [error]" → Mandas error + logs + screenshots

---

## 📚 REFERENCIAS

**Tu investigación original**: `guidefase6refactorultraterminals.txt`

**Implementación**:
- Branch 1: websocket.ts (+150 líneas)
- Branch 2: terminal.ts (+200 líneas)
- Branch 3: process.ts (420 líneas NUEVO)
- Branch 4: project.ts (540 líneas NUEVO)
- Branch 5: coordination.ts (410 líneas NUEVO)

**Total**: ~1,720 líneas basadas en tu documento de 18,000 palabras.

---

**¿Listo para testear?** 🚀

Empieza con PASO 1 (Pre-requisitos) y reporta resultados.
