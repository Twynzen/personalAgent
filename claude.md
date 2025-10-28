# CLAUDE.MD - Memoria Permanente del Proyecto Sendell

**Última actualización**: 2025-10-28
**Estado del proyecto**: v0.1 MVP - COMPLETADO Y FUNCIONAL
**Desarrolladores**: Daniel (Testing/PM) + Claude (Arquitectura/Desarrollo)

---

## RESUMEN EJECUTIVO DEL PROYECTO

**Sendell** es un agente autónomo AI que monitorea y controla dispositivos Windows, usando LangGraph para orquestación y psutil para monitoreo del sistema.

### Estado Actual del MVP (v0.1)
COMPLETADO. Todas las funcionalidades core están operativas:
- ✅ Monitoreo del sistema (CPU, RAM, disco) en tiempo real
- ✅ Detección de aplicación activa (respetando privacidad)
- ✅ Lista de procesos por uso de recursos
- ✅ Apertura de aplicaciones por comando
- ✅ Chat interactivo con Sendell
- ✅ GUI "Ver Cerebro" para gestionar memoria y configuración
- ✅ Sistema de autonomía L1-L5 configurable desde GUI
- ✅ Sistema de memoria JSON persistente

### Por qué este stack
- **LangGraph**: Patrón ReAct con estado persistente
- **OpenAI GPT-4**: Razonamiento avanzado
- **psutil**: Cross-platform system monitoring
- **tkinter**: GUI nativa sin dependencias adicionales

---

## ARQUITECTURA TÉCNICA REAL

### Arquitectura Implementada (Simplificada)

```
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE ORQUESTACIÓN                         │
│   LangGraph Agent (ReAct) + OpenAI GPT-4 Turbo             │
│   - Chat interactivo y loop proactivo                        │
│   - 6 herramientas (tools) directamente integradas          │
│   - Sistema de memoria JSON persistente                      │
│   - GUI tkinter para configuración                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ (Tools llamados directamente,
                      │  MCP server existe pero no activo)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              CAPA DE DISPOSITIVO                             │
│      Monitoreo y Control (psutil + pywin32)                 │
│   - Monitoreo: CPU, RAM, disco, ventanas activas           │
│   - Control: Abrir aplicaciones                             │
│   - Validación: Sistema L1-L5 de permisos                  │
└─────────────────────────────────────────────────────────────┘
```

**Nota importante**: El servidor MCP está implementado (mcp/server.py) pero NO está activo en v0.1. Las herramientas son llamadas directamente por el agente LangGraph. MCP será activado en v0.2 para extensibilidad.

### Stack Tecnológico Real

**Core Framework**:
- Python 3.10+
- LangGraph 0.2.0+ con create_react_agent
- OpenAI GPT-4 Turbo (gpt-4-turbo-preview)
- LangChain Core 0.3.0+
- Transport: Directo (tools como funciones Python)

**Sistema & Automatización**:
- psutil (cross-platform monitoring)
- pywin32 (Windows específico para ventanas)
- tkinter (GUI nativa)

**Memoria & Datos**:
- JSON persistente (data/sendell_memory.json)
- No usa bases de datos externas en v0.1
- Sistema simple y funcional

**Seguridad & Config**:
- Pydantic v2 (validación)
- python-dotenv (.env para configuración)
- Sistema L1-L5 de permisos (permissions.py)
- PII scrubbing en logs

**CLI & UX**:
- Typer (comandos CLI)
- Rich (formateo de output)

---

## ESTRUCTURA DE ARCHIVOS (ACTUAL)

