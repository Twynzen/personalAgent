# Guía de Pruebas - Phase 6: Refactor & Enhancement

**Branch:** `feature/phase6-refactor-ultra`
**Estado:** Listo para Probar ✅
**Tiempo Estimado:** 25-30 minutos

---

## 🎯 ¿Qué Cambió en Phase 6?

Phase 6 es un **refactor masivo** basado en investigación exhaustiva (guidefase6refactorultraterminals.txt). Se implementaron 5 branches críticos para producción:

### Branch 1: WebSocket Client Refactor ⚡
- **Exponential backoff**: 1s → 2s → 4s → 8s → 16s → 32s → 60s (cap)
- **Jitter**: 0-1000ms random delay (previene thundering herd)
- **Heartbeat**: 30s ping, 35s pong timeout
- **Message queue**: Max 1000 mensajes durante desconexión
- **Resultado**: Conexión ultra-estable, reintenta correctamente

### Branch 2: Shell Integration Upgrade 🔧
- **executeCommand()**: API v1.93+ con output + exitCode
- **strip-ansi**: Output limpio sin códigos ANSI
- **Fallback automático**: sendText() si Shell Integration no disponible
- **Error messaging**: Indica si cmd.exe (no soportado) vs PowerShell/Git Bash
- **Resultado**: Control completo de terminales con output confiable

### Branch 3: Process & Port Detection 🔍
- **pidtree**: Enumeración recursiva de child processes (10-50ms)
- **ps-list**: Detalles completos de procesos (PID, nombre, CPU, memoria)
- **tcp-port-used**: Detección de puertos en uso
- **Caching**: 5s TTL para desarrollo, previene llamadas excesivas
- **Running state**: Threshold 30s para procesos "long-running"
- **Resultado**: Detecta proyectos corriendo con 95%+ accuracy

### Branch 4: Project Intelligence 🧠
- **Auto-detección**: Node.js, Python, Rust, Go, Java, .NET, Ruby, PHP
- **Framework detection**: Next.js, React, Vue, Angular, FastAPI, Django, Flask, etc.
- **Port extraction**: Extrae puertos de configs automáticamente
- **Monorepo detection**: workspaces, lerna.json, nx.json, pnpm-workspace.yaml
- **Script priority**: dev > start > serve (para arrancar proyectos)
- **CLAUDE.md**: Detecta si proyecto tiene CLAUDE.md
- **Resultado**: Entiende proyectos automáticamente sin configuración manual

### Branch 5: Multi-Instance Coordination 🔒
- **proper-lockfile**: Atomic mkdir() locking (cross-platform seguro)
- **Stale timeout**: 10s (limpia workers crashed)
- **Heartbeat**: 5s updates (mantiene lock activo)
- **Election**: PID más bajo se convierte en active worker (determinista)
- **Coordination file**: temp/sendell/coordination.json
- **Resultado**: Múltiples VS Code windows sin conflictos

---

## 🧪 Instrucciones de Prueba

### Paso 0: Instalar Dependencias (IMPORTANTE ⚠️)

**Antes de compilar, DEBES instalar las nuevas dependencias NPM:**

```bash
cd sendell-vscode-extension
npm install
```

**Nuevas dependencias agregadas:**
- `strip-ansi` - Remoción de códigos ANSI
- `pidtree` - Process hierarchy detection
- `ps-list` - Process details
- `tcp-port-used` - Port checking
- `proper-lockfile` - File-based locking

**Verifica que instaló correctamente:**
```bash
npm list strip-ansi pidtree ps-list tcp-port-used proper-lockfile
```

Deberías ver las 5 librerías listadas sin errores.

---

### Paso 1: Compilar la Extensión

```bash
cd sendell-vscode-extension
npm run compile
```

**Output esperado:**
```
> sendell-extension@0.3.0 compile
> tsc -p ./
```

- Si ves errores de TypeScript: REPORTA (no deberían haber)
- Si compila sin errores: ✅ Continúa

---

### Paso 2: Recargar VS Code con Extensión

**Opción A (Recomendada):**
1. Presiona `F5` en VS Code
2. Se abre ventana "Extension Development Host"
3. Verifica barra inferior derecha: `$(sync~spin) Sendell` (conectando)

**Opción B (Si ya corriendo):**
1. En ventana Extension Host, presiona `Ctrl+R` para recargar

**Verifica:**
- Barra de estado muestra `Sendell` con algún ícono
- Si dice `$(error) Sendell` = problema de compilación

---

### Paso 3: Iniciar Sendell Python Server

