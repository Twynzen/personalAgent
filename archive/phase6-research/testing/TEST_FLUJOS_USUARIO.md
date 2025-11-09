# TEST DE FLUJOS DE USUARIO - FASE 6
# Escenarios de Uso Real (Happy Paths)

**Objetivo**: Probar que la extensión funciona en situaciones reales de desarrollo.

---

## 🎯 FLUJOS A PROBAR (5 escenarios reales)

### FLUJO 1: Desarrollador abre proyecto y Sendell lo detecta automáticamente

**Situación real**: Abres VS Code en un proyecto, Sendell debe verlo

**Pasos**:
1. Abre VS Code en carpeta `sendell-vscode-extension` (o cualquier proyecto Node.js)
2. Presiona F5 para debuggear extensión
3. En la ventana nueva, pregúntale a Sendell en Python:
   ```
   "¿Qué proyecto tengo abierto?"
   ```

**Resultado esperado**:
```
Sendell responde algo como:
"Tienes abierto 'sendell-vscode-extension', es un proyecto Node.js con TypeScript.
Tiene 5 scripts: compile, watch, lint, etc."
```

**✅ Funciona si**: Sendell detecta el proyecto correctamente
**❌ Falla si**: Dice "no hay proyectos" o da error

---

### FLUJO 2: Desarrollador corre comando en terminal, Sendell ve el output

**Situación real**: Ejecutas npm install, Sendell debe ver qué pasó

**Pasos**:
1. En VS Code (Extension Development Host), abre terminal integrada
2. Ejecuta un comando simple:
   ```bash
   echo "Hello from terminal"
   ```
3. Pregúntale a Sendell:
   ```
   "¿Qué acabo de ejecutar en la terminal?"
   ```

**Resultado esperado**:
```
Sendell responde:
"Ejecutaste 'echo Hello from terminal' en PowerShell (o Git Bash).
El output fue: Hello from terminal"
```

**✅ Funciona si**: Sendell capturó el comando y el output
**❌ Falla si**: No sabe qué comando ejecutaste

---

### FLUJO 3: Desarrollador tiene servidor corriendo, Sendell detecta puerto activo

**Situación real**: Corres `npm run dev`, Sendell debe detectar el puerto

**Pasos**:
1. En terminal integrada, inicia servidor:
   ```bash
   # Ejemplo Node.js simple
   npx http-server -p 3000
   ```
2. Pregúntale a Sendell:
   ```
   "¿Qué puertos tengo activos?"
   ```

**Resultado esperado**:
```
Sendell responde:
"Puerto 3000 está en uso por el proceso http-server (PID: 12345).
Está escuchando conexiones."
```

**✅ Funciona si**: Detecta puerto 3000 activo
**❌ Falla si**: No detecta ningún puerto

---

### FLUJO 4: Desarrollador tiene errores en terminal, Sendell los ve

**Situación real**: Build falla, Sendell debe notarte

**Pasos**:
1. En terminal, ejecuta comando que falle:
   ```bash
   # Comando que no existe
   comandoInexistente
   ```
2. Pregúntale a Sendell:
   ```
   "¿Hubo algún error en la terminal?"
   ```

**Resultado esperado**:
```
Sendell responde:
"Sí, detecté un error: 'comandoInexistente' no se reconoce como comando.
Exit code: 1 (error)"
```

**✅ Funciona si**: Detecta el error y exit code
**❌ Falla si**: Dice "todo bien" o no vio el error

---

### FLUJO 5: Desarrollador abre 2 ventanas VS Code, Sendell las coordina

**Situación real**: Trabajas en 2 proyectos simultáneamente

**Pasos**:
1. Abre **2 ventanas de VS Code** diferentes
2. En ambas, presiona F5 (2 Extension Development Hosts corriendo)
3. Pregúntale a Sendell:
   ```
   "¿Cuántas ventanas de VS Code tengo abiertas?"
   ```

**Resultado esperado**:
```
Sendell responde:
"Tienes 2 ventanas de VS Code activas:
- Ventana 1: PID 12345, proyecto 'sendell'
- Ventana 2: PID 67890, proyecto 'sendell-vscode-extension'"
```

**✅ Funciona si**: Detecta ambas ventanas sin conflicto
**❌ Falla si**: Solo ve 1 ventana o da error de lock

---

## 📋 CHECKLIST RÁPIDO

Marca lo que funciona:

- [ ] **Flujo 1**: Sendell detecta proyecto abierto
- [ ] **Flujo 2**: Sendell captura comando + output de terminal
- [ ] **Flujo 3**: Sendell detecta puerto activo (3000)
- [ ] **Flujo 4**: Sendell detecta errores en terminal
- [ ] **Flujo 5**: Sendell coordina múltiples ventanas VS Code

