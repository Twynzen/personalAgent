# Sendell - Tu Asistente AI Personal

**Version**: 0.1.0 MVP
**Estado**: Funcional
**Desarrollador**: Daniel

Sendell es tu agente AI autónomo que monitorea tu sistema Windows, te ayuda con tareas, y aprende sobre ti. Es tu Jarvis personal.

---

## Lo que hace Sendell AHORA (100% funcional)

- Monitorea CPU, RAM, Disco en tiempo real
- Ve qué aplicación estás usando (respetando privacidad)
- Lista procesos que consumen recursos
- Abre aplicaciones por comando
- Conversa contigo inteligentemente
- Tiene una "mente" visual donde puedes gestionar su memoria y configuración
- Se adapta según el nivel de autonomía que le des (L1-L5)

---

## Instalación Rápida

### 1. Requisitos
- Windows 10/11
- Python 3.10+
- OpenAI API Key

### 2. Instalar
```powershell
cd C:\Users\Daniel\Desktop\Daniel\sendell
uv sync
copy .env.example .env
notepad .env  # Pega tu OPENAI_API_KEY
```

### 3. Probar
```powershell
uv run python -m sendell health
```

Si ves una tabla con CPU/RAM/Disco, está listo.

---

## Cómo Usar Sendell

### Comando 1: `sendell health`
**Qué hace**: Chequeo rápido del sistema (sin agente)

```powershell
uv run python -m sendell health
```

**Salida**: Tabla con CPU%, RAM%, Disco%

---

### Comando 2: `sendell chat` (EL PRINCIPAL)
**Qué hace**: Chat interactivo con Sendell

```powershell
uv run python -m sendell chat
```

**Ejemplos de lo que puedes decirle:**

```
You: "How's my system?"
Sendell: CPU 25%, RAM 89% (alta), Disco 89%

You: "What's using all my RAM?"
Sendell: Top 3: Chrome (1.5GB), VS Code (800MB)...

You: "Open notepad"
Sendell: [Si nivel >= L3] Abre notepad directamente
        [Si nivel = L2] Pide tu aprobación primero

You: "Show me your brain"
Sendell: Abre GUI para gestionar memoria y config
```

**Comandos especiales en el chat:**
- `/health` - Health check rápido
- `/help` - Ayuda
- `/quit` - Salir

---

### Comando 3: `sendell brain` (NUEVO - IMPORTANTE)
**Qué hace**: Abre la interfaz gráfica de Sendell

```powershell
uv run python -m sendell brain
```

**GUI con 3 pestañas:**

#### Tab 1: MEMORIAS
- **Facts aprendidos**: Lo que Sendell sabe de ti
- **Agregar/Eliminar facts** manualmente
- **Estadísticas**: Total de facts, conversaciones, sesiones
- **⭐ CONFIGURAR AUTONOMÍA**: Cambia entre L1-L5 aquí

#### Tab 2: PROMPTS
- **Ver/Editar** el system prompt que define a Sendell
- Personaliza su personalidad y comportamiento
- Guarda y reinicia para aplicar cambios

#### Tab 3: HERRAMIENTAS
- Lista de las **6 acciones** que Sendell puede hacer
- Con descripciones de cada una

---

### Comando 4: `sendell start`
**Qué hace**: Modo proactivo (loop OODA)

```powershell
# 3 ciclos de prueba cada 30 segundos
uv run python -m sendell start --interval 30 --max-cycles 3
```

Sendell monitorea tu sistema cada N segundos y te alerta proactivamente.

---

## Niveles de Autonomía (L1-L5)

**Configurar**: `sendell brain` → tab Memorias → Selector desplegable

| Nivel | Nombre | Comportamiento |
|-------|--------|---------------|
| **L1** | Monitor Only | Solo observa, nunca actúa |
| **L2** | Ask Permission | **DEFAULT** - Pide permiso para TODO |
| **L3** | Safe Actions | Ejecuta acciones seguras automáticamente (abrir apps) |
| **L4** | Modify State | Puede cerrar apps, modificar archivos |
| **L5** | Full Autonomy | Autonomía completa (peligroso) |

**Recomendación**: Usa L2 si no confías 100%, L3 para uso normal.

---

## Las 6 Herramientas de Sendell

Todas 100% funcionales:

1. **get_system_health** - Obtiene CPU, RAM, Disco %
2. **get_active_window** - Ve qué ventana está activa
3. **list_top_processes** - Lista procesos por uso de recursos
4. **open_application** - Abre apps (notepad, chrome, vscode, etc.)
5. **respond_to_user** - Te envía mensajes
6. **show_brain** - Abre la GUI de configuración

---

## Configuración (.env)

```bash
# OpenAI (OBLIGATORIO)
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview

# Autonomía (configurable desde GUI)
SENDELL_AUTONOMY_LEVEL=2

# Loop proactivo
SENDELL_LOOP_INTERVAL=60
SENDELL_PROACTIVE_MODE=true

# Privacidad
SENDELL_BLOCKED_APPS=1password,keepass,banking
SENDELL_SCRUB_PII=true

# Logs
SENDELL_LOG_LEVEL=INFO
```

**No toques el .env manualmente**. Usa `sendell brain` para configurar.

---

## Arquitectura del Proyecto