```
sendell/
├── pyproject.toml              # Dependencias con uv
├── README.md                   # Documentación usuario
├── .env                        # Configuración (crear desde .env.example)
├── .env.example                # Template de configuración
├── claude.md                   # Este archivo - Memoria permanente
│
├── data/
│   └── sendell_memory.json     # Memoria persistente (facts, conversaciones)
│
├── src/
│   └── sendell/
│       ├── __init__.py
│       ├── __main__.py         # Entry: uv run python -m sendell
│       ├── config.py           # Pydantic Settings
│       │
│       ├── agent/              # 🧠 ORQUESTACIÓN
│       │   ├── __init__.py
│       │   ├── core.py         # SendellAgent con LangGraph
│       │   ├── prompts.py      # System prompts (chat, proactive, base)
│       │   ├── memory.py       # Sistema JSON de memoria
│       │   └── brain_gui.py    # GUI tkinter (3 tabs)
│       │
│       ├── mcp/                # 🔌 CAPA MCP (implementado, no activo)
│       │   ├── __init__.py
│       │   ├── server.py       # Servidor MCP (para v0.2)
│       │   └── tools/          # Implementación de herramientas
│       │       ├── __init__.py
│       │       ├── monitoring.py    # get_system_health, get_active_window
│       │       ├── process.py       # list_top_processes, open_application
│       │       └── conversation.py  # respond_to_user
│       │
│       ├── device/             # 💻 DISPOSITIVO
│       │   ├── __init__.py
│       │   ├── monitor.py      # SystemMonitor (wrapper psutil)
│       │   ├── automation.py   # AppController (abrir apps)
│       │   └── platform/
│       │       ├── __init__.py
│       │       └── windows.py  # APIs Windows (pywin32)
│       │
│       ├── security/           # 🔒 SEGURIDAD
│       │   ├── __init__.py
│       │   └── permissions.py  # L1-L5 autonomy levels
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py       # Logging con PII scrubbing
│           └── errors.py       # Excepciones custom
```

---

## FUNCIONALIDADES IMPLEMENTADAS

### 6 Herramientas Funcionales

Todas 100% operativas:

1. **get_system_health**
   - Retorna: CPU%, RAM%, Disco% con detección de umbrales
   - Uso: Monitoreo rápido del sistema
   - Permiso: L1+ (read-only)

2. **get_active_window**
   - Retorna: Título ventana, proceso, PID
   - Uso: Entender contexto del usuario
   - Permiso: L1+ (read-only)
   - Privacidad: Respeta apps bloqueadas en config

3. **list_top_processes**
   - Parámetros: n (cantidad), sort_by (memory/cpu)
   - Retorna: Top N procesos con uso de recursos
   - Uso: Identificar apps que consumen recursos
   - Permiso: L1+ (read-only)

4. **open_application**
   - Parámetros: app_name, args (opcional)
   - Uso: Abrir aplicaciones (notepad, chrome, vscode, etc.)
   - Permiso: L3+ (acción con estado)
   - Validación: Respeta apps bloqueadas

5. **respond_to_user**
   - Parámetros: message, requires_approval (bool)
   - Uso: Comunicación proactiva del agente
   - Permiso: Siempre permitido

6. **show_brain** (NUEVO en v0.1)
   - Sin parámetros
   - Abre GUI tkinter para gestionar memoria y config
   - Tabs: Memorias, Prompts, Herramientas
   - Permite configurar autonomía L1-L5 desde GUI
   - Uso: "show me your brain", "open brain interface"

### Sistema de Permisos (L1-L5) - CONFIGURABLE

**Configurable desde**: `sendell brain` -> Tab Memorias -> Selector desplegable

- **L1 - Monitor Only**: Solo observar, nunca actuar
- **L2 - Ask Permission**: Preguntar antes de cualquier acción (DEFAULT)
- **L3 - Safe Actions**: Auto-ejecutar acciones seguras (abrir apps)
- **L4 - Modify State**: Cerrar apps, modificar archivos
- **L5 - Full Autonomy**: Autonomía completa (peligroso)

**Cómo funciona**:
1. Usuario selecciona nivel en GUI
2. Nivel se guarda en .env (SENDELL_AUTONOMY_LEVEL)
3. Agente debe reiniciarse para aplicar cambios
4. Cada tool valida permisos antes de ejecutar

### Sistema de Memoria (JSON)

**Ubicación**: `data/sendell_memory.json`

**Estructura**:
```json
{
  "facts": [
    {
      "fact": "Daniel trabaja en AI",
      "category": "work",
      "learned_at": "2025-10-28T14:30:00"
    }
  ],
  "preferences": {
    "favorite_apps": ["vscode"],
    "work_hours": "14:00-18:00"
  },
  "conversations": [
    {
      "timestamp": "2025-10-28T14:35:00",
      "messages": [...]
    }
  ],
  "sessions": [
    {
      "start": "2025-10-28T14:00:00",
      "end": "2025-10-28T15:00:00",
      "actions_taken": 5
    }
  ]
}
```