---

## 🚨 SI ALGO FALLA

**Formato de reporte**:
```
❌ Flujo X falló

Qué hice:
[Describe los pasos]

Qué esperaba:
[Lo que debería pasar]

Qué pasó:
[Lo que realmente pasó]

Logs (si hay):
[Copia el error o mensaje]
```

**Ejemplo**:
```
❌ Flujo 2 falló

Qué hice:
- Ejecuté "echo test" en terminal
- Pregunté "¿qué ejecuté?"

Qué esperaba:
- Sendell responde "ejecutaste echo test"

Qué pasó:
- Sendell dijo "no hay terminales activas"

Logs:
[ERROR] Terminal not found in registry
```

---

## ⚙️ SETUP INICIAL (Hacer UNA vez)

### PASO 1: Compilar extensión

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell\sendell-vscode-extension
npm install
npm run compile
```

**Debe completar sin errores**. Si sale error de TypeScript, repórtalo.

---

### PASO 2: Iniciar servidor Sendell Python

**Abre NUEVA terminal** (no uses la misma donde compilaste):

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv run python -m sendell chat
```

Espera a ver:
```
========================================
      SENDELL - AI Agent v0.2
  Autonomous & Proactive AI Assistant
========================================

🔌 VS Code WebSocket server started (ws://localhost:7000)
Waiting for VS Code extension...
```

**NO cierres esta terminal** - Sendell debe quedar corriendo.

---

### PASO 3: Abrir extensión en debug

**Abre NUEVA ventana de VS Code** (Ctrl+Shift+N o File → New Window)

1. En la nueva ventana, abre carpeta: `C:\Users\Daniel\Desktop\Daniel\sendell\sendell-vscode-extension`
2. Presiona **F5** (o Run → Start Debugging)
3. Espera a que se abra ventana **[Extension Development Host]**

En la terminal de Python, ahora debe decir:
```
Waiting for VS Code extension... ✓ Connected
```

---

### PASO 4: Verificar conexión

En la ventana **[Extension Development Host]**:
- Presiona Ctrl+Shift+U (Output panel)
- En dropdown, selecciona "Sendell Extension"

Debe aparecer:
```
[INFO] Sendell extension activated
[INFO] WebSocket connecting to ws://localhost:7000...
[INFO] WebSocket connected!
[INFO] Heartbeat started (ping every 30s)
```

---

### PASO 5: Abrir proyecto para testear

**En la ventana Extension Development Host**:
- File → Open Folder
- Elige un proyecto (ej: `C:\Users\Daniel\Desktop\Daniel\sendell`)
- Abre terminal integrada (Ctrl+`)

**⚠️ IMPORTANTE**: Los terminales deben abrirse DESPUÉS de activar la extensión (F5), no antes.

---

**✅ Listo para probar flujos** - Ahora vuelve a la terminal de Python donde corre Sendell y empieza con Flujo 1.

---

## 💡 TIPS

- **No reinicies entre flujos** - prueba todos seguidos
- **Copia logs si falla** - ayuda a debuggear
- **Usa proyectos reales** - sendell, sendell-vscode-extension, etc.
- **Terminal = PowerShell o Git Bash** (NO cmd.exe)

---

## 🤔 FAQ: ¿Por qué dice "5 terminales" y luego "0 terminales"?

**Respuesta corta**: Dos fuentes de datos diferentes.

**Detección por Proceso** (`list_vscode_instances()`):
- Busca procesos VS Code en el sistema con `psutil`
- Cuenta terminales como **procesos hijos** de VS Code
- NO requiere que extensión esté corriendo
- ✅ Detecta TODOS los terminales que existen

**Detección por WebSocket** (ProjectContext):
- Solo cuenta terminales que se **conectaron al WebSocket**
- Requiere extensión corriendo (F5) en esa ventana
- Solo ve terminales abiertos DESPUÉS de activar extensión
- ❌ Si terminales se abrieron antes, no los ve

**Ejemplo**:
```
Terminal 1: Abierto ANTES de F5 → Process ✅ | WebSocket ❌
Terminal 2: Abierto DESPUÉS de F5 → Process ✅ | WebSocket ✅
Terminal 3: En ventana SIN extensión → Process ✅ | WebSocket ❌
```

**Solución**:
- Para probar, abre terminales DESPUÉS de presionar F5
- O reinicia VS Code con extensión ya activa
- Así ambas fuentes dirán lo mismo

---

**¿Listo?** Empieza con Flujo 1 y reporta qué pasa 🚀
