# CLAUDE.MD - Memoria Permanente del Proyecto Sendell

**Última actualización**: 2025-10-29 22:20
**Estado del proyecto**: v0.2 Fase 2A en desarrollo - Sistema de Notificaciones Visuales
**Desarrolladores**: Daniel (Testing/PM) + Claude (Arquitectura/Desarrollo)

---

## 🚨 ESTADO ACTUAL DEL DESARROLLO (Para Reinicio de Contexto)

**Branch actual**: `feature/ui-foundation` (Branch 1 de Fase 2A completado, pendiente push)
**Siguiente**: Crear `feature/ascii-art-library` (Branch 2 de Fase 2A)

**Workflow establecido**:
1. Claude crea branch para tarea específica
2. Claude desarrolla código
3. Claude muestra código a Daniel para testing
4. Daniel testea y da feedback ("funciona" o "ajusta X")
5. Si funciona → Claude hace commit con mensaje descriptivo
6. Daniel hace push
7. Repetir para siguiente branch
8. Documentar SIEMPRE en CLAUDE.md

**Fase actual**: Fase 2A - Sistema de Notificaciones Visuales (6 branches totales)
- ✅ Branch 1: UI Foundation (COMPLETADO - pendiente push por Daniel)
- ⏳ Branch 2: ASCII Art Library (SIGUIENTE - por iniciar)
- ⏳ Branch 3: Notification Levels + Sounds
- ⏳ Branch 4: Snooze/Dismiss Integration
- ⏳ Branch 5: Reminder System Integration
- ⏳ Branch 6: Brain GUI Customization

**Contexto de Fase 2A**:
Daniel testeó sistema de reminders (v0.2 Fase 1) y pidió mejoras:
- Reminders actuales abren notepad (funciona pero muy simple)
- Necesita: Ventanas visuales llamativas con ASCII art, colores, sonidos
- Objetivo: Hacer notificaciones más impactantes y personalizadas

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

## ESTRUCTURA DE ARCHIVOS (ACTUAL - 2025-10-29)