**Estado actual (v0.1)**:
- ✅ Estructura JSON implementada
- ✅ CRUD de facts desde GUI
- ✅ Persistencia en disco
- ⏳ Auto-aprendizaje de facts (v0.2)
- ⏳ Facts cargados automáticamente en conversaciones (v0.2)

### GUI "Ver Cerebro" (brain_gui.py)

**Cómo abrir**:
- Comando: `uv run python -m sendell brain`
- Chat: "show me your brain", "open brain interface"

**Tab 1: MEMORIAS**
- Vista de facts aprendidos con categoría y fecha
- Botón "Agregar Fact" para añadir manualmente
- Botón "Eliminar Fact" para borrar seleccionado
- Estadísticas: Total facts, conversaciones, sesiones
- **SELECTOR DE AUTONOMÍA**: Dropdown L1-L5 con botón "Guardar Nivel"

**Tab 2: PROMPTS**
- Vista/edición del system prompt completo
- Permite personalizar personalidad de Sendell
- Botón "Guardar Prompt"
- Nota: Reiniciar agente para aplicar cambios

**Tab 3: HERRAMIENTAS**
- Lista de las 6 herramientas disponibles
- Muestra nombre y descripción de cada una
- Read-only (informativo)

### Comandos CLI Disponibles

```powershell
# Chequeo rápido del sistema (sin agente)
uv run python -m sendell health

# Chat interactivo (COMANDO PRINCIPAL)
uv run python -m sendell chat

# Abrir GUI de configuración/memoria
uv run python -m sendell brain

# Loop proactivo OODA (testing)
uv run python -m sendell start --interval 30 --max-cycles 3

# Ver versión
uv run python -m sendell version
```

---

## DECISIONES ARQUITECTÓNICAS IMPORTANTES

### 1. LangGraph create_react_agent - CORRECCIÓN CRÍTICA

**Error inicial**: Usé parámetro `state_modifier` que no existe
**Corrección**: El parámetro correcto es `prompt` (acepta string, se convierte automáticamente a SystemMessage)

```python
# CORRECTO
self.agent = create_react_agent(
    self.llm,
    self.tools,
    prompt=get_system_prompt(),  # String convertido a SystemMessage
)

# INCORRECTO (no existe)
self.agent = create_react_agent(
    self.llm,
    self.tools,
    state_modifier=...,  # Error!
)
```

**Aprendizaje**: No asumir APIs sin verificar documentación oficial.

### 2. MCP Server: Implementado pero No Activo

**Decisión**: Tools llamados directamente por LangGraph, MCP server existe pero no se usa en v0.1
**Razón**:
- Simplicidad para MVP
- Menos overhead
- MCP será activado en v0.2 para permitir extensibilidad (plugins externos)

**Ubicación**: `src/sendell/mcp/server.py` (listo para activarse)

### 3. Memoria JSON vs Base de Datos

**Decisión**: JSON simple en v0.1
**Razón**:
- Rapidez de desarrollo
- Sin dependencias adicionales
- Suficiente para MVP
- PostgreSQL/SQLite en v0.2+ si es necesario

### 4. Encoding: Solo ASCII

**Decisión**: Todos los archivos Python usan solo ASCII
**Razón**: Windows tuvo problemas con UTF-8 fancy characters (→, ✅, ⚠️)
**Implementación**:
- Flechas: -> en lugar de →
- Status: [OK], [!] High en lugar de ✅, ⚠️
- Sin emojis en código

**Errores resueltos**:
- UnicodeDecodeError en README.md (byte 0xd3)
- UnicodeDecodeError en core.py (byte 0x92)
- UnicodeDecodeError en __main__.py (byte 0xa0)

### 5. GUI con tkinter

**Decisión**: tkinter para GUI (no Electron, no web)
**Razón**:
- Incluido en Python (sin dependencias)
- Nativo
- Suficiente para gestión de config y memoria

### 6. Agente Único (No Multi-Agente)

**Decisión**: Un solo agente bien diseñado
**Razón**: Research de Anthropic muestra que multi-agente usa 15x más tokens con beneficios marginales

---

