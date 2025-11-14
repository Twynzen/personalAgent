# Sendell - Instalación Híbrida (FastAPI + Node.js)

**Versión:** v0.3
**Actualizado:** 2025-11-13

Esta guía cubre la instalación de la arquitectura híbrida de Sendell con:
- FastAPI (Python) para proyectos y métricas
- Node.js para terminales PTY

---

## 📋 Requisitos Previos

### Software Requerido

**Python:**
- Python 3.10+ ([python.org](https://www.python.org/downloads/))
- uv package manager ([astral.sh/uv](https://astral.sh/uv))

**Node.js:**
- Node.js 16+ LTS ([nodejs.org](https://nodejs.org/))
- npm (incluido con Node.js)

**Herramientas de compilación (Windows):**
- Visual Studio Build Tools 2019+ ([visualstudio.microsoft.com](https://visualstudio.microsoft.com/downloads/))
  - O: `npm install --global windows-build-tools` (deprecado pero funciona)
- Python 3.x (para node-gyp)

**Opcional:**
- Git ([git-scm.com](https://git-scm.com/))
- VS Code ([code.visualstudio.com](https://code.visualstudio.com/))

### Verificar Instalaciones

```bash
# Python
python --version
# Debe ser 3.10+

# uv
uv --version

# Node.js
node --version
# Debe ser 16+

# npm
npm --version

# Build tools (Windows)
npm config get msvs_version
# Debe mostrar 2019 o superior
```

---

## 🚀 Instalación

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/sendell.git
cd sendell
```

O si ya tienes el código, navega al directorio:

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
```

### Paso 2: Configurar Backend Python (FastAPI)

**2.1. Instalar dependencias Python:**

```bash
uv sync
```

Esto instalará:
- FastAPI + Uvicorn
- LangGraph + LangChain
- psutil
- Pydantic
- Todas las dependencias del agente Sendell

**2.2. Crear archivo `.env`:**

```bash
# Copiar template
cp .env.example .env

# O crear manualmente
notepad .env
```

**Contenido mínimo de `.env`:**

```env
# OpenAI API (OBLIGATORIO)
OPENAI_API_KEY=sk-tu-api-key-aqui

# Autonomía
SENDELL_AUTONOMY_LEVEL=2

# Logging
SENDELL_LOG_LEVEL=INFO

# Proactive system
SENDELL_PROACTIVE_MODE=true
SENDELL_LOOP_INTERVAL=60
```

**2.3. Verificar instalación:**

```bash
# Test basic import
uv run python -c "from sendell.agent.core import SendellAgent; print('OK')"

# Ver versión
uv run python -m sendell version
```

### Paso 3: Configurar Terminal Server (Node.js)

**3.1. Instalar dependencias Node.js:**

```bash
cd terminal-server
npm install
```

Esto instalará:
- `ws` (WebSocket server)
- `node-pty` (PTY bindings - requiere compilación nativa)

**Nota Windows:** Si `node-pty` falla, instalar build tools:

```bash
npm install --global windows-build-tools
# O manualmente: Visual Studio Build Tools 2019+
```

**3.2. Verificar instalación:**

```bash
# Test server
node server.js
```

Deberías ver:

```
========================================
   Sendell Terminal Server
========================================
Plataforma: win32 10.0.19045
Node.js: v18.x.x
WebSocket: ws://localhost:3000
========================================

✅ Servidor listo - Esperando conexiones...
```

Presiona `Ctrl+C` para detener.

**3.3. Volver al directorio raíz:**

```bash
cd ..
```

### Paso 4: Compilar Dashboard Angular

**4.1. Instalar dependencias Angular:**

```bash
cd sendell-dashboard
npm install
```

**4.2. Build para producción:**

```bash
npm run build
```

Esto genera archivos en `dist/sendell-dashboard/browser/`

**4.3. Copiar build a static de FastAPI:**

```bash
# Windows (PowerShell)
cd ..
.\build-dashboard.sh

# O manualmente:
Remove-Item -Recurse -Force src\sendell\web\static\*
Copy-Item -Recurse sendell-dashboard\dist\sendell-dashboard\browser\* src\sendell\web\static\
```

**4.4. Verificar:**

```bash
ls src\sendell\web\static\
```

Deberías ver:
- `index.html`
- `main-*.js`
- `polyfills-*.js`
- `styles-*.css`

---

## ▶️ Iniciar Sendell

### Opción 1: Inicio Manual (Recomendado para desarrollo)

**Terminal 1 - FastAPI Server:**

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv run uvicorn sendell.web.server:app --port 8765 --reload
```

Output esperado:

```
INFO:     Uvicorn running on http://127.0.0.1:8765
INFO:     Application startup complete.
```

**Terminal 2 - Node.js Terminal Server:**

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell\terminal-server
npm start
```

Output esperado:

```
========================================
   Sendell Terminal Server
========================================
WebSocket: ws://localhost:3000
========================================

✅ Servidor listo - Esperando conexiones...
```

**Abrir Dashboard:**

En navegador: [http://localhost:8765](http://localhost:8765)

### Opción 2: Script de Inicio (TODO - v0.4)

Crear `start-sendell.bat` (Windows):

```bat
@echo off
echo Starting Sendell...

start "FastAPI Server" cmd /k "cd C:\Users\Daniel\Desktop\Daniel\sendell && uv run uvicorn sendell.web.server:app --port 8765"

timeout /t 2 /nobreak

start "Node.js Terminal Server" cmd /k "cd C:\Users\Daniel\Desktop\Daniel\sendell\terminal-server && npm start"

timeout /t 2 /nobreak

echo Opening dashboard...
start http://localhost:8765

echo.
echo Sendell started!
echo - FastAPI: http://localhost:8765
echo - Node.js PTY: ws://localhost:3000
echo.
echo Press Ctrl+C in each window to stop.
pause
```

Ejecutar:

```bash
.\start-sendell.bat
```

---

## 🧪 Verificar Instalación

### Test 1: FastAPI Health Check

```bash
# Con server corriendo
curl http://localhost:8765/api/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "timestamp": "2025-11-13T..."
}
```

### Test 2: Lista de Proyectos

```bash
curl http://localhost:8765/api/projects
```

Respuesta esperada (con VS Code abierto):

```json
{
  "projects": [
    {
      "pid": 12345,
      "name": "sendell",
      "workspace_path": "C:\\Users\\Daniel\\Desktop\\Daniel\\sendell",
      "state": "ready"
    }
  ]
}
```

### Test 3: Node.js Terminal Server

**Opción A - Con wscat:**

```bash
# Instalar wscat
npm install -g wscat

# Conectar al terminal server
wscat -c ws://localhost:3000

# Deberías ver el prompt de PowerShell/cmd
# Escribe comandos y presiona Enter
> dir
< [output del comando]
```

**Opción B - Desde Dashboard:**

1. Abrir http://localhost:8765
2. Debe mostrar lista de proyectos VS Code
3. Click en proyecto con estado OFFLINE
4. Debe aparecer terminal embebido
5. Escribir `dir` o `ls` + Enter
6. Debe mostrar contenido del directorio

### Test 4: Dashboard UI

**Checklist:**

- [ ] Dashboard carga sin errores (DevTools → Console)
- [ ] Aparece título "Sendell - Project Monitor"
- [ ] Lista de proyectos VS Code visible
- [ ] Gráficos de actividad animados (ECG-style)
- [ ] Click en proyecto OFFLINE → terminal aparece
- [ ] Escribir comandos en terminal → output visible
- [ ] Click fuera del terminal → terminal se oculta
- [ ] Click nuevamente en proyecto → terminal reaparece

---

## 🐛 Troubleshooting

### Error: "Module not found: psutil"

**Causa:** Dependencias Python no instaladas

**Solución:**

```bash
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv sync
```

### Error: "gyp ERR! build error" (node-pty)

**Causa:** No hay herramientas de compilación en Windows

**Solución:**

```bash
# Opción 1: windows-build-tools
npm install --global windows-build-tools

# Opción 2: Visual Studio Build Tools
# Descargar de: https://visualstudio.microsoft.com/downloads/
# Seleccionar: "Desktop development with C++"
```

### Error: "Port 8765 already in use"

**Causa:** Otra instancia de FastAPI corriendo

**Solución:**

```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr 8765

# Matar proceso (PowerShell - reemplazar PID)
Stop-Process -Id <PID> -Force

# O cambiar puerto
uv run uvicorn sendell.web.server:app --port 8766
```

### Error: "Port 3000 already in use"

**Causa:** Otra instancia de Node.js corriendo

**Solución:**

```bash
# Ver proceso
netstat -ano | findstr 3000

# Matar proceso
taskkill /F /PID <PID>
```

### Error: "Dashboard muestra pantalla en blanco"

**Causa:** Build de Angular no copiado a static/

**Solución:**

```bash
cd sendell-dashboard
npm run build
cd ..
.\build-dashboard.sh
```

### Error: "Terminal no aparece al hacer click"

**Checks:**

1. **Node.js server corriendo:**
   ```bash
   netstat -ano | findstr 3000
   # Debe mostrar LISTENING
   ```

2. **WebSocket conectando:**
   - Abrir DevTools (F12)
   - Network → WS
   - Debe aparecer conexión a `ws://localhost:3000`
   - Ver mensajes

3. **Console errors:**
   - DevTools → Console
   - Buscar errores relacionados con xterm.js o WebSocket

**Solución común:**

```bash
# Reiniciar Node.js server
cd terminal-server
npm start
```

### Error: "Comandos no se ejecutan / cada letra es comando"

**Causa:** Frontend no actualizado a patrón echo remoto

**Solución:**

Verificar `sendell-dashboard/src/app/components/terminal.component.ts`:

```typescript
// ✅ CORRECTO - Echo remoto:
this.terminal.onData((data) => {
  if (this.ws && this.ws.readyState === WebSocket.OPEN) {
    this.ws.send(data);  // Solo enviar - PTY hace echo
  }
});

// ❌ INCORRECTO - Echo local:
this.terminal.onData((data) => {
  this.terminal.write(data);  // NO hacer echo local
  this.ws.send(data);
});
```

Si encuentras el patrón incorrecto:

```bash
git checkout feature/nodejs-pty-terminal
cd sendell-dashboard
npm run build
cd ..
.\build-dashboard.sh
```

---

## 🔄 Actualizar Código

### Pull de Git

```bash
git pull origin main
```

### Actualizar Dependencias Python

```bash
uv sync
```

### Actualizar Dependencias Node.js

```bash
cd terminal-server
npm install
cd ..
```

### Rebuild Dashboard

```bash
cd sendell-dashboard
npm run build
cd ..
.\build-dashboard.sh
```

### Reiniciar Servidores

```bash
# Ctrl+C en ambas terminales
# Luego reiniciar como en sección "Iniciar Sendell"
```

---

## 📊 Puertos Utilizados

| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| FastAPI | 8765 | HTTP | REST API + Dashboard |
| FastAPI WebSocket | 8765 | WS | Project updates |
| Node.js Terminal Server | 3000 | WS | PTY I/O |

**Firewall:** Asegúrate de que localhost pueda conectar a estos puertos.

---

## 📁 Estructura de Archivos Post-Instalación

```
sendell/
├── .env                          # Configuración (API keys)
├── .venv/                        # Virtual environment (uv)
│
├── src/sendell/                  # Python backend
│   ├── web/
│   │   ├── server.py            # FastAPI app
│   │   └── static/              # Angular build (copiado)
│   │       ├── index.html
│   │       ├── main-*.js
│   │       └── styles-*.css
│   └── ...
│
├── terminal-server/              # Node.js terminal server
│   ├── node_modules/            # Dependencias Node.js
│   ├── server.js                # PTY server
│   └── package.json
│
├── sendell-dashboard/            # Angular source
│   ├── node_modules/            # Dependencias Angular
│   ├── src/                     # Código fuente
│   └── dist/                    # Build output
│       └── sendell-dashboard/
│           └── browser/         # → copiado a src/sendell/web/static/
│
└── docs/
    ├── ARCHITECTURE.md          # Documentación arquitectura
    └── INSTALLATION_HYBRID.md  # Esta guía
```

---

## 🎯 Próximos Pasos

Después de instalar:

1. **Leer arquitectura:** `docs/ARCHITECTURE.md`
2. **Testear terminales:** Abrir dashboard, probar comandos
3. **Explorar agente:** `uv run python -m sendell chat`
4. **Ver memoria:** `uv run python -m sendell brain`

---

## 📚 Recursos Adicionales

- **Documentación oficial:** `README.md`
- **Tutorial:** `TUTORIAL.md`
- **Investigación PTY:** `docs/research/researchxtermjs.txt`
- **Plan Claude Code:** `CLAUDE_CODE_INTEGRATION_PLAN.md`

---

**¿Problemas?**

1. Revisar esta guía de troubleshooting
2. Ver logs en consola
3. Abrir issue en GitHub con:
   - OS y versión
   - Logs completos
   - Pasos para reproducir

---

**Versión:** 1.0
**Autores:** Sendell Team
**Licencia:** MIT

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