```
sendell/
├── pyproject.toml              # Dependencias con uv
├── README.md                   # Documentación usuario
├── CLAUDE.md                   # Este archivo - Memoria permanente
├── .env                        # Configuración (crear desde .env.example)
├── .env.example                # Template de configuración
├── test_notification.py        # Testing script para UI (v0.2 Fase 2A)
│
├── data/
│   └── sendell_memory.json     # Memoria persistente (facts, conversaciones, reminders, identity)
│
├── src/
│   └── sendell/
│       ├── __init__.py
│       ├── __main__.py         # Entry: uv run python -m sendell (comandos: chat, status, brain, health)
│       ├── config.py           # Pydantic Settings
│       │
│       ├── agent/              # 🧠 ORQUESTACIÓN
│       │   ├── __init__.py
│       │   ├── core.py         # SendellAgent con LangGraph (7 tools)
│       │   ├── prompts.py      # System prompts (chat, proactive, base)
│       │   ├── memory.py       # Sistema JSON de memoria
│       │   └── brain_gui.py    # GUI tkinter (3 tabs: Memorias, Prompts, Herramientas)
│       │
│       ├── proactive/          # ⏰ SISTEMA PROACTIVO (v0.2 Fase 1)
│       │   ├── __init__.py
│       │   ├── identity.py              # AgentIdentity, RelationshipPhase
│       │   ├── temporal_clock.py        # TimeContext, optimal timing
│       │   ├── reminders.py             # Reminder, ReminderManager
│       │   ├── reminder_actions.py      # popup, notepad, sound, chat_message
│       │   └── proactive_loop.py        # ProactiveLoop asyncio background
│       │
│       ├── ui/                 # 🎨 SISTEMA UI (v0.2 Fase 2A - EN DESARROLLO)
│       │   ├── __init__.py              # ✅ Branch 1 completado
│       │   └── notification_window.py   # ✅ NotificationWindow con 4 niveles
│       │
│       ├── mcp/                # 🔌 CAPA MCP (implementado, no activo)
│       │   ├── __init__.py
│       │   ├── server.py       # Servidor MCP (para v0.2+)
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

## DESARROLLO ACTUAL: RAMA feature/proactivity

### Sesión 13 (2025-10-28): Inicio de Proactividad

**Objetivo**: Evolucionar Sendell de agente reactivo a agente proactivo con identidad temporal.

**Visión**: Sendell debe ser un compañero que vive contigo, no solo un asistente que espera comandos. Enfoque en el **usuario como persona**, no solo su trabajo.

**Documentos de referencia**:
- `proactividad.txt` - Arquitectura de proactividad (sistemas, fases, identidad)
- `iapersonal.txt` - Stack tecnológico y arquitectura completa
- `PROACTIVITY_DESIGN.md` - Diseño detallado de implementación

**Branch creado**: `feature/proactivity`

**5 Sistemas Core a implementar**:

1. **Sistema de Identidad Temporal**
   - Agente tiene "birth_date" y conoce hace cuánto vive
   - Fases de evolución: Birth (días 1-7), Adolescence (8-30), Maturity (31-60), Mastery (60+)
   - Ejemplo: "Es mi 5to día contigo, aún estoy aprendiendo tu ritmo"

2. **Sistema de Reloj Interno**
   - Sendell concibe el tiempo como recurso útil
   - Contextos: morning_routine, work_hours, evening_routine, sleep_time
   - Trackea uso del tiempo del usuario

3. **Sistema de Memoria Personal Expandida**
   - Más allá de facts: hábitos, rutinas, proyectos personales, familia
   - Ejemplo: "Abuela María", hábito "Llamar a la abuela" semanal
   - Patrones detectados: procrastinación, preferencias

4. **Sistema de Recordatorios Personales**
   - One-time: "Recuérdame llamar al doctor mañana 10am"
   - Recurring: "Recuérdame llamar a mi abuela todos los domingos"
   - Conditional: "Recuérdame revisar proyecto X cuando tenga tiempo libre"

5. **Sistema de Atención Temporal Adaptativo**
   - No check-ins fijos, sino cálculo dinámico de urgencia
   - Urgency scoring 0-1 basado en: deadlines, hábitos, patrones, contexto
   - Conversión urgencia a timing: 0.9 = 15min, 0.5 = 4h, 0.2 = mañana

**Implementación por fases (5 semanas)**:

**Fase 1 (Semana 1)**: Fundación
- identity.py: AgentIdentity con birth_date, relationship_age, phase
- temporal_clock.py: Reloj interno con time contexts
- Actualizar memoria JSON con agent_identity
- Validación: "Cuánto tiempo llevas conmigo?" -> "Es mi 5to día contigo"

**Fase 2 (Semana 2)**: Memoria Personal
- personal_memory.py: Habit, Routine, PersonalProject, Goal
- GUI: Tab "Vida Personal" en brain_gui
- CRUD de hábitos y rutinas
- Validación: Agregar hábito "Llamar a la abuela" semanal

**Fase 3 (Semana 3)**: Recordatorios Básicos
- reminders.py: Reminder con tipos (one_time, recurring, conditional)
- Trigger system para time-based
- Integración con loop proactivo
- Validación: "Recuérdame X mañana" -> se dispara correctamente

**Fase 4 (Semana 4)**: Urgency Scoring
- attention_system.py: calculate_urgency_score, urgency_to_next_interaction
- Factores: deadlines, hábitos overdue, patrones, tiempo óptimo
- Validación: Intervenciones oportunas, no spam

**Fase 5 (Semana 5)**: Loop Proactivo Completo
- proactive_loop.py: Loop con todos los sistemas integrados
- daily_reflection: Reflexión al final del día
- Sistema de feedback: ¿Esto te ayudó?
- Validación: Dejar correr 7 días, medir utilidad vs molestia

**Nuevos módulos**:
```
src/sendell/proactive/
├── identity.py              # AgentIdentity, relationship phases
├── temporal_clock.py        # Reloj interno, time awareness
├── personal_memory.py       # Memoria personal expandida
├── reminders.py             # Sistema de recordatorios
├── attention_system.py      # Urgency scoring, timing optimizer
└── proactive_loop.py        # Loop principal proactivo
```

**Principios de diseño**:
- ✅ Respeto al usuario: 1 intervención valiosa > 10 molestas
- ✅ Transparencia: Explica por qué actúa
- ✅ Evolución gradual: Días 1-7 tímido, días 30+ anticipatorio
- ✅ Medición: Track utilidad de intervenciones, aprende del feedback

**Métricas de éxito v0.2**:
- ✅ Intervenciones proactivas útiles >80%
- ✅ Falsos positivos (molestias) <10%
- ✅ 95%+ recordatorios se disparan a tiempo
- ✅ Usuario siente que Sendell "lo conoce"

---

## PRÓXIMOS PASOS INMEDIATOS

### Para v0.2 (En desarrollo - rama feature/proactivity):

**PRIORIDAD 1: Proactividad (5 semanas)**
1. **Identidad temporal y reloj interno** (Semana 1)
2. **Memoria personal expandida** (Semana 2)
3. **Sistema de recordatorios** (Semana 3)
4. **Urgency scoring** (Semana 4)
5. **Loop proactivo completo** (Semana 5)

**PRIORIDAD 2: Integración (después de proactividad)**
- Memoria conversacional persistente con checkpointer
- Auto-aprendizaje de facts desde conversaciones
- Activar servidor MCP para extensibilidad

**FUTURO v0.3+**:
- Detección automática de patrones
- Integración Google Calendar/Email
- Análisis de productividad
- take_screenshot, manage_projects, control_music

### Sesión 14 (2025-10-28): Fase 1 Completada - Sistema Proactivo Funcionando

**Estado**: ✅ **FASE 1 COMPLETADA AL 100% Y TESTEADA**

**Commit**: `4917bbb` - "feat: Complete proactive system integration - Phase 1 100%"

**Lo implementado**:

#### 1. Módulos Core (Commit anterior: 125e911)
- ✅ `identity.py` (270 líneas) - AgentIdentity con birth_date, phases, milestones
- ✅ `temporal_clock.py` (200 líneas) - Contextos temporales, optimal timing
- ✅ `reminders.py` (370 líneas) - Sistema completo de reminders (one-time, recurring)
- ✅ `reminder_actions.py` (240 líneas) - Acciones ejecutables (popup, notepad, sound)
- ✅ `proactive_loop.py` (180 líneas) - Loop background asyncio
- ✅ `memory.py` actualizado - Soporte para agent_identity y reminders

#### 2. Integración Core (Esta sesión)
- ✅ **core.py** (+100 líneas):
  - Inicializa todos los componentes proactivos en `__init__()`
  - Tool `add_reminder` agregado (7mo tool del agente)
  - Método `add_reminder_from_chat()` para crear reminders desde conversación
  - Callback `_on_reminder_triggered()` para gestionar disparos
  - Método `get_proactive_status()` para queries de estado

- ✅ **__main__.py** (+60 líneas):
  - Banner v0.2 "Autonomous & Proactive AI Assistant"
  - Comando `status` - muestra identity, loop status, upcoming reminders
  - Chat auto-inicia proactive loop en background
  - Input no-bloqueante con `asyncio.to_thread()` - permite loop independiente
  - Cleanup graceful al salir (stop loop)

#### 3. Optimizaciones Críticas
- ✅ **Loop independiente**: No bloquea chat, corre cada 60s
- ✅ **Logging limpio**: Verbosidad movida a DEBUG, solo INFO para eventos importantes
- ✅ **UI no invasiva**: Solo muestra "⏰ Processing N reminder(s)..." cuando hay acción
- ✅ **Persistencia robusta**: Estado guardado en `data/sendell_memory.json`

#### 4. Testing Exitoso ✅
```
✅ Reminder de 2 minutos con popup → FUNCIONA
✅ Reminder con múltiples acciones (popup + notepad + sound) → FUNCIONA
✅ Loop corre independiente sin bloquear input → FUNCIONA
✅ UI limpia sin spam de logs → FUNCIONA
✅ Persistencia correcta entre sesiones → FUNCIONA
```

**Ejemplo de uso**:
```
You: Remind me to test in 2 minutes with popup and notepad

