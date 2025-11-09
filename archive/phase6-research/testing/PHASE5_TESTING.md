# Guía de Pruebas - Phase 5: Pulido y Mejoras

**Branch:** `feature/vscode-polish-phase5`
**Estado:** Listo para Probar ✅
**Tiempo Estimado:** 15-20 minutos

---

## 🎯 ¿Qué Cambió en Phase 5?

### 1. **Categorización Automática de Terminales**
- Las terminales se categorizan solas según el primer comando que ejecutes
- Categorías: `claude_code`, `dev_server`, `git`, `test`, `build`, `other`
- Puntaje de confianza (0-100%) muestra qué tan seguro está el sistema

### 2. **Monitoreo Basado en Eventos (Ganancia MASIVA de Eficiencia)**
- La extensión YA NO envía todo el output de terminales constantemente
- Solo envía cuando:
  - Exit code != 0 (comando falló)
  - Output contiene "error", "exception", "failed"
  - Se detecta marcador de Claude Code ([SENDELL:COMPLETE])
  - Ruido de dev servers filtrado (webpack, HMR, vite updates)
- **Resultado:** ¡90-98% menos tráfico WebSocket!

### 3. **Dashboard de Terminales (Tab en Brain GUI)**
- NUEVO Tab "Terminales" en Brain GUI
- Muestra todos los proyectos y terminales con categorías
- Click en proyecto → ves terminales
- Click en terminal → ves output (últimas 50 líneas)
- Botón "Ver Completo" → output completo en ventana nueva
- **NUEVA Herramienta:** `show_terminal_dashboard()` - Sendell puede abrir esto dinámicamente

### 4. **Verificación de Conexión**
- Verificación al inicio: Espera 10s para que extensión conecte
- Muestra ✓ Conectado o ⚠ No conectado
- **NUEVO Comando:** `/vscode` - Revisa estado de conexión en cualquier momento
- Tips de troubleshooting si no conecta

### 5. **Detección de Marcadores de Claude Code**
- Detecta `[SENDELL:COMPLETE] <mensaje>` en output de terminal
- Detecta `[SENDELL:NOTIFY] <mensaje>` para alertas
- Se loguea prominentemente cuando se detecta
- Se almacena en output de terminal para recuperación

---

## 🧪 Instrucciones de Prueba

### Paso 1: Recompilar la Extensión

**Abre terminal en:**
```bash
cd sendell-vscode-extension
npm run compile
```

**Deberías ver:**
```
> sendell-extension@0.3.0 compile
> tsc -p ./
```
- Sin errores = ✅

### Paso 2: Recargar VS Code con la Extensión

**Opción A (Recomendada):**
1. Presiona `F5` en VS Code
2. O ve a "Run and Debug" (Ctrl+Shift+D)
3. Click en "Run Extension"
4. Se abre nueva ventana de VS Code con extensión activa

**Opción B (Si ya está corriendo):**
1. En la ventana de Extension Host (la que se abrió con F5)
2. Presiona Ctrl+R para recargar

**Verifica:**
- En barra de estado inferior derecha debe aparecer: `$(plug) Sendell`
- Si dice `$(debug-disconnect) Sendell` = no está conectado aún (normal, Sendell no está corriendo)

### Paso 3: Iniciar Sendell Chat

**En terminal (fuera de VS Code o en terminal de VS Code):**
```bash
uv run python -m sendell chat
```

**Output Esperado:**
```
========================================
      SENDELL - AI Agent v0.2
  Autonomous & Proactive AI Assistant
========================================

🔌 VS Code WebSocket server started (ws://localhost:7000)
Waiting for VS Code extension... ✓ Connected
⏰ Proactive reminders active (checking every 60s)

You:
```

**SI VES:**
```
Waiting for VS Code extension... ⚠ Not connected (extension may not be running)
Some VS Code features will be limited. Use /vscode to check status.
```
**Solución:**
- Espera 5 segundos más
- Escribe `/vscode` en el chat
- Si sigue sin conectar, recarga VS Code (Ctrl+R en ventana Extension Host)