## CONFIGURACIÓN (.env)

```bash
# OpenAI (OBLIGATORIO)
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview

# Agente
SENDELL_AUTONOMY_LEVEL=2  # L1-L5 (configurable desde GUI)
SENDELL_LOOP_INTERVAL=60  # Segundos para loop proactivo
SENDELL_PROACTIVE_MODE=true

# Privacidad
SENDELL_BLOCKED_APPS=1password,keepass,banking
SENDELL_SCRUB_PII=true

# Logs
SENDELL_LOG_LEVEL=INFO

# LangChain (opcional)
LANGCHAIN_TRACING_V2=false
```

**IMPORTANTE**: No editar .env manualmente para autonomía. Usar `sendell brain` -> Tab Memorias -> Selector.

---

## DEPENDENCIAS REALES (pyproject.toml)

```toml
[project]
name = "sendell"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    # Core LangGraph
    "langgraph>=0.2.0",
    "langchain-core>=0.3.0",
    "langchain-openai>=0.2.0",
    "openai>=1.0.0",

    # MCP (implementado, no activo en v0.1)
    "mcp>=0.9.0",

    # System Monitoring
    "psutil>=5.9.0",
    "pywin32>=306; sys_platform == 'win32'",

    # Configuration
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",

    # CLI & UX
    "typer>=0.9.0",
    "rich>=13.0.0",
]
```

**Instalación**: `uv sync`

---

## SEGURIDAD Y PRIVACIDAD

### Implementado en v0.1

- ✅ Input validation con Pydantic
- ✅ Sistema L1-L5 de permisos
- ✅ subprocess con shell=False (automation.py)
- ✅ PII scrubbing en logs (emails, teléfonos, tarjetas)
- ✅ Apps bloqueadas configurables
- ✅ Credenciales en .env (nunca hardcoded)
- ✅ Solo lee metadatos (títulos ventanas), nunca contenido

### Lo que Sendell NUNCA hace

- ❌ Leer contenido de ventanas (solo títulos)
- ❌ Monitorear apps bloqueadas
- ❌ Guardar contraseñas
- ❌ Enviar datos a terceros (excepto OpenAI API para LLM)
- ❌ Telemetry sin opt-in

---

## SYSTEM PROMPT DEL AGENTE (prompts.py)

**3 tipos de prompts**:

1. **Base System Prompt**: Define personalidad y capacidades
2. **Chat Mode Prompt**: Para modo interactivo
3. **Proactive Loop Prompt**: Para ciclos OODA automáticos

**Editable desde**: `sendell brain` -> Tab Prompts -> Editar y guardar

**Contenido clave del prompt**:
- Personalidad: Helpful, proactive, non-intrusive
- Capacidades: 6 herramientas documentadas
- Restricciones: Respetar privacidad, explicar acciones
- Decision framework basado en nivel L1-L5
- Apps bloqueadas: Nunca acceder

---

## ROADMAP DE DESARROLLO

### ✅ v0.1 (COMPLETADO - Octubre 2025)

- ✅ Setup completo del proyecto
- ✅ 6 herramientas operativas
- ✅ Chat interactivo funcional
- ✅ Health check rápido
- ✅ Sistema de memoria JSON
- ✅ GUI "Ver Cerebro" con 3 tabs
- ✅ Configuración de autonomía desde GUI
- ✅ Sistema L1-L5 implementado
- ✅ CLI con Typer + Rich
- ✅ Documentación completa (README + claude.md)

### 🔜 v0.2 (Próximo - 2-3 semanas)

- [ ] Memoria conversacional persistente
- [ ] Facts cargados automáticamente en contexto
- [ ] Auto-aprendizaje de facts desde conversaciones
- [ ] Checkpointer de LangGraph
- [ ] Más herramientas:
  - take_screenshot
  - manage_projects (track proyectos activos)
  - control_music
- [ ] Activar servidor MCP para extensibilidad

### 🔮 v0.3 (Futuro - 1-2 meses)

- [ ] Integración email (lectura, envío)
- [ ] Integración calendario (eventos, recordatorios)
- [ ] Sistema de plugins/skills extensible
- [ ] Análisis de productividad
- [ ] Event listeners (en lugar de polling)

### 🚀 v1.0 (Largo plazo - 3-6 meses)