```
sendell/
├── src/sendell/
│   ├── agent/
│   │   ├── core.py          # Agente LangGraph + GPT-4
│   │   ├── prompts.py       # System prompt
│   │   ├── memory.py        # Sistema de memoria (JSON)
│   │   └── brain_gui.py     # GUI tkinter
│   ├── device/
│   │   ├── monitor.py       # Wrapper de psutil
│   │   ├── automation.py    # Control de apps
│   │   └── platform/
│   │       └── windows.py   # APIs de Windows
│   ├── mcp/
│   │   ├── server.py        # Servidor MCP (no usado aún)
│   │   └── tools/           # Implementación de herramientas
│   ├── security/
│   │   └── permissions.py   # Sistema L1-L5
│   ├── utils/
│   │   ├── logger.py        # Logging con PII scrubbing
│   │   └── errors.py        # Excepciones custom
│   ├── config.py            # Configuración Pydantic
│   └── __main__.py          # CLI principal
├── data/
│   └── sendell_memory.json  # Memoria persistente
├── .env                     # Tu configuración
└── pyproject.toml           # Dependencias
```

---

## Stack Tecnológico

- **Agente**: LangGraph (ReAct pattern)
- **LLM**: OpenAI GPT-4 Turbo
- **Monitoreo**: psutil (cross-platform) + pywin32 (Windows)
- **GUI**: tkinter (incluido en Python)
- **Config**: Pydantic + python-dotenv
- **CLI**: Typer + Rich

---

## Sistema de Memoria

### Dónde se guarda
`data/sendell_memory.json`

### Qué guarda
```json
{
  "facts": [
    {"fact": "Daniel trabaja en AI", "category": "work"}
  ],
  "preferences": {
    "favorite_apps": ["vscode"],
    "work_hours": "14:00-18:00"
  },
  "conversations": [...],
  "sessions": [...]
}
```

### Cómo agregar facts
1. `sendell brain`
2. Tab Memorias
3. "Agregar Fact"
4. Escribe y guarda

**Nota**: Por ahora son manuales. Auto-aprendizaje viene en v0.2.

---

## Privacidad y Seguridad

### Lo que Sendell NUNCA hace
- ❌ Leer contenido de ventanas (solo títulos)
- ❌ Monitorear apps bloqueadas (password managers, banking)
- ❌ Guardar contraseñas o datos sensibles
- ❌ Enviar datos a terceros (excepto OpenAI para el LLM)

### Lo que Sendell SÍ hace
- ✅ Scrubbing de PII en logs (emails, teléfonos, tarjetas)
- ✅ Validación de inputs con Pydantic
- ✅ Ejecución segura (sin shell=True)
- ✅ Logs de auditoría de todas las acciones

---

## Troubleshooting

### Error: "ModuleNotFoundError"
```powershell
uv sync --all-extras
```

### Error: "OpenAI API Key"
Verifica que `.env` tenga tu API key correcta.

### Sendell pide permiso para todo
Cambias a L3: `sendell brain` → Memorias → Autonomía L3

### GUI no abre
```powershell
uv add tk  # Si falta tkinter
```

---

## Roadmap

### ✅ v0.1 (ACTUAL)
- [x] Chat interactivo funcional
- [x] 6 herramientas operativas
- [x] GUI "Ver Cerebro"
- [x] Sistema de memoria (JSON)
- [x] Configuración de autonomía desde GUI
- [x] Niveles L1-L5

### 🔜 v0.2 (Próximo - 2-3 semanas)
- [ ] Memoria conversacional persistente
- [ ] Sendell lee facts automáticamente en conversaciones
- [ ] Aprendizaje automático de facts
- [ ] Checkpointer de LangGraph
- [ ] Más herramientas (screenshots, proyectos, música)

### 🔮 v0.3 (Futuro)
- [ ] Integración email/calendario
- [ ] Sistema de plugins
- [ ] Análisis de productividad

### 🚀 v1.0 (Largo plazo)
- [ ] Servidor MCP funcional
- [ ] Multi-dispositivo
- [ ] macOS support

---

## Preguntas Frecuentes

### ¿Cuánto cuesta usar Sendell?
Sendell es gratis. Pagas solo el uso de OpenAI API (muy barato, ~$0.01-0.05 por conversación).

### ¿Funciona sin internet?
No. Necesita internet para conectarse a OpenAI.

### ¿Sendell guarda mis conversaciones?
Sí, en `data/sendell_memory.json` localmente. Puedes borrarlas desde la GUI.

### ¿Puedo usar otro LLM (no OpenAI)?
Por ahora solo OpenAI. Soporte para modelos locales (Llama, etc.) en v0.3.

### ¿Por qué "Sendell"?
Es tu nombre personalizado para tu asistente AI. Úsalo como quieras.

---

## Comandos Rápidos (Cheatsheet)

```powershell
# Chequeo rápido
uv run python -m sendell health

# Chat principal
uv run python -m sendell chat

# Abrir configuración/memoria
uv run python -m sendell brain

# Modo proactivo (3 ciclos de prueba)
uv run python -m sendell start --max-cycles 3

# Ver versión
uv run python -m sendell version
```

---

## Soporte

- **Bugs/Features**: Crea issues en el repo
- **Documentación técnica**: Ver `claude.md`
- **Developer**: Daniel

---

**Hecho por Daniel**
**Con ayuda de Claude (Anthropic)**

v0.1.0 - MVP Release - Octubre 2025