### Paso 4: Probar Categorización de Terminales

**Abre 4 terminales en VS Code (Ctrl+Shift+`):**

#### Terminal 1: Claude Code
```bash
claude
```
**Qué debe pasar:**
- Extension detecta "claude" en comando
- Categoriza como `claude_code` (95% confidence)
- En logs de extensión: `Terminal ... categorized as 'claude_code' (confidence: 95%)`

**Cómo ver logs de extensión:**
- View → Output (Ctrl+Shift+U)
- Dropdown arriba: selecciona "Sendell"

#### Terminal 2: Sendell Chat (Dev Server)
```bash
uv run python -m sendell chat
```
**Qué debe pasar:**
- Detecta "uv run python -m sendell"
- Categoriza como `dev_server` (90% confidence)
- Logs: `Terminal ... categorized as 'dev_server' (confidence: 90%)`

#### Terminal 3: Git
```bash
git status
```
**Qué debe pasar:**
- Detecta "git status"
- Categoriza como `git` (95% confidence)
- Logs: `Terminal ... categorized as 'git' (confidence: 95%)`

#### Terminal 4: Testing
```bash
echo "Testing Sendell"
```
**Qué debe pasar:**
- No coincide con patrones conocidos
- Categoriza como `other` (30% confidence)
- Logs: `Terminal ... categorized as 'other' (confidence: 30%)`

**✅ ÉXITO:** Si ves las 4 categorizaciones correctas en logs de extensión

### Paso 5: Probar Dashboard de Terminales

#### Método 1: Preguntar a Sendell

**En el chat de Sendell, escribe:**
```
You: muéstrame el dashboard de terminales
```
O también funciona:
```
You: déjame ver las terminales
You: show me the terminal dashboard
You: quiero ver las terminales de vscode
```

**Qué debe pasar:**
1. Sendell usa tool `show_terminal_dashboard()`
2. Se abre ventana de Brain GUI automáticamente
3. Aparece tab "Terminales" (4to tab después de Memorias, Prompts, Herramientas)

#### Método 2: Abrir Brain GUI Directamente

**En el chat de Sendell:**
```
You: show me your brain
```
**Luego:**
- Click en tab "Terminales"

**Qué debes ver en el Dashboard:**

**Columna Izquierda (Proyectos):**
```
sendell (4 terminals)
```
O si tienes más proyectos abiertos, los verás listados.

**Columna Derecha (Terminales - después de seleccionar proyecto):**
```
[CC] claude
[DEV] uv
[GIT] git
[---] echo
```

**Panel Central (Output - después de seleccionar terminal):**
- Header con info del terminal
- Output de las últimas líneas
- Si seleccionas terminal de Claude Code, deberías ver tu sesión

**Botones:**
- "Actualizar" → recarga lista de proyectos/terminales
- "Ver Completo" → abre ventana nueva con hasta 1000 líneas

**✅ ÉXITO:** Si ves proyectos, terminales categorizados, y output al seleccionar

### Paso 6: Probar Estado de Conexión

**En el chat de Sendell, escribe:**
```
/vscode
```

**Output Esperado (si está conectado):**
```
VS Code Integration Status
┌─────────────────────┬────────────────────────────────────┐
│ Property            │ Value                              │
├─────────────────────┼────────────────────────────────────┤
│ Server Status       │ Running                            │
│ Server URL          │ ws://localhost:7000                │
│ Extension Status    │ Connected (1 client(s))            │
│ Projects Detected   │ 1                                  │
│ Terminals Monitored │ 4                                  │
└─────────────────────┴────────────────────────────────────┘
```

**Output Esperado (si NO está conectado):**
```
VS Code Integration Status
┌─────────────────────┬────────────────────────────────────┐
│ Property            │ Value                              │
├─────────────────────┼────────────────────────────────────┤
│ Server Status       │ Running                            │
│ Server URL          │ ws://localhost:7000                │
│ Extension Status    │ No clients connected               │
│ Projects Detected   │ 0                                  │
│ Terminals Monitored │ 0                                  │
└─────────────────────┴────────────────────────────────────┘

Troubleshooting:
1. Make sure VS Code is running
2. Check that Sendell extension is installed and enabled
3. Reload VS Code window (Ctrl+Shift+P -> 'Reload Window')
4. Check extension logs (Output panel -> Sendell)
```

**✅ ÉXITO:** Si ves tabla con stats correctos

### Paso 7: Probar Filtrado Basado en Eventos

**Objetivo:** Comprobar que output normal NO se envía, solo lo importante.

#### Prueba A: Output Normal (NO debe enviarse)

**En una terminal de VS Code:**
```bash
echo "Este es output normal que no tiene errores"
echo "Otra línea más de texto"
echo "Y otra más"
```

**Qué debe pasar:**
- Output se ve en VS Code (obviamente)
- En logs de Sendell Python: **NO debe aparecer este output**
- En logs de extensión: `Output buffered locally (not sent): terminal_name, XX chars`

**Cómo verificar:**
- Mira la consola de Python donde corre Sendell
- NO deberías ver "Este es output normal..."
- Deberías ver solo: `Output buffered locally`

#### Prueba B: Output con Error (SÍ debe enviarse)

**En una terminal:**
```bash
python -c "raise Exception('Error de prueba para Sendell')"
```

**Qué debe pasar:**
- Error se ejecuta en terminal
- En logs de extensión: `Important output from terminal_name (other): XX chars`
- En logs de Sendell Python: Deberías ver el error detectado
- El error se almacena en buffer

**Verifica en Dashboard:**
1. Abre dashboard: `You: muéstrame el dashboard`
2. Selecciona proyecto sendell
3. Selecciona la terminal donde ejecutaste el error
4. En panel de output deberías ver: `Error de prueba para Sendell`

**✅ ÉXITO:**
- Output normal = buffered locally, NO enviado
- Error = detectado y enviado

### Paso 8: Probar Detección de Errores

**En el chat de Sendell:**
```
You: ¿hay errores en mis terminales?
```
O:
```
You: check for errors in my terminals
```

**Qué debe pasar:**
1. Sendell usa tool `get_project_errors()`
2. Encuentra el error del Paso 7B
3. Responde algo como: "Sí, detecté 1 error en el proyecto sendell: Exception: Error de prueba para Sendell"

**✅ ÉXITO:** Sendell reporta el error que forzaste

### Paso 9: Probar Marcadores de Claude Code (AVANZADO)

**En la terminal de Claude Code (la que abriste con `claude`):**

Ejecuta:
```bash
echo "[SENDELL:COMPLETE] Tarea de prueba completada exitosamente"
```

**Qué debe pasar:**

1. **En logs de extensión (VS Code Output → Sendell):**
   - `Important output from claude (claude_code): XX chars`
   - Marcador detectado

2. **En logs de Sendell Python (consola):**
   - `[CLAUDE CODE] Task completed in sendell/claude: Tarea de prueba completada exitosamente`
   - O nivel WARNING con el mensaje

3. **En Dashboard:**
   - Abre dashboard
   - Selecciona terminal claude
   - En output deberías ver:
     ```
     >>> Claude Code completed: Tarea de prueba completada exitosamente
     ```

**También prueba el marcador NOTIFY:**
```bash
echo "[SENDELL:NOTIFY] Necesito tu aprobación para continuar"
```

**Debe aparecer en logs:**
```
[CLAUDE CODE] Notification from sendell/claude: Necesito tu aprobación para continuar
```

**✅ ÉXITO:** Marcadores detectados y logueados correctamente

### Paso 10: Probar Refresh del Dashboard

**Con el Dashboard abierto:**

1. Ejecuta un comando nuevo en una terminal de VS Code:
   ```bash
   npm --version
   ```

2. En el Dashboard, click en botón "Actualizar"

3. Deberías ver:
   - La terminal que ejecutó npm ahora categorizada (probablemente `build` o `other`)
   - El comando `npm --version` como último comando

**✅ ÉXITO:** Dashboard se actualiza con nueva info

---

## ✅ Checklist de Éxito

Después de probar, deberías tener:

- [ ] **Paso 1:** Extensión compilada sin errores
- [ ] **Paso 2:** VS Code recargado con extensión activa
- [ ] **Paso 3:** Sendell conecta con extensión (✓ Connected)
- [ ] **Paso 4:** 4 terminales categorizadas correctamente:
  - [ ] claude → `claude_code` (95%)
  - [ ] uv run → `dev_server` (90%)
  - [ ] git → `git` (95%)
  - [ ] echo → `other` (30%)
- [ ] **Paso 5:** Dashboard abre y muestra:
  - [ ] Proyectos en lista izquierda
  - [ ] Terminales con iconos [CC], [DEV], [GIT]
  - [ ] Output visible al seleccionar terminal
- [ ] **Paso 6:** Comando `/vscode` muestra stats correctos
- [ ] **Paso 7:** Filtrado funciona:
  - [ ] Output normal NO se envía (logs: "buffered locally")
  - [ ] Errores SÍ se envían (logs: "Important output")
- [ ] **Paso 8:** Sendell detecta errores con tool `get_project_errors()`
- [ ] **Paso 9:** Marcadores Claude Code detectados:
  - [ ] [SENDELL:COMPLETE] logueado
  - [ ] [SENDELL:NOTIFY] logueado
  - [ ] Aparecen en Dashboard
- [ ] **Paso 10:** Botón "Actualizar" funciona

---

## 🐛 ¿Qué Reportar?

### Si algo NO funciona:

**1. Copia el error exacto:**
- Screenshot o copia/pega el mensaje de error

**2. Revisa logs de extensión:**
- VS Code: View → Output → Dropdown selecciona "Sendell"
- Busca líneas con ERROR o WARN
- Copia las últimas 20 líneas

**3. Revisa logs de Sendell Python:**
- En la consola donde corre `uv run python -m sendell chat`
- Busca ERROR o WARNING
- Copia el traceback completo

**4. Escenarios específicos:**

| Problema | Qué reportar |
|----------|--------------|
| "Categorías incorrectas" | Dime qué terminal, qué comando ejecutaste, qué categoría le dio |
| "Dashboard no abre" | ¿Algún error? ¿Sendell respondió algo? |
| "Extensión no conecta" | Muéstrame output de `/vscode` |
| "Mucho tráfico aún" | Muéstrame logs, busca ratio de "buffered locally" vs "Important output" |
| "Marcadores no detectan" | Copia el comando exacto que ejecutaste |

**Dime:**
- ✅ **"funciona perfecto"** → Hago commit
- ⚠️ **"funciona pero X está raro"** → Describe X con detalle
- ❌ **"no funciona: [error]"** → Manda error completo + logs

---

## 🎯 Beneficios Principales de Phase 5

1. **90-98% menos tráfico WebSocket** (monitoreo basado en eventos)
2. **Auto-categorización** (no necesitas etiquetar manualmente)
3. **Dashboard visual** (fácil ver output de terminales)
4. **Verificación de conexión** (sabes si extensión funciona)
5. **Coordinación con Claude Code** (marcadores para tareas completadas)
6. **Queries on-demand** (Sendell solo revisa cuando le preguntas)

---

## 💡 Tips de Testing

1. **Mantén abierto Output panel de extensión** mientras pruebas (View → Output → Sendell)
2. **Usa múltiples terminales** para ver categorización en acción
3. **Ejecuta comandos que generen errores** para probar filtrado
4. **Pregunta a Sendell sobre terminales** para ver tools en acción
5. **Abre y cierra dashboard varias veces** para ver que es estable

---

## 🚀 Ready!

**Empieza desde el Paso 1 y ve marcando el checklist.**

Si algo no queda claro, pregúntame y ajusto las instrucciones.

**¡Dale con toda! 💪**