- [ ] Servidor MCP HTTP (multi-dispositivo)
- [ ] Sincronización de contexto entre dispositivos
- [ ] macOS support
- [ ] Opción de modelos locales (Llama, Mistral)

---

## LOG DE PROGRESO

### Sesión 1 (2025-10-24): Planificación

- ✅ Lectura de sendellguia.txt
- ✅ Creación de claude.md
- ✅ Arquitectura de 3 capas definida
- ✅ Todo list inicial

### Sesión 2 (2025-10-24): Setup Estructura

- ✅ Creación estructura de carpetas completa
- ✅ pyproject.toml con todas las dependencias
- ✅ .env.example y config.py con Pydantic
- ✅ .gitignore configurado

### Sesión 3 (2025-10-24): Implementación Core

- ✅ device/monitor.py - Wrapper psutil
- ✅ device/automation.py - Control de apps
- ✅ device/platform/windows.py - APIs Windows
- ✅ security/permissions.py - Sistema L1-L5
- ✅ utils/logger.py - PII scrubbing
- ✅ utils/errors.py - Excepciones custom

### Sesión 4 (2025-10-24): Herramientas MCP

- ✅ mcp/tools/monitoring.py - get_system_health, get_active_window
- ✅ mcp/tools/process.py - list_top_processes, open_application
- ✅ mcp/tools/conversation.py - respond_to_user
- ✅ mcp/server.py - Servidor MCP completo

### Sesión 5 (2025-10-24): Agente LangGraph

- ✅ agent/prompts.py - System prompts
- ✅ agent/core.py - SendellAgent con create_react_agent
- ✅ __main__.py - CLI con 4 comandos
- ✅ README.md inicial

### Sesión 6 (2025-10-25): Resolución de Errores

**Error 1**: UnicodeDecodeError en README.md
- Causa: Caracteres fancy Unicode
- Solución: Recrear con ASCII puro

**Error 2**: UnicodeDecodeError en agent/core.py
- Causa: Flechas → en docstrings
- Solución: Cambiar a ->

**Error 3**: UnicodeDecodeError en __main__.py
- Causa: Emojis (✅, ⚠️)
- Solución: Cambiar a [OK], [!] High
- **Aprendizaje**: Solo ASCII en código

### Sesión 7 (2025-10-25): Testing Inicial

- ✅ `sendell health` funcionó correctamente
- ✅ Tabla con CPU, RAM, Disco mostrada
- ⚠️ Error en `sendell chat`: create_react_agent parámetro incorrecto

### Sesión 8 (2025-10-25): Corrección LangGraph

**Error**: create_react_agent() got unexpected keyword argument 'state_modifier'
- Daniel proporcionó langgraph.txt con documentación oficial
- Corrección: Cambiar a parámetro `prompt`
- ✅ Chat funcionó correctamente después del fix

### Sesión 9 (2025-10-26): Análisis Profundo

- Daniel preguntó sobre capacidades de Sendell
- Explicación: MCP server existe pero no está activo
- Explicación: Memoria no persistente aún en conversaciones
- Discusión sobre evolución futura

### Sesión 10 (2025-10-26): GUI "Ver Cerebro"

**Idea de Daniel**: Interfaz gráfica para gestionar memoria
- ✅ agent/memory.py - Sistema JSON de memoria
- ✅ agent/brain_gui.py - GUI tkinter con 3 tabs
- ✅ show_brain() como 6ta herramienta
- ✅ Actualización mcp/server.py para incluir show_brain
- ✅ Comando CLI: `sendell brain`

**Tabs implementados**:
1. Memorias: CRUD de facts + estadísticas
2. Prompts: Ver/editar system prompt
3. Herramientas: Lista de 6 tools

### Sesión 11 (2025-10-27): Configuración de Autonomía

**Problema**: Daniel en L2, Sendell no pudo abrir notepad
- No es bug, es diseño (L2 requiere aprobación)
- Daniel: "quiero que eso sea configurable en la mente"

**Solución**:
- ✅ Agregado selector de autonomía en Tab Memorias de GUI
- ✅ Dropdown con opciones L1-L5
- ✅ Función save_autonomy_level() para escribir en .env
- ✅ Mensajes claros al usuario sobre reinicio