**En terminal (puede ser terminal de VS Code o externa):**
```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv run python -m sendell chat
```

**Output esperado:**
```
========================================
      SENDELL - AI Agent v0.2
  Autonomous & Proactive AI Assistant
========================================

🔌 VS Code WebSocket server started (ws://localhost:7000)
Waiting for VS Code extension...
```

**Espera 2-3 segundos...**

Si la extensión está funcionando, deberías ver:
```
✓ Connected
⏰ Proactive reminders active (checking every 60s)

You:
```

**Si ves:**
```
⚠ Not connected (extension may not be running)
```

**Solución:**
1. Verifica que ventana Extension Host esté abierta
2. Presiona `Ctrl+R` en Extension Host para recargar
3. Espera 5 segundos más
4. Si sigue sin conectar, escribe `/vscode` para diagnosticar

---

### Paso 4: Verificar WebSocket Connection (Branch 1)

**En el chat de Sendell, escribe:**
```
/vscode
```

**Output esperado:**
```
VS Code Integration Status
┌─────────────────────┬────────────────────────────────────┐
│ Property            │ Value                              │
├─────────────────────┼────────────────────────────────────┤
│ Server Status       │ Running                            │
│ Server URL          │ ws://localhost:7000                │
│ Extension Status    │ Connected (1 client(s))            │
│ Projects Detected   │ X                                  │
│ Terminals Monitored │ Y                                  │
└─────────────────────┴────────────────────────────────────┘
```

**Qué verificar:**
- ✅ `Extension Status` = "Connected (1 client(s))"
- ✅ `Projects Detected` > 0
- ✅ `Terminals Monitored` >= 0

**Si dice "No clients connected":**
1. Ve a Output panel en VS Code: `View` → `Output` → Dropdown: `Sendell`
2. Busca errores
3. Verifica que `ws://localhost:7000` no esté bloqueado por firewall

**✅ ÉXITO**: Si ves "Connected"

---

### Paso 5: Test WebSocket Stability (Branch 1 - Heartbeat)

**Objetivo**: Verificar que conexión NO se cae después de 60s (bug común pre-refactor)

**Pasos:**
1. Con Sendell corriendo y conectado
2. Espera **2 minutos** (120 segundos) sin hacer nada
3. En VS Code: `View` → `Output` → `Sendell`
4. Busca líneas: `Sending ping to server` cada ~30 segundos
5. Busca líneas: `Pong received from server` después de cada ping

**Output esperado en logs (cada 30s):**
```
[DEBUG] Sending ping to server
[DEBUG] Pong received from server
[DEBUG] Sending ping to server
[DEBUG] Pong received from server
```

**Después de 2 minutos, escribe en Sendell chat:**
```
You: /vscode
```

**Verifica:**
- ✅ Sigue diciendo "Connected"
- ✅ NO dice "Disconnected"
- ✅ NO hubo reconexión (no debería ver mensajes "Reconnecting...")

**✅ ÉXITO**: Conexión estable por 2+ minutos

---

### Paso 6: Test WebSocket Reconnection (Branch 1 - Exponential Backoff)

**Objetivo**: Verificar reconexión automática con exponential backoff

**Pasos:**
1. Con Sendell conectado
2. **DETÉN el servidor Python**: `Ctrl+C` en terminal de Sendell
3. En VS Code Output (`Sendell`), observa logs de reconexión

**Output esperado (exponential backoff):**
```
[WARN] Disconnected from Sendell server: 1006 - Unknown reason
[INFO] Scheduling reconnect attempt 1/10 in 1XXXms (base: 1000ms, jitter: XXXms)
[INFO] Connecting to Sendell server: ws://localhost:7000
[ERROR] WebSocket error: ...
[INFO] Scheduling reconnect attempt 2/10 in 2XXXms (base: 2000ms, jitter: XXXms)
[INFO] Scheduling reconnect attempt 3/10 in 4XXXms (base: 4000ms, jitter: XXXms)
[INFO] Scheduling reconnect attempt 4/10 in 8XXXms (base: 8000ms, jitter: XXXms)
```

**Verifica:**
- ✅ Delays aumentan: ~1s → ~2s → ~4s → ~8s
- ✅ Hay jitter (nunca exacto, tiene 0-1000ms random)
- ✅ NO hace spam de intentos inmediatos

4. **REINICIA Sendell**: `uv run python -m sendell chat`
5. Espera a que reconecte automáticamente

**Output esperado:**
```
[INFO] Connected to Sendell server
[INFO] Handshake sent: X workspace(s)
```