Sendell: [usa tool add_reminder]
✅ Reminder set: 'test' at 10:42 PM (in 2 min) with actions: ['popup', 'notepad']

[Después de 2 minutos, automáticamente:]
⏰ Processing 1 reminder(s)...
✅ Reminder: 'test' → popup, notepad
[Popup de Windows aparece + Notepad se abre]
```

**Comandos disponibles**:
```bash
uv run python -m sendell chat    # Chat con loop proactivo auto-activado
uv run python -m sendell status  # Ver identity, loop status, reminders
```

**Resultado status**:
```
Agent Identity
  Age: 0 days
  Phase: birth
  Confidence: 0.00

Proactive Loop
  Running: Yes/No
  Check interval: 60s
  Cycles run: X
  Reminders triggered: Y

Reminders
  Total: N
  Due now: M
  Upcoming (24h): K

Upcoming Reminders (next 24h)
  - test at 10:42 PM (popup, notepad)
```

**Arquitectura final Fase 1**:
```
src/sendell/proactive/
├── __init__.py              ✅ Exports
├── identity.py              ✅ AgentIdentity, RelationshipPhase
├── temporal_clock.py        ✅ TimeContext, optimal timing
├── reminders.py             ✅ Reminder, ReminderManager, ReminderType
├── reminder_actions.py      ✅ popup, notepad, sound, chat_message
└── proactive_loop.py        ✅ ProactiveLoop, asyncio background
```

**Métricas**:
- 🎯 ~1500 líneas de código nuevo
- 🎯 6 módulos core + integración en 2 archivos principales
- 🎯 2 sesiones de desarrollo + debugging
- 🎯 Testing manual 100% exitoso

**Decisiones técnicas clave**:
1. **asyncio.to_thread()** para input no-bloqueante → loop puede correr libremente
2. **Logging en niveles** (DEBUG vs INFO) → UI limpia
3. **Tool approach** para reminders → LLM puede parsear lenguaje natural
4. **60s check interval** → balance entre reactividad y performance
5. **JSON persistence** → simple, funcional, extensible

**Próximos pasos recomendados**:

**Opción A - Merge y Validación** (RECOMENDADO):
1. Merge `feature/proactivity` → `main`
2. Tag release `v0.2.0`
3. Usar en producción por 3-7 días
4. Recopilar feedback real
5. Ajustar basándose en uso real

**Opción B - Continuar desarrollo**:
1. Fase 2: Hábitos y Rutinas (2-3 sesiones)
2. Fase 3: Proyectos Personales (2 sesiones)
3. Fase 4: Personalidad Evolutiva (2 sesiones)

**Documentación actualizada**:
- ✅ `IMPLEMENTATION_STATUS.md` - Estado completo, roadmap Fase 2-5
- ✅ Commit detallado con changelog completo
- ✅ `claude.md` actualizado (esta entrada)

### Sesión 15 (2025-10-29): Inicio Fase 2A - Sistema de Notificaciones Visuales

**Objetivo**: Mejorar UX de reminders con ventanas visuales llamativas en lugar de notepad simple.

**Contexto**: Daniel testeó sistema de reminders y feedback fue:
- ✅ Notepad funciona pero es muy simple
- ❌ Necesita algo más llamativo y visual
- 💡 Propuesta: Ventanas con ASCII art, colores, sonidos, niveles de urgencia

**Roadmap Fase 2A** (6 tareas):
1. UI Foundation (ventanas base)
2. ASCII Art Library
3. Sistema de niveles con sonidos
4. Botones Snooze/Dismiss funcionales
5. Integración con reminders
6. Customización desde brain GUI

---

#### Branch 1: `feature/ui-foundation` - ✅ COMPLETADO

**Objetivo**: Estructura base del módulo UI con ventanas de notificación

**Implementación**:
- Creado módulo `src/sendell/ui/`
- `notification_window.py` (272 líneas):
  - Clase `NotificationLevel` (Enum: INFO, ATTENTION, URGENT, AVATAR)
  - Clase `NotificationWindow` (ventana tkinter completa)
  - 4 niveles con diferentes colores, tamaños, comportamiento
  - Sistema de callbacks (on_dismiss, on_snooze)
  - Auto-centrado en pantalla
  - Topmost para niveles urgentes

**Características por nivel**:
| Nivel | Color | Tamaño | Topmost | Botones |
|-------|-------|--------|---------|---------|
| INFO | Azul | 400x250 | No | Dismiss |
| ATTENTION | Naranja | 500x350 | Sí | Dismiss + Snooze |
| URGENT | Rojo | 600x400 | Sí | Dismiss + Snooze |
| AVATAR | Morado | 500x400 | Sí | Dismiss |

**Testing**:
- Script `test_notification.py` creado para testing manual
- Daniel testeó todos los niveles: "funciona bastante bien"
- ✅ Todas las ventanas se abren correctamente
- ✅ Colores y tamaños apropiados
- ✅ Botones responden correctamente
- ✅ Topmost funciona en niveles correctos

**Commit**: `9b5f2a4` - "feat: Add UI notification window system (Phase 2A - Task 1)"

**Archivos creados**:
- `src/sendell/ui/__init__.py`
- `src/sendell/ui/notification_window.py` (272 líneas)
- `test_notification.py` (152 líneas)

**Próximo paso**: Branch 2 - ASCII Art Library

---

**FIN DE MEMORIA PERMANENTE**

Este archivo refleja el estado REAL del proyecto Sendell.
Última actualización: 2025-10-29 22:15 (Sesión 15 - Branch 1 Fase 2A completado)
Estado: v0.1 MVP COMPLETADO - v0.2 FASE 1 COMPLETADA - v0.2 FASE 2A INICIADA ✅