### Sesión 12 (2025-10-28): Optimización Documentación

**Tarea de Daniel**: "mejora y optimiza la documentacion del software el readme y el calude.md borrando lo que no sirve y entendiendo en su totalidad el proyecto bien supremamente claro ultrathink"

**Completado**:
- ✅ README.md completamente reescrito
  - Enfoque práctico y claro
  - Eliminada info desactualizada
  - Secciones por comandos
  - Troubleshooting y FAQ
  - Bilingual-friendly
- ✅ claude.md optimizado (este archivo)
  - Reflejando estado REAL del proyecto
  - Todas las features documentadas
  - Log de progreso completo
  - Decisiones arquitectónicas con aprendizajes

---

## LECCIONES APRENDIDAS

### 1. Encoding en Windows
**Problema**: Python en Windows con UTF-8 fancy characters
**Solución**: Solo ASCII en archivos Python
**Aplicar siempre**: Evitar →, emojis, caracteres especiales en código

### 2. Verificar Documentación Oficial
**Problema**: Asumí API de create_react_agent sin verificar
**Solución**: Daniel proporcionó docs oficiales
**Aplicar siempre**: No adivinar APIs, revisar docs primero

### 3. MVP Simple Funciona
**Problema**: Tendencia a sobre-complicar arquitectura
**Solución**: JSON simple, tools directos, sin MCP activo
**Resultado**: v0.1 completado y funcional rápidamente

### 4. GUI Aumenta Usabilidad
**Problema**: Configurar autonomía requería editar .env manualmente
**Solución**: GUI con selector visual
**Resultado**: Mejor UX, menos errores de usuario

### 5. Testing Iterativo
**Workflow**: Daniel testea -> reporta error -> Claude corrige -> documenta
**Resultado**: Errores resueltos rápidamente, aprendizaje documentado

---

## PREGUNTAS RESPONDIDAS

### Durante desarrollo (ya resueltas):

1. **API Key**: ✅ Daniel tiene OpenAI API key configurada
2. **Permisos**: ✅ Default L2, configurable desde GUI
3. **Apps bloqueadas**: ✅ Configurables en .env (password managers, banking)
4. **Testing**: ✅ Daniel testea, Claude implementa y ajusta
5. **Lenguaje**: ✅ Documentación bilingüe, código en inglés

---

## RECURSOS Y REFERENCIAS

### Documentación Usada
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangGraph create_react_agent: langgraph.txt (proporcionado por Daniel)
- MCP Protocol: https://modelcontextprotocol.io/
- psutil: https://psutil.readthedocs.io/
- Pydantic: https://docs.pydantic.dev/

### Proyectos de Referencia
- AutoGPT: Arquitectura de agente autónomo
- Open Interpreter: UX conversacional

---

## CONTACTO Y COLABORACIÓN

**Workflow establecido**:
1. ✅ Claude implementa según plan y feedback
2. ✅ Daniel prueba funcionalidad (comandos health, chat, brain)
3. ✅ Daniel reporta bugs o solicita features
4. ✅ Claude ajusta y documenta en claude.md
5. ✅ Repetir hasta objetivo completado

**Comunicación**:
- claude.md es la memoria permanente (fuente de verdad)
- Daniel proporciona docs cuando es necesario (ej: langgraph.txt)
- Documentación optimizada y clara para continuidad

---

## PRÓXIMOS PASOS INMEDIATOS

### Para v0.2 (Siguiente milestone):

1. **Memoria conversacional persistente**
   - Cargar facts en contexto automáticamente
   - LangGraph checkpointer para mantener conversaciones

2. **Auto-aprendizaje**
   - Extraer facts automáticamente de conversaciones
   - Categorizar facts inteligentemente

3. **Más herramientas**
   - take_screenshot: Capturar pantalla cuando sea útil
   - manage_projects: Track proyectos activos de Daniel
   - control_music: Control de Spotify/media

4. **Activar MCP Server**
   - Permitir plugins externos
   - Extensibilidad para terceros

---

**FIN DE MEMORIA PERMANENTE**

Este archivo refleja el estado REAL del proyecto Sendell v0.1.
Última actualización: 2025-10-28
Estado: MVP COMPLETADO Y FUNCIONAL
