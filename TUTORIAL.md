# Tutorial Completo: Sendell - Tu Asistente AI Personal

**Versión**: 0.1.0 MVP
**Duración estimada**: 30-45 minutos
**Objetivo**: Al terminar este tutorial, comprenderás completamente qué es Sendell, cómo funciona, y habrás probado todas sus capacidades.

---

## Tabla de Contenidos

1. [¿Qué es Sendell? - Explicación Detallada](#1-qué-es-sendell---explicación-detallada)
2. [¿Cómo Funciona Internamente?](#2-cómo-funciona-internamente)
3. [Instalación Paso a Paso](#3-instalación-paso-a-paso)
4. [Prueba 1: Health Check](#4-prueba-1-health-check)
5. [Prueba 2: Chat Interactivo](#5-prueba-2-chat-interactivo)
6. [Prueba 3: Explorando el Cerebro de Sendell](#6-prueba-3-explorando-el-cerebro-de-sendell)
7. [Prueba 4: Niveles de Autonomía](#7-prueba-4-niveles-de-autonomía)
8. [Prueba 5: Loop Proactivo](#8-prueba-5-loop-proactivo)
9. [Prueba 6: Sistema de Memoria](#9-prueba-6-sistema-de-memoria)
10. [Prueba 7: Todas las Herramientas](#10-prueba-7-todas-las-herramientas)
11. [Troubleshooting](#11-troubleshooting)
12. [Resumen Final](#12-resumen-final)

---

## 1. ¿Qué es Sendell? - Explicación Detallada

### Concepto Principal

**Sendell** es un **agente AI autónomo** que vive en tu computadora Windows y actúa como tu asistente personal tipo "Jarvis" (como en Iron Man).

### ¿Qué puede hacer?

#### Monitoreo del Sistema
- Ve cuánto CPU, RAM y disco estás usando en tiempo real
- Detecta cuando algo está consumiendo demasiados recursos
- Identifica qué aplicación estás usando (respetando tu privacidad)
- Lista los procesos que más recursos consumen

#### Acciones
- Puede abrir aplicaciones que le pidas (notepad, chrome, vscode, etc.)
- Se comunica contigo proactivamente cuando detecta algo importante
- Ejecuta comandos según el nivel de autonomía que le des

#### Memoria
- Aprende "facts" sobre ti (manualmente por ahora)
- Guarda conversaciones y sesiones
- Tiene una interfaz gráfica donde puedes ver y gestionar su memoria

#### Inteligencia
- Usa GPT-4 de OpenAI para razonar
- Decide qué herramientas usar según tu petición
- Respeta niveles de autonomía (L1-L5)

### ¿Qué NO es Sendell?

- ❌ NO lee el contenido de tus ventanas (solo títulos)
- ❌ NO es spyware ni malware
- ❌ NO envía tus datos a ningún lado excepto OpenAI para procesar tu petición
- ❌ NO accede a apps que tú bloquees (password managers, banking, etc.)

### Casos de Uso Reales

**Ejemplo 1**: "¿Cómo está mi sistema?"
- Sendell revisa CPU, RAM, disco
- Te responde: "CPU 25%, RAM 89% (alta), Disco 60%"
- Te sugiere: "Chrome está usando 1.5GB, ¿quieres que lo cierre?"

**Ejemplo 2**: "Abre notepad"
- Si estás en L3+, Sendell lo abre directamente
- Si estás en L2, te pide permiso primero

**Ejemplo 3**: "¿Qué está consumiendo mi RAM?"
- Sendell lista los top 10 procesos por memoria
- Te muestra nombres, PIDs, y cuánto usan

**Ejemplo 4**: "Muéstrame tu cerebro"
- Sendell abre una GUI donde ves:
  - Facts que sabe de ti
  - Su system prompt (personalidad)
  - Las 6 herramientas que tiene
  - Puedes configurar su nivel de autonomía

---

## 2. ¿Cómo Funciona Internamente?

### Arquitectura en 2 Capas (Simplificada)

```
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE ORQUESTACIÓN                         │
│                                                              │
│   LangGraph Agent + GPT-4                                   │
│   - Recibe tu mensaje                                        │
│   - Decide qué herramientas usar                            │
│   - Ejecuta herramientas                                     │
│   - Te responde                                              │
│                                                              │
│   6 Herramientas Disponibles:                               │
│   1. get_system_health                                       │
│   2. get_active_window                                       │
│   3. list_top_processes                                      │
│   4. open_application                                        │
│   5. respond_to_user                                         │
│   6. show_brain                                              │
│                                                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ (Llama directamente a psutil/pywin32)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              CAPA DE DISPOSITIVO                             │
│                                                              │
│   psutil + pywin32                                          │
│   - Lee CPU, RAM, disco                                      │
│   - Lee ventana activa                                       │
│   - Lista procesos                                           │
│   - Abre aplicaciones                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de una Conversación

**Tú escribes**: "How's my system?"

1. **CLI captura tu input** (__main__.py)
2. **Se envía al agente LangGraph** (agent/core.py)
3. **GPT-4 razona**: "Necesito usar get_system_health"
4. **LangGraph ejecuta get_system_health** -> llama a psutil
5. **psutil retorna**: CPU 25%, RAM 89%, Disco 60%
6. **GPT-4 genera respuesta**: "Your system is mostly healthy. CPU at 25% is normal. RAM at 89% is high - you might want to close some apps. Disk at 60% is fine."
7. **Te muestra la respuesta** en consola

### Tecnologías Usadas

- **Python 3.10+**: Lenguaje base
- **LangGraph**: Orquesta el agente (patrón ReAct)
- **OpenAI GPT-4 Turbo**: Cerebro del agente
- **psutil**: Lee métricas del sistema (CPU, RAM, disco, procesos)
- **pywin32**: APIs de Windows (ventanas activas)
- **tkinter**: GUI para "Ver Cerebro"
- **Typer + Rich**: CLI con formateo bonito
- **Pydantic**: Validación de configuración
- **JSON**: Almacena memoria en data/sendell_memory.json

---

## 3. Instalación Paso a Paso

### Requisitos Previos

Antes de empezar, asegúrate de tener:
- ✅ Windows 10 o 11
- ✅ Python 3.10 o superior
- ✅ OpenAI API Key (crea una en https://platform.openai.com/api-keys)
- ✅ Conexión a internet

### Paso 1: Verificar Python

Abre PowerShell o CMD y ejecuta:

```powershell
python --version
```

Debes ver algo como: `Python 3.10.x` o superior.

Si no tienes Python, descárgalo de: https://www.python.org/downloads/

**IMPORTANTE**: Al instalar Python, marca la casilla "Add Python to PATH".

### Paso 2: Instalar uv (gestor de dependencias)

```powershell
pip install uv
```

Verifica la instalación:

```powershell
uv --version
```

### Paso 3: Navegar a la Carpeta del Proyecto

```powershell
cd C:\Users\Daniel\Desktop\Daniel\sendell
```

(Ajusta la ruta según donde tengas el proyecto)

### Paso 4: Instalar Dependencias

```powershell
uv sync
```

Esto instalará todas las dependencias necesarias. Tomará 1-2 minutos.

### Paso 5: Configurar tu API Key

1. Copia el archivo de ejemplo:

```powershell
copy .env.example .env
```

2. Abre el archivo `.env` con notepad:

```powershell
notepad .env
```

3. Pega tu OpenAI API Key:

```
OPENAI_API_KEY=sk-tu-api-key-aqui
```

4. Guarda y cierra notepad.

### Paso 6: Verificar Instalación

```powershell
uv run python -m sendell version
```

Debes ver:

```
Sendell v0.1.0 - MVP Release
Autonomous AI Agent for System Monitoring
```

**¡Listo!** Sendell está instalado.

---

## 4. Prueba 1: Health Check

### Objetivo
Verificar que Sendell puede leer métricas de tu sistema.

### Comando

```powershell
uv run python -m sendell health
```

### Qué Esperar

Verás una tabla como esta:

```
                System Health
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric       ┃ Value                  ┃ Status   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ CPU Usage    │ 25%                    │ [OK]     │
│ RAM Usage    │ 89% (14.2GB / 16.0GB)  │ [!] High │
│ Disk Usage   │ 60% (480GB / 800GB)    │ [OK]     │
└──────────────┴────────────────────────┴──────────┘
```

### ¿Qué Está Pasando?

1. Sendell usa **psutil** para leer:
   - CPU: Porcentaje de uso actual
   - RAM: Porcentaje y GB usados/totales
   - Disco: Porcentaje y GB usados/totales (disco C:)

2. Compara contra umbrales:
   - CPU > 80% = [!] High
   - RAM > 85% = [!] High
   - Disco > 90% = [!] High

3. **NO usa el agente AI** - es una lectura directa del sistema.

### Ejercicio

1. Abre varias aplicaciones (Chrome, VS Code, etc.)
2. Ejecuta `sendell health` otra vez
3. Observa cómo cambian los valores

**✅ Prueba 1 completada**: Sendell puede leer tu sistema.

---

## 5. Prueba 2: Chat Interactivo

### Objetivo
Conversar con Sendell y que use sus herramientas inteligentemente.

### Comando

```powershell
uv run python -m sendell chat
```

### Qué Esperar

Verás el banner de Sendell y un prompt:

```
========================================
      SENDELL - AI Agent v0.1
  Autonomous System Monitor & Control
========================================

Interactive chat mode started!
Type your messages below. Commands:
  /quit or /exit - Exit chat
  /health - Quick system health check
  /help - Show available commands

You: _
```

### Conversación 1: Pregunta Simple

**Tú escribes**: `How's my system?`

**Sendell responde** (ejemplo):
```
Thinking...

Sendell: I've checked your system. Here's the status:

- CPU: 25% - Normal usage
- RAM: 89% (14.2GB / 16.0GB) - HIGH! You're using a lot of memory
- Disk: 60% - Healthy

Your RAM is quite high. Would you like me to show you which apps are using the most memory?
```

**¿Qué pasó?**
1. Sendell usó la herramienta `get_system_health`
2. GPT-4 interpretó los resultados
3. Te respondió en lenguaje natural

### Conversación 2: Pregunta con Seguimiento

**Tú**: `Yes, show me what's using my RAM`

**Sendell** (ejemplo):
```
Thinking...

Sendell: Here are the top 5 processes by memory usage:

1. chrome.exe - 1.5 GB (PID: 12345)
2. Code.exe - 800 MB (PID: 12346)
3. Discord.exe - 600 MB (PID: 12347)
4. Spotify.exe - 400 MB (PID: 12348)
5. explorer.exe - 300 MB (PID: 12349)

Chrome is using the most memory. Would you like suggestions for freeing up RAM?
```

**¿Qué pasó?**
1. Sendell usó la herramienta `list_top_processes` con sort_by="memory"
2. GPT-4 formateó la respuesta de manera legible

### Conversación 3: Pedir una Acción

**Tú**: `Open notepad`

**Respuesta depende del nivel de autonomía**:

**Si estás en L2 (default)**:
```
Sendell: I need your permission to open notepad. I'm currently at autonomy level L2
(Ask Permission), which requires approval for all actions.

Would you like me to open notepad?

Note: You can change my autonomy level to L3 (Safe Actions) in the brain interface
if you want me to open apps automatically without asking.
```

**Si estás en L3+**:
```
Sendell: Opening notepad...

[Notepad se abre]

Sendell: Notepad opened successfully!
```

### Conversación 4: Ver el Cerebro

**Tú**: `Show me your brain`

**Sendell**:
```
Sendell: Opening my brain interface...

[Se abre una ventana GUI]

Sendell: Brain GUI opened. Check the new window to manage my memory and settings.
```

### Comandos Especiales en el Chat

Prueba estos comandos:

1. `/health` - Health check rápido (sin salir del chat)
2. `/help` - Muestra ayuda
3. `/quit` - Salir del chat

### Ejercicio

Mantén una conversación de 5 mensajes con Sendell:

1. "How's my system?"
2. "What's using my CPU?"
3. "Open calculator"
4. "What can you do?"
5. "Show me your brain"

**✅ Prueba 2 completada**: Puedes conversar con Sendell y usa herramientas inteligentemente.

---

## 6. Prueba 3: Explorando el Cerebro de Sendell

### Objetivo
Entender la interfaz gráfica donde Sendell guarda su memoria y configuración.

### Comando

```powershell
uv run python -m sendell brain
```

O desde el chat: `show me your brain`

### Qué Esperar

Se abrirá una ventana GUI con 3 pestañas (tabs).

---

### Tab 1: MEMORIAS

**Qué ves**:

```
┌─────────────────────────────────────────────────────┐
│ MEMORIAS                                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Facts Aprendidos:                                   │
│ ┌─────────────────────────────────────────────┐   │
│ │ (Lista vacía si es primera vez)             │   │
│ │                                             │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ [Agregar Fact] [Eliminar Fact]                     │
│                                                     │
│ Estadísticas:                                       │
│ Total Facts: 0                                      │
│ Total Conversaciones: 0                             │
│ Total Sesiones: 0                                   │
│                                                     │
│ ─────────────────────────────────────────────────  │
│                                                     │
│ Configurar Autonomía:                              │
│ Nivel actual: L2 - Ask Permission                  │
│                                                     │
│ [Dropdown: L1 L2 L3 L4 L5] [Guardar Nivel]        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Prueba 1: Agregar un Fact**

1. Click en **"Agregar Fact"**
2. Aparece un diálogo:
   - **Fact**: "Me gusta programar en Python"
   - **Categoría**: "preferences"
3. Click **OK**
4. El fact aparece en la lista

**Prueba 2: Ver Detalles de un Fact**

- Selecciona el fact que agregaste
- Verás: fact, categoría, y fecha/hora cuando se agregó

**Prueba 3: Eliminar un Fact**

1. Selecciona un fact
2. Click **"Eliminar Fact"**
3. Confirma
4. El fact desaparece

**Prueba 4: Cambiar Nivel de Autonomía**

1. En el dropdown, selecciona **"3 - Safe Actions"**
2. Click **"Guardar Nivel"**
3. Verás un mensaje: "Autonomía actualizada a nivel 3. Reinicia Sendell para aplicar cambios."
4. Cierra y vuelve a abrir el chat para que aplique

---

### Tab 2: PROMPTS

**Qué ves**:

```
┌─────────────────────────────────────────────────────┐
│ PROMPTS                                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ System Prompt (Define personalidad de Sendell):    │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ You are Sendell, an autonomous AI assistant │   │
│ │ monitoring this Windows device.             │   │
│ │                                             │   │
│ │ Your primary goals:                         │   │
│ │ 1. Monitor system health proactively...    │   │
│ │ ...                                         │   │
│ │ (puedes scrollear para ver todo)            │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ [Guardar Prompt]                                    │
│                                                     │
│ Nota: Reinicia Sendell después de editar           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Prueba 1: Leer el Prompt**

- Lee el system prompt completo
- Entenderás cómo está programada la personalidad de Sendell

**Prueba 2: Editar el Prompt (Opcional)**

1. Modifica una línea, por ejemplo:
   - Cambia: "Helpful, proactive, non-intrusive"
   - Por: "Helpful, very friendly, enthusiastic"
2. Click **"Guardar Prompt"**
3. Reinicia el chat
4. Sendell ahora será más entusiasta en sus respuestas

**Nota**: Este es avanzado. Si no estás seguro, no lo cambies.

---

### Tab 3: HERRAMIENTAS

**Qué ves**:

```
┌─────────────────────────────────────────────────────┐
│ HERRAMIENTAS                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Herramientas Disponibles (6):                      │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 1. get_system_health                        │   │
│ │    Get current system health metrics...    │   │
│ │                                             │   │
│ │ 2. get_active_window                        │   │
│ │    Get information about currently...      │   │
│ │                                             │   │
│ │ 3. list_top_processes                       │   │
│ │    List top N processes by resource...     │   │
│ │                                             │   │
│ │ 4. open_application                         │   │
│ │    Open an application by name...          │   │
│ │                                             │   │
│ │ 5. respond_to_user                          │   │
│ │    Send a message to the user...           │   │
│ │                                             │   │
│ │ 6. show_brain                               │   │
│ │    Open the Sendell Brain GUI...           │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ (Esta pestaña es solo informativa)                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Prueba 1: Ver Todas las Herramientas**

- Lee la lista completa
- Nota las descripciones de cada herramienta
- Estas son las 6 capacidades de Sendell

### Ejercicio

1. Abre la GUI
2. Agrega 3 facts sobre ti:
   - "Mi nombre es [tu nombre]" (categoría: personal)
   - "Trabajo en [tu trabajo]" (categoría: work)
   - "Uso [tu app favorita] frecuentemente" (categoría: preferences)
3. Cambia el nivel de autonomía a L3
4. Lee el system prompt completo
5. Verifica las 6 herramientas

**✅ Prueba 3 completada**: Conoces la GUI y cómo gestionar memoria y configuración.

---

## 7. Prueba 4: Niveles de Autonomía

### Objetivo
Entender cómo los niveles L1-L5 cambian el comportamiento de Sendell.

### Los 5 Niveles Explicados

| Nivel | Nombre | Comportamiento | Ejemplo |
|-------|--------|----------------|---------|
| **L1** | Monitor Only | Solo observa, NUNCA actúa | "I can see notepad would be useful, but I'm at L1 so I can only observe." |
| **L2** | Ask Permission | Pide permiso para TODO | "I'd like to open notepad. May I?" |
| **L3** | Safe Actions | Ejecuta acciones seguras automáticamente | [Abre notepad sin preguntar] |
| **L4** | Modify State | Puede cerrar apps, modificar archivos | Puede cerrar Chrome si consume mucho RAM |
| **L5** | Full Autonomy | Autonomía completa (¡peligroso!) | Puede hacer cualquier cosa |

**Default**: L2 (Ask Permission) - Recomendado para empezar

---

### Prueba en L2 (Default)

1. Asegúrate de estar en L2:
   ```powershell
   uv run python -m sendell brain
   ```
   - Ve a Tab Memorias
   - Verifica que dice "L2 - Ask Permission"

2. Abre el chat:
   ```powershell
   uv run python -m sendell chat
   ```

3. Pide: `Open calculator`

4. **Resultado esperado**:
   ```
   Sendell: I need your permission to open calculator. I'm currently at autonomy
   level L2 (Ask Permission), which requires approval for all actions.

   Would you like me to open calculator?
   ```

**Observación**: Sendell SIEMPRE pide permiso en L2.

---

### Prueba en L3 (Safe Actions)

1. Cambia a L3:
   - Abre la GUI: `uv run python -m sendell brain`
   - Tab Memorias -> Dropdown -> "3 - Safe Actions"
   - Click "Guardar Nivel"
   - Cierra la GUI

2. **IMPORTANTE**: Reinicia el chat (cierra y abre otra vez)

3. Abre el chat:
   ```powershell
   uv run python -m sendell chat
   ```

4. Pide: `Open calculator`

5. **Resultado esperado**:
   ```
   Sendell: Opening calculator...

   [Calculator se abre automáticamente]

   Sendell: Calculator opened successfully!
   ```

**Observación**: En L3, Sendell NO pide permiso para acciones "seguras" como abrir apps.

---

### Prueba en L1 (Monitor Only)

1. Cambia a L1:
   - GUI -> Tab Memorias -> "1 - Monitor Only"
   - Guarda y reinicia chat

2. Pide: `Open notepad`

3. **Resultado esperado**:
   ```
   Sendell: I'm currently at autonomy level L1 (Monitor Only), which means I can
   only observe your system but cannot take any actions.

   I cannot open notepad at this level. If you'd like me to perform actions,
   please change my autonomy level to L2 or higher in the brain interface.
   ```

**Observación**: En L1, Sendell NUNCA actúa, solo informa.

---

### Tabla Comparativa de Comportamiento

Prueba este escenario en cada nivel:

**Escenario**: "My RAM is high. What should I do?"

| Nivel | Respuesta de Sendell |
|-------|---------------------|
| L1 | "Your RAM is at 89%. Chrome is using 1.5GB. I can only observe, but I recommend closing Chrome." |
| L2 | "Your RAM is at 89%. Chrome is using 1.5GB. Would you like me to close Chrome for you?" |
| L3 | "Your RAM is at 89%. I'd like to close Chrome (1.5GB). May I? (Note: In L3 I can open apps but closing apps requires L4+)" |
| L4 | [Cierra Chrome automáticamente] "I closed Chrome to free up 1.5GB of RAM." |
| L5 | [Cierra Chrome y otros apps] "I closed Chrome and Discord to free up 2.1GB of RAM." |

### Recomendaciones de Uso

- **L1**: Testing, cuando no confías en el agente
- **L2**: Uso normal, control total (RECOMENDADO)
- **L3**: Uso diario, confías en Sendell para acciones simples
- **L4**: Uso avanzado, dejas que Sendell modifique estado
- **L5**: Solo para expertos, autonomía completa

### Ejercicio

1. Prueba el mismo comando en L1, L2, y L3:
   - "Open notepad"

2. Observa las diferencias en respuesta y comportamiento

3. Vuelve a L2 (o L3 según tu preferencia)

**✅ Prueba 4 completada**: Entiendes los niveles de autonomía y cómo cambian el comportamiento.

---

## 8. Prueba 5: Loop Proactivo

### Objetivo
Ver a Sendell monitoreando tu sistema automáticamente cada N segundos.

### ¿Qué es el Loop Proactivo?

Es el modo "OODA" (Observe -> Orient -> Decide -> Act):
- **Observe**: Sendell lee tu sistema cada N segundos
- **Orient**: Analiza la información
- **Decide**: Determina si hay algo que reportar
- **Act**: Te notifica o ejecuta acciones

**Piensa en ello como**: Sendell corriendo en background vigilando tu sistema.

---

### Comando

```powershell
uv run python -m sendell start --interval 30 --max-cycles 3
```

**Parámetros**:
- `--interval 30`: Ejecuta cada 30 segundos
- `--max-cycles 3`: Solo 3 ciclos (para testing, si omites esto corre infinitamente)

### Qué Esperar

```
========================================
      SENDELL - AI Agent v0.1
  Autonomous System Monitor & Control
========================================

Starting proactive monitoring...
Autonomy Level: L2 - Ask Permission
Loop Interval: 30s
Press Ctrl+C to stop

Proactive loop started. Monitoring system...

--- Cycle 1 ---
[Sendell analiza tu sistema]
[Si detecta algo, verás output aquí]
Sleeping for 30s...

--- Cycle 2 ---
[Sendell analiza otra vez]
Sleeping for 30s...

--- Cycle 3 ---
[Sendell analiza por tercera vez]

Reached max cycles (3). Stopping.
```

### Escenarios de Output

**Escenario 1: Todo Normal**

```
--- Cycle 1 ---
[No output visible - Sendell vio que todo está OK]
Sleeping for 30s...
```

**Escenario 2: RAM Alta**

```
--- Cycle 1 ---
[Sendell detecta RAM alta]

[!] RAM at 89% (14.2GB / 16.0GB) - HIGH
Top memory consumers:
1. chrome.exe - 1.5 GB
2. Code.exe - 800 MB

Suggestion: Consider closing chrome.exe to free up memory.

Sleeping for 30s...
```

**Escenario 3: Nueva Aplicación Abierta**

```
--- Cycle 2 ---
[Sendell nota que abriste una nueva app]

Active window changed: Microsoft Word (WINWORD.EXE)
Looks like you're working on a document.

Sleeping for 30s...
```

---

### Ejercicio Interactivo

**Objetivo**: Ver a Sendell reaccionar a cambios en tu sistema.

1. Inicia el loop:
   ```powershell
   uv run python -m sendell start --interval 15 --max-cycles 5
   ```
   (15 segundos para testing rápido, 5 ciclos)

2. **Durante el Cycle 1**: No hagas nada
   - Observa el output

3. **Durante el Cycle 2**: Abre Chrome con muchas pestañas
   - Observa si Sendell detecta el aumento de RAM

4. **Durante el Cycle 3**: Abre una app pesada (Photoshop, VS Code, etc.)
   - Observa si Sendell comenta sobre el cambio

5. **Durante el Cycle 4**: Cambia a una ventana diferente
   - Observa si Sendell nota el cambio de ventana activa

6. **Cycle 5**: Deja que termine

### Detener el Loop Manualmente

Si NO usaste `--max-cycles`, el loop corre infinitamente.

Para detenerlo:
- Presiona **Ctrl+C**

Verás:

```
^C
Sendell shutting down gracefully...
```

---

### Modo Producción (Sin Límite de Ciclos)

Para usar Sendell como un agente persistente:

```powershell
uv run python -m sendell start --interval 60
```

(Corre cada 60 segundos, sin límite)

**Usa esto cuando**: Quieres que Sendell monitoree tu sistema todo el día.

**Para detener**: Ctrl+C

**✅ Prueba 5 completada**: Has visto a Sendell monitorear proactivamente tu sistema.

---

## 9. Prueba 6: Sistema de Memoria

### Objetivo
Entender cómo Sendell guarda y usa memoria persistente.

### ¿Dónde se Guarda la Memoria?

Archivo: `data/sendell_memory.json`

### Estructura de la Memoria

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

---

### Prueba 1: Ver el Archivo de Memoria

1. Navega a la carpeta del proyecto

2. Abre `data/sendell_memory.json` con notepad:
   ```powershell
   notepad data\sendell_memory.json
   ```

3. Si es la primera vez, verás:
   ```json
   {
     "facts": [],
     "preferences": {},
     "conversations": [],
     "sessions": []
   }
   ```

---

### Prueba 2: Agregar Facts desde GUI

1. Abre la GUI:
   ```powershell
   uv run python -m sendell brain
   ```

2. Tab Memorias -> "Agregar Fact"

3. Agrega estos facts:
   - Fact: "Me gusta programar en Python", Categoría: "preferences"
   - Fact: "Trabajo en [tu empresa]", Categoría: "work"
   - Fact: "Mi app favorita es [tu app]", Categoría: "preferences"

4. Cierra la GUI

5. Abre otra vez `data/sendell_memory.json`:
   ```powershell
   notepad data\sendell_memory.json
   ```

6. **Observa**: Los facts están ahí con timestamps!

---

### Prueba 3: Persistencia de Memoria

**Objetivo**: Verificar que la memoria persiste entre sesiones.

1. Agrega un fact en la GUI: "Prueba de persistencia"

2. Cierra la GUI completamente

3. Reinicia tu computadora (opcional, pero recomendado)

4. Abre la GUI otra vez:
   ```powershell
   uv run python -m sendell brain
   ```

5. **Verifica**: El fact "Prueba de persistencia" sigue ahí

**Conclusión**: La memoria es persistente, no se pierde.

---

### Prueba 4: Estadísticas de Memoria

En la GUI (Tab Memorias), verás:

```
Estadísticas:
Total Facts: 3
Total Conversaciones: 0
Total Sesiones: 0
```

**¿Por qué 0 conversaciones y sesiones?**

- Estas features están implementadas en la estructura pero no se usan activamente en v0.1
- Se activarán en v0.2 con memoria conversacional completa

---

### Estado Actual de Memoria (v0.1)

**Funciona**:
- ✅ Facts guardados persistentemente
- ✅ CRUD de facts desde GUI
- ✅ Categorías de facts
- ✅ Timestamps

**No funciona aún (v0.2)**:
- ⏳ Sendell carga facts automáticamente en conversaciones
- ⏳ Sendell aprende facts automáticamente de conversaciones
- ⏳ Conversaciones guardadas con historial
- ⏳ Sesiones trackeadas automáticamente

---

### Ejercicio

1. Crea 5 facts en diferentes categorías:
   - 2 en "personal"
   - 2 en "work"
   - 1 en "preferences"

2. Verifica que están en el JSON

3. Elimina 1 fact desde la GUI

4. Verifica que se eliminó del JSON

5. Cierra y reabre la GUI

6. Verifica que los cambios persisten

**✅ Prueba 6 completada**: Entiendes el sistema de memoria y cómo funciona la persistencia.

---

## 10. Prueba 7: Todas las Herramientas

### Objetivo
Probar explícitamente cada una de las 6 herramientas de Sendell.

---

### Herramienta 1: get_system_health

**Qué hace**: Lee CPU, RAM, Disco

**Cómo probarla**:

```powershell
uv run python -m sendell chat
```

```
You: Check my system health
```

**Output esperado**:
```
Sendell: I've checked your system:
- CPU: 25% (normal)
- RAM: 89% (14.2GB / 16.0GB) - HIGH
- Disk: 60% (480GB / 800GB) - OK

Your RAM usage is quite high. Would you like me to show you what's using it?
```

**Prueba exitosa si**: Ves CPU%, RAM%, Disco%

---

### Herramienta 2: get_active_window

**Qué hace**: Ve qué ventana/app tienes activa

**Cómo probarla**:

1. Abre Chrome o cualquier app

2. Haz click en esa ventana (para que esté activa)

3. En el chat de Sendell:
   ```
   You: What am I doing right now?
   ```

**Output esperado**:
```
Sendell: You're currently using Google Chrome (chrome.exe).
The active window is "Tutorial Completo: Sendell - Google Chrome".
```

**Prueba exitosa si**: Sendell identifica correctamente tu ventana activa

---

### Herramienta 3: list_top_processes

**Qué hace**: Lista procesos que más consumen recursos

**Cómo probarla**:

```
You: What's using my RAM?
```

**Output esperado**:
```
Sendell: Here are the top processes by memory usage:

1. chrome.exe - 1.5 GB (PID: 12345)
2. Code.exe - 800 MB (PID: 12346)
3. Discord.exe - 600 MB (PID: 12347)
4. Spotify.exe - 400 MB (PID: 12348)
5. explorer.exe - 300 MB (PID: 12349)
```

**Variante con CPU**:
```
You: What's using my CPU?
```

**Output esperado**:
```
Sendell: Top processes by CPU usage:

1. chrome.exe - 45% (PID: 12345)
2. System - 15% (PID: 4)
3. Code.exe - 10% (PID: 12346)
...
```

**Prueba exitosa si**: Ves lista de procesos con uso de RAM o CPU

---

### Herramienta 4: open_application

**Qué hace**: Abre aplicaciones

**Cómo probarla (asegúrate de estar en L3+)**:

```
You: Open calculator
```

**Output esperado**:
```
Sendell: Opening calculator...

[Calculator se abre]

Sendell: Calculator opened successfully!
```

**Aplicaciones soportadas** (prueba varias):

- `notepad` - Bloc de notas
- `calc` o `calculator` - Calculadora
- `mspaint` - Paint
- `chrome` - Google Chrome (si está instalado)
- `firefox` - Firefox (si está instalado)
- `code` - VS Code (si está instalado)
- `cmd` - Command Prompt
- `powershell` - PowerShell

**Prueba**:
1. `Open notepad`
2. `Open calculator`
3. `Open paint`

**Prueba exitosa si**: Cada aplicación se abre correctamente

---

### Herramienta 5: respond_to_user

**Qué hace**: Sendell usa esto para comunicarse contigo (esto pasa automáticamente)

**Cómo probarla**:

Esta herramienta se usa implícitamente en todas las conversaciones.

Cada vez que Sendell te responde, está usando `respond_to_user` internamente.

**No necesitas hacer nada especial** - ya la has usado en todas las pruebas anteriores.

---

### Herramienta 6: show_brain

**Qué hace**: Abre la GUI

**Cómo probarla**:

```
You: Show me your brain
```

o

```
You: Open brain interface
```

o

```
You: Let me see your memory
```

**Output esperado**:
```
Sendell: Opening my brain interface...

[GUI se abre]

Sendell: Brain GUI opened. Check the new window to manage my memory and settings.
```

**Prueba exitosa si**: La GUI se abre

---

### Resumen: Tabla de Herramientas

| # | Herramienta | Para Qué Sirve | Comando de Prueba |
|---|-------------|----------------|-------------------|
| 1 | get_system_health | Ver CPU/RAM/Disco | "Check my system" |
| 2 | get_active_window | Ver ventana activa | "What am I doing?" |
| 3 | list_top_processes | Ver procesos top | "What's using my RAM?" |
| 4 | open_application | Abrir apps | "Open calculator" |
| 5 | respond_to_user | Comunicarse | (automático) |
| 6 | show_brain | Abrir GUI | "Show me your brain" |

---

### Ejercicio Final: Conversación Completa

Mantén esta conversación que usa TODAS las herramientas:

```
You: How's my system?
[Usa: get_system_health]

You: What am I doing right now?
[Usa: get_active_window]

You: Show me what's using my CPU
[Usa: list_top_processes con sort_by=cpu]

You: Now show me what's using my RAM
[Usa: list_top_processes con sort_by=memory]

You: Open notepad
[Usa: open_application]

You: Show me your brain
[Usa: show_brain]
```

**✅ Prueba 7 completada**: Has probado las 6 herramientas de Sendell.

---

## 11. Troubleshooting

### Problema 1: "ModuleNotFoundError"

**Error**:
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solución**:
```powershell
uv sync --all-extras
```

Si persiste:
```powershell
uv pip install langgraph langchain-core langchain-openai
```

---

### Problema 2: "OpenAI API Key Error"

**Error**:
```
openai.AuthenticationError: Invalid API key
```

**Solución**:
1. Verifica que el `.env` tenga tu API key:
   ```powershell
   notepad .env
   ```

2. Verifica que la key empiece con `sk-`

3. Si no estás seguro, genera una nueva key en: https://platform.openai.com/api-keys

4. Pega la nueva key en `.env`:
   ```
   OPENAI_API_KEY=sk-nueva-key-aqui
   ```

---

### Problema 3: Sendell Pide Permiso Para Todo

**Síntoma**: Sendell pregunta antes de cada acción

**Causa**: Estás en nivel L2 (Ask Permission)

**Solución**:
1. Abre la GUI: `uv run python -m sendell brain`
2. Tab Memorias -> Selector de autonomía
3. Cambia a "3 - Safe Actions"
4. Guarda y reinicia el chat

---

### Problema 4: GUI No Abre

**Error**: Nada pasa al ejecutar `sendell brain`

**Solución 1** (si falta tkinter):
```powershell
pip install tk
```

**Solución 2** (si falta pywin32 en Windows):
```powershell
pip install pywin32
```

**Solución 3** (reinstalar dependencias):
```powershell
uv sync --all-extras
```

---

### Problema 5: "psutil" Error

**Error**:
```
ModuleNotFoundError: No module named 'psutil'
```

**Solución**:
```powershell
uv pip install psutil
```

---

### Problema 6: Sendell No Abre Aplicaciones

**Síntoma**: "Open notepad" no hace nada o da error

**Causa 1**: Estás en L1 (Monitor Only)
- Solución: Cambia a L2 o L3

**Causa 2**: Estás en L2 y no diste permiso
- Solución: Responde "yes" cuando Sendell pida permiso

**Causa 3**: La aplicación no está instalada
- Solución: Usa apps que sepas que tienes (notepad siempre existe en Windows)

---

### Problema 7: Chat Lento

**Síntoma**: Sendell tarda mucho en responder

**Causa**: GPT-4 puede tardar 2-10 segundos

**Esto es normal**. Si tarda más de 20 segundos:
1. Verifica tu conexión a internet
2. Verifica que tu API key tenga créditos: https://platform.openai.com/usage

---

### Problema 8: Error de Encoding

**Error**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Causa**: Archivos con caracteres especiales

**Solución**: Este problema ya está resuelto en v0.1. Si lo ves:
1. Reporta el archivo específico que causa el error
2. Usa solo ASCII en configuraciones

---

### Problema 9: Memory File Corrupto

**Error**:
```
JSONDecodeError: Expecting value
```

**Causa**: El archivo `data/sendell_memory.json` está corrupto

**Solución**:
1. Haz backup si hay datos importantes:
   ```powershell
   copy data\sendell_memory.json data\sendell_memory_backup.json
   ```

2. Elimina el archivo corrupto:
   ```powershell
   del data\sendell_memory.json
   ```

3. Reinicia Sendell - creará un archivo nuevo

---

### Problema 10: No Tengo `uv` Instalado

**Alternativa sin uv**:

1. Usar pip directo:
   ```powershell
   pip install -e .
   ```

2. Ejecutar comandos sin `uv run`:
   ```powershell
   python -m sendell health
   python -m sendell chat
   python -m sendell brain
   ```

---

## 12. Resumen Final

### ¿Qué Has Aprendido?

Después de completar este tutorial, ahora sabes:

1. **Qué es Sendell**: Un agente AI autónomo que monitorea tu sistema Windows

2. **Cómo funciona**: LangGraph + GPT-4 + psutil en 2 capas

3. **Instalación**: Cómo instalar y configurar con tu OpenAI API key

4. **4 Comandos principales**:
   - `sendell health` - Chequeo rápido
   - `sendell chat` - Chat interactivo (PRINCIPAL)
   - `sendell brain` - GUI de configuración
   - `sendell start` - Loop proactivo

5. **6 Herramientas**:
   - get_system_health - Métricas del sistema
   - get_active_window - Ventana activa
   - list_top_processes - Procesos top
   - open_application - Abrir apps
   - respond_to_user - Comunicarse
   - show_brain - GUI

6. **Niveles de autonomía**: L1 (solo observa) a L5 (autonomía completa)

7. **Sistema de memoria**: Facts, preferencias, conversaciones en JSON

8. **GUI con 3 tabs**: Memorias, Prompts, Herramientas

---

### Checklist de Testing Completo

Marca lo que has completado:

- [ ] ✅ Instalación exitosa
- [ ] ✅ Health check funcionó
- [ ] ✅ Chat interactivo funcionó
- [ ] ✅ Probé las 6 herramientas
- [ ] ✅ Abrí la GUI
- [ ] ✅ Agregué facts a la memoria
- [ ] ✅ Cambié el nivel de autonomía
- [ ] ✅ Probé L1, L2, y L3
- [ ] ✅ Ejecuté el loop proactivo
- [ ] ✅ Verifiqué persistencia de memoria

---

### Próximos Pasos

**Uso Diario**:
1. Mantén Sendell en L2 o L3
2. Usa `sendell chat` para interactuar
3. Agrega facts sobre ti en la GUI
4. (Opcional) Usa `sendell start` para monitoreo continuo

**Experimentación**:
1. Edita el system prompt para cambiar personalidad
2. Prueba diferentes niveles de autonomía
3. Agrega apps bloqueadas en `.env`

**Feedback**:
- Si encuentras bugs, reporta en el proyecto
- Sugiere nuevas herramientas que te gustaría tener

---

### Recursos Adicionales

- **README.md**: Referencia rápida de comandos
- **claude.md**: Documentación técnica y arquitectura
- **GitHub Issues**: Para reportar problemas

---

### Preguntas Frecuentes Finales

**P: ¿Cuánto cuesta usar Sendell?**
R: Sendell es gratis. Solo pagas el uso de OpenAI API (~$0.01-0.05 por conversación).

**P: ¿Funciona sin internet?**
R: No. Necesita internet para conectarse a OpenAI.

**P: ¿Puedo usar otro LLM (no OpenAI)?**
R: Por ahora solo OpenAI. Soporte para modelos locales vendrá en v0.3.

**P: ¿Es seguro?**
R: Sí. Sendell NO lee contenido de ventanas, NO accede a apps bloqueadas, y todos los datos están en tu computadora local.

**P: ¿Sendell aprende automáticamente?**
R: En v0.1, facts son manuales. Auto-aprendizaje vendrá en v0.2.

---

## ¡Felicidades!

Has completado el tutorial completo de Sendell. Ahora comprendes perfectamente:
- Qué es y cómo funciona
- Cómo instalarlo y configurarlo
- Cómo usar cada comando
- Cómo funciona cada herramienta
- Cómo gestionar memoria y autonomía

**¡Bienvenido al equipo de usuarios de Sendell!** 🤖

---

**Creado por**: Daniel
**Con ayuda de**: Claude (Anthropic)
**Versión del tutorial**: 1.0
**Fecha**: Octubre 2025