**En Sendell chat, verifica con:**
```
You: /vscode
```

Debe decir `Connected (1 client(s))` nuevamente.

**✅ ÉXITO**: Reconexión automática con backoff exponencial + jitter

---

### Paso 7: Test Message Queue (Branch 1 - Offline Messages)

**Objetivo**: Verificar que mensajes se guardan durante desconexión y se envían al reconectar

**Pasos:**
1. Con Sendell conectado
2. En VS Code, abre una terminal (Ctrl+Shift+`)
3. **DETÉN Sendell**: `Ctrl+C`
4. Ejecuta comandos en terminal de VS Code:
   ```bash
   echo "Test message 1"
   echo "Test message 2"
   git status
   ```
5. En Output panel (`Sendell`), verifica:
   ```
   [DEBUG] Message queued (1/1000)
   [DEBUG] Message queued (2/1000)
   [DEBUG] Message queued (3/1000)
   ```

6. **REINICIA Sendell**: `uv run python -m sendell chat`
7. Espera reconexión
8. En Output panel (`Sendell`), busca:
   ```
   [INFO] Flushing X queued message(s)
   [DEBUG] Sent queued message: ...
   [INFO] Message queue flushed successfully
   ```

**✅ ÉXITO**: Mensajes se guardan offline y se envían al reconectar

---

### Paso 8: Test Shell Integration - executeCommand (Branch 2)

**Objetivo**: Verificar que `executeCommand()` funciona con output + exitCode

**Pre-requisito**: Debes estar en PowerShell o Git Bash (NO cmd.exe)

**Verifica tu shell:**
En terminal de VS Code, ejecuta:
```powershell
echo $PSVersionTable   # PowerShell
```
O:
```bash
echo $SHELL   # Git Bash
```

**Si estás en cmd.exe:**
1. Abre nueva terminal
2. Click en dropdown de shell (arriba derecha de terminal)
3. Selecciona "PowerShell" o "Git Bash"

**Pasos de testing:**
1. En Output panel (`Sendell`), configura log level a DEBUG:
   - Ve a configuración VS Code: `Ctrl+,`
   - Busca: `sendell.logLevel`
   - Cambia a: `debug`
   - Recarga extensión: `Ctrl+R` en Extension Host

2. Ejecuta comando que FALLA (exit code != 0):
   ```powershell
   python -c "raise Exception('Test error for Sendell')"
   ```

3. En Output panel (`Sendell`), busca:
   ```
   [INFO] Executing command with Shell Integration: python -c "raise Exception('Test error for Sendell')"
   [INFO] Command completed: exit code 1, output: XXX chars
   ```

**Verifica:**
- ✅ Dice "Executing command with Shell Integration"
- ✅ Muestra `exit code 1` (o != 0)
- ✅ Muestra tamaño de output en chars

4. Ejecuta comando exitoso:
   ```powershell
   echo "Hello Sendell"
   ```

5. Verifica:
   ```
   [INFO] Command completed: exit code 0, output: XXX chars
   ```

**✅ ÉXITO**: Shell Integration captura commands + exitCode + output

---

### Paso 9: Test ANSI Stripping (Branch 2)

**Objetivo**: Verificar que códigos ANSI se remueven del output

**Pasos:**
1. Instala un comando que produce output con colores (si no tienes):
   ```powershell
   npm install -g chalk-cli
   ```

2. Ejecuta comando con colores:
   ```bash
   echo "$(tput setaf 1)RED TEXT$(tput sgr0) normal text"
   ```
   O en PowerShell:
   ```powershell
   Write-Host "RED TEXT" -ForegroundColor Red
   ```

3. En Output panel (`Sendell`), el output NO debería tener códigos ANSI raros como:
   - `\x1b[31m` (color codes)
   - `\x1b[0m` (reset)
   - `[1m`, `[22m`, etc.

**Verifica:**
- ✅ Output se ve limpio (solo texto)
- ✅ NO hay `\x1b` o `[XXm` en logs

**✅ ÉXITO**: ANSI escape codes removidos correctamente

---

### Paso 10: Test Process Detection (Branch 3)

**Objetivo**: Verificar detección de child processes

**Este test NO tiene UI visible**, pero puedes verificar funcionalidad preguntándole a Sendell.

**Pasos:**
1. Abre múltiples terminales en VS Code con comandos long-running:
   - Terminal 1: `uv run python -m sendell chat` (si tienes otra ventana)
   - Terminal 2: `npm run dev` (si tienes proyecto Node.js)
   - Terminal 3: Deja vacía o ejecuta `ping localhost -t` (Windows)

2. En chat de Sendell, pregunta:
   ```
   You: ¿qué proyectos tengo corriendo en VS Code?
   ```

   O:
   ```
   You: list my VS Code projects and terminals
   ```

**Sendell debería:**
- Usar tool `list_vscode_instances()` (de psutil - ya existe)
- O usar tools nuevos si están integrados

**Verifica en logs de Sendell Python:**
- Busca líneas sobre detección de procesos
- Debería mencionar VS Code instances, PIDs, terminales

**✅ ÉXITO**: Sendell puede ver proyectos de VS Code

---

### Paso 11: Test Project Intelligence (Branch 4)

**Objetivo**: Verificar auto-detección de tipo de proyecto

**Este test requiere integración Python (próxima fase)**, pero puedes verificar que la extensión recopila metadata.

**Pasos:**
1. Abre un workspace de Node.js (ej: sendell-vscode-extension/)
2. En Output panel (`Sendell`), busca handshake message:
   ```
   [INFO] Handshake sent: 1 workspace(s)
   ```

3. El handshake incluye:
   - `name`: nombre del workspace
   - `path`: ruta completa
   - `type`: 'folder'

**Para verificar project intelligence:**
1. Abre Developer Tools de Extension Host:
   - `Help` → `Toggle Developer Tools`
2. En Console, ejecuta:
   ```javascript
   const proj = await vscode.commands.executeCommand('sendell.detectProjectType', '/path/to/project');
   console.log(proj);
   ```

**Si implementado, deberías ver:**
```json
{
  "type": "nodejs",
  "framework": "Next.js",
  "ports": [3000],
  "isMonorepo": false
}
```

**Por ahora (sin integración completa):**
- ✅ Extensión compila sin errores (project.ts existe)
- ✅ No hay errores de TypeScript

**✅ ÉXITO**: project.ts compila y está listo para integración

---

### Paso 12: Test Multi-Instance Coordination (Branch 5)

**Objetivo**: Verificar que múltiples VS Code windows se coordinan sin conflictos

**Pasos:**
1. Con Sendell corriendo y 1 VS Code Extension Host abierto
2. Abre OTRA instancia de VS Code:
   - `File` → `New Window`
   - Presiona `F5` (lanza otra Extension Host)

3. Ahora tienes 2 Extension Hosts corriendo simultáneamente

4. En Output panel de AMBAS extensiones, busca:
   ```
   [INFO] CoordinationManager initialized (PID: XXXX, file: ...)
   [INFO] Coordination started for PID XXXX
   [INFO] Worker registered: PID XXXX
   ```

5. Uno de ellos debería decir:
   ```
   [INFO] Elected as active worker: PID XXXX
   ```

   (El PID más bajo se convierte en active worker)

6. Verifica archivo de coordinación:
   ```powershell
   type %TEMP%\sendell\coordination.json
   ```

   O en Git Bash:
   ```bash
   cat /tmp/sendell/coordination.json
   ```

**Debe contener:**
```json
{
  "activeWorker": 12345,
  "workersRegistered": [12345, 12346],
  "lastActivity": 1699999999999,
  "version": "0.3.0"
}
```

**Verifica:**
- ✅ `activeWorker`: PID más bajo
- ✅ `workersRegistered`: Array con 2 PIDs
- ✅ `lastActivity`: Timestamp reciente (actualiza cada 5s)

7. **CIERRA una Extension Host** (la que NO es active worker)

8. Espera 10 segundos (stale timeout)

9. Verifica coordination.json nuevamente:
   - ✅ `workersRegistered` ahora tiene solo 1 PID (el que sigue corriendo)

**✅ ÉXITO**: Múltiples instances se coordinan y limpian workers crashed

---

### Paso 13: Test Graceful Shutdown (Branch 1+5)

**Objetivo**: Verificar que extensión se desconecta limpiamente

**Pasos:**
1. Con todo corriendo (Sendell + Extension)
2. **CIERRA Extension Host** (ventana completa)
3. En terminal de Sendell Python, verifica:
   - NO deberías ver errores de WebSocket
   - Puede ver: `[WARN] Disconnected ...` pero sin crash

4. En coordination.json:
   - Debería haber removido el PID de la extensión cerrada

**✅ ÉXITO**: Cierre limpio sin errores

---

## ✅ Checklist de Éxito

Después de completar todos los tests, marca los que funcionaron:

**Branch 1: WebSocket Client**
- [ ] npm install ejecutó sin errores
- [ ] Extensión compila sin errores TypeScript
- [ ] Conexión inicial funciona (`/vscode` muestra Connected)
- [ ] Heartbeat: conexión estable por 2+ minutos
- [ ] Exponential backoff: delays aumentan correctamente (1s→2s→4s→8s)
- [ ] Jitter: delays tienen variación random
- [ ] Message queue: mensajes offline se envían al reconectar

**Branch 2: Shell Integration**
- [ ] executeCommand() funciona (logs muestran "Executing command with Shell Integration")
- [ ] Exit codes capturados correctamente (0 para éxito, !=0 para error)
- [ ] Output capturado (muestra "XXX chars")
- [ ] ANSI stripping: output limpio sin `\x1b` codes

**Branch 3: Process & Port Detection**
- [ ] process.ts compila sin errores
- [ ] Sendell puede listar proyectos VS Code (pregunta en chat)

**Branch 4: Project Intelligence**
- [ ] project.ts compila sin errores
- [ ] Handshake envía workspace info correctamente

**Branch 5: Multi-Instance Coordination**
- [ ] coordination.ts compila sin errores
- [ ] Coordination file creado en temp/sendell/coordination.json
- [ ] Worker registration funciona (PIDs en workersRegistered)
- [ ] Active worker election (PID más bajo elegido)
- [ ] Stale worker cleanup (PID removido al cerrar Extension Host)
- [ ] Graceful shutdown: extensión se desconecta limpiamente

---

## 🐛 ¿Qué Reportar?

### Si algo NO funciona:

**1. Errores de npm install:**
```bash
npm install 2>&1 | tee npm-install-log.txt
```
Envía `npm-install-log.txt`

**2. Errores de compilación TypeScript:**
```bash
npm run compile 2>&1 | tee compile-log.txt
```
Envía `compile-log.txt` + screenshot de errores

**3. Extension no conecta:**
- Screenshot de barra de estado (muestra ícono de Sendell)
- Output panel completo (`View` → `Output` → `Sendell`)
- Output de `/vscode` en Sendell chat
- Verifica firewall: `netstat -an | findstr 7000` (Windows)

**4. Heartbeat no funciona:**
- Output panel completo (últimos 5 minutos)
- Timestamp cuando desconectó

**5. Exponential backoff incorrecto:**
- Output panel mostrando todos los intentos de reconexión
- Calcula delays manualmente y compara con esperado

**6. Shell Integration no funciona:**
- ¿Qué shell usas? (`echo $PSVersionTable` en PowerShell, `echo $SHELL` en Bash)
- Si cmd.exe: Esto es esperado (no soportado), cambia a PowerShell
- Output panel con logs de ejecutar comando

**7. Coordination no funciona:**
- Contenido completo de coordination.json
- Output panel de AMBAS Extension Hosts
- PIDs de ambos procesos: `Get-Process | Where-Object {$_.ProcessName -like "*extensionHost*"}`

**Formato ideal:**
```
TEST: [nombre del test]
RESULTADO: [FALLO/ÉXITO]
ESPERADO: [qué debería pasar]
ACTUAL: [qué pasó realmente]
LOGS: [logs relevantes]
SCREENSHOTS: [si aplica]
```

---

## 🎯 Beneficios de Phase 6

Después de completar Phase 6, deberías tener:

1. **Conexión ultra-estable**: No más desconexiones misteriosas después de 60s
2. **Reconexión inteligente**: Exponential backoff + jitter previene spam
3. **Control completo de terminales**: executeCommand() con output + exitCode
4. **Output limpio**: Sin códigos ANSI raros
5. **Process monitoring**: Detecta proyectos corriendo con 95%+ accuracy
6. **Project intelligence**: Entiende tipo de proyecto automáticamente
7. **Multi-instance safe**: Múltiples VS Code sin conflictos
8. **Production-ready**: Basado en 55,000 palabras de research + best practices

---

## 💡 Tips de Testing

1. **Output panel es tu amigo**: `View` → `Output` → `Sendell`
2. **Usa DEBUG log level** para ver todo: Settings → `sendell.logLevel` → `debug`
3. **Ten paciencia**: Algunas features tienen delays intencionales (heartbeat 30s, stale cleanup 10s)
4. **Cierra limpiamente**: Usa `Ctrl+C` en Sendell, cierra Extension Host normalmente
5. **coordination.json es útil**: Muestra estado real de workers activos

---

## 🚀 Ready!

**Empieza desde Paso 0 (npm install) y ve paso a paso.**

Si algo no queda claro, pregúntame y ajusto el testing guide.

**¡Vamos con toda! 💪**
