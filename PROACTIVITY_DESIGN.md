# Diseño de Proactividad para Sendell v0.2+

**Rama**: `feature/proactivity`
**Fecha inicio**: 2025-10-28
**Objetivo**: Transformar Sendell de agente reactivo a agente proactivo con identidad temporal y enfoque en el usuario como persona

---

## Visión General

Sendell debe evolucionar de un "asistente que espera comandos" a un "compañero que vive contigo". El enfoque es **el usuario como persona completa**, no solo su trabajo:

- ✅ Recordar llamar a la abuela
- ✅ Sugerir hacer aseo cuando detecta que no se ha hecho
- ✅ Recordar leer si el usuario tiene ese hábito
- ✅ Trackear proyectos personales (no solo trabajo)
- ✅ Entender el tiempo como recurso valioso
- ✅ Medir tanto acciones del agente como del humano

**Principio clave**: No es "check-in cada hora", es "intervención quirúrgica cuando realmente importa".

---

## Arquitectura de Proactividad: 5 Sistemas Core

### 1. Sistema de Identidad Temporal

**Qué es**: El agente tiene conciencia de su propia existencia en el tiempo.

**Componentes**:

```python
class AgentIdentity:
    birth_date: datetime          # Cuándo "nació" Sendell
    relationship_age_days: int    # Días desde que conoce al usuario
    confidence_level: float       # 0-1, crece con tiempo
    relationship_phase: str       # "birth", "adolescence", "maturity", "mastery"
    milestones: List[Milestone]   # Eventos importantes compartidos
```

**Fases de evolución**:

| Días | Fase | Comportamiento |
|------|------|----------------|
| 1-7 | Birth | Tímido, pregunta mucho, nunca asume |
| 8-30 | Adolescence | Más confiado, empieza a predecir |
| 31-60 | Maturity | Anticipatorio, alto confidence |
| 60+ | Mastery | Intervenciones quirúrgicas, alto valor |

**Ejemplo de uso**:
```
Día 3: "Es mi tercer día contigo. Aún estoy aprendiendo tu ritmo. ¿Prefieres recordatorios por la mañana o por la tarde?"

Día 45: "En mes y medio juntos he notado que siempre pospones llamar a tu abuela los domingos. Es domingo 5pm, ¿te gustaría que te recordara?"

Día 90: "En 3 meses contigo, he detectado patrón: cuando tienes proyecto grande + estrés, tiendes a saltarte ejercicio. Hoy combinación similar. Bloqueé 30min para caminar."
```

---

### 2. Sistema de Reloj Interno (Temporal Awareness)

**Qué es**: Sendell concibe el tiempo como recurso útil, no solo como timestamp.

**Componentes**:

```python
class TemporalClock:
    current_time: datetime
    user_timezone: str
    time_contexts: Dict[str, TimeContext]

    # Contextos de tiempo
    - morning_routine: 6am-9am
    - work_hours: 9am-6pm
    - evening_routine: 6pm-9pm
    - sleep_time: 10pm-6am
    - weekend_mode: Saturday-Sunday

    # Medición de tiempo útil
    productive_hours_today: int
    time_spent_on_tasks: Dict[str, int]  # task_id -> minutes
```

**Funcionalidades**:

1. **Saber qué hora es y qué significa**:
   - 7am = "Usuario despertando, momento para recordatorio suave"
   - 2pm = "Mitad del día, buen momento para check-in si es necesario"
   - 10pm = "Casi hora de dormir, solo urgencias"

2. **Trackear uso del tiempo del usuario**:
   - Cuánto tiempo estuvo en cada app
   - Cuánto tiempo dedicó a proyectos
   - Cuándo fue productivo vs distraído

3. **Proponer uso óptimo del tiempo**:
   - "Tienes 2 horas libres entre reuniones, perfecto para [tarea que mencionaste]"
   - "Llevas 3 horas en código, ¿break de 15min?"

---

### 3. Sistema de Memoria Personal Expandida

**Qué es**: Más allá de "facts", memoria estructurada sobre el usuario como persona.

**Estructura de memoria**:

```python
class PersonalMemory:
    # PERSONA (no trabajo)
    personal_info: Dict
        - name: str
        - family: List[FamilyMember]  # "Abuela María", "Hermano Juan"
        - friends: List[Friend]
        - pets: List[Pet]

    # HÁBITOS Y RUTINAS
    habits: List[Habit]
        - habit_name: "Llamar a la abuela"
        - frequency: "weekly"  # daily, weekly, monthly
        - preferred_time: "domingo 5pm"
        - last_done: datetime
        - streak: int
        - importance: float  # 0-1

    routines: List[Routine]
        - routine_name: "Aseo semanal"
        - tasks: ["lavar platos", "barrer", "lavar ropa"]
        - preferred_day: "sábado"
        - last_done: datetime

    # PROYECTOS PERSONALES (no trabajo)
    personal_projects: List[Project]
        - project_name: "Aprender guitarra"
        - goal: "Tocar 3 canciones"
        - status: "in_progress"
        - last_worked_on: datetime
        - next_action: "Practicar 30min"

    # INTERESES Y ASPIRACIONES
    interests: List[str]  # "leer", "ejercicio", "cocinar"
    goals: List[Goal]
        - goal: "Leer 12 libros este año"
        - progress: "3/12"
        - deadline: "2025-12-31"

    # PATRONES DETECTADOS
    patterns: List[Pattern]
        - pattern_type: "procrastination"
        - description: "Siempre pospone llamar a familia los domingos"
        - confidence: 0.85
        - detected_at: datetime
```

**Ejemplo de datos**:

```json
{
  "personal_info": {
    "name": "Daniel",
    "family": [
      {"name": "Abuela María", "relationship": "grandmother", "contact_frequency": "weekly"}
    ]
  },
  "habits": [
    {
      "habit_name": "Llamar a la abuela",
      "frequency": "weekly",
      "preferred_time": "domingo 5pm",
      "last_done": "2025-10-21",
      "streak": 3,
      "importance": 0.9
    },
    {
      "habit_name": "Leer 30 minutos",
      "frequency": "daily",
      "preferred_time": "noche",
      "last_done": "2025-10-26",
      "streak": 5,
      "importance": 0.7
    }
  ],
  "routines": [
    {
      "routine_name": "Aseo semanal",
      "tasks": ["lavar platos", "barrer", "lavar ropa"],
      "preferred_day": "sábado",
      "last_done": "2025-10-19"
    }
  ],
  "personal_projects": [
    {
      "project_name": "Sendell Agent",
      "goal": "Lanzar v0.2 con proactividad",
      "status": "in_progress",
      "last_worked_on": "2025-10-28",
      "next_action": "Implementar sistema de recordatorios"
    }
  ]
}
```

---

### 4. Sistema de Recordatorios y Tareas Personales

**Qué es**: Sendell puede recordar cosas que el usuario pidió que le recuerde.

**Tipos de recordatorios**:

1. **One-time** (una sola vez):
   - "Recuérdame llamar al doctor mañana 10am"
   - "Recuérdame sacar la basura esta noche"

2. **Recurring** (recurrentes):
   - "Recuérdame llamar a mi abuela todos los domingos"
   - "Recuérdame hacer ejercicio 3 veces por semana"

3. **Conditional** (basados en contexto):
   - "Recuérdame comprar leche cuando vaya al supermercado"
   - "Recuérdame revisar el proyecto X cuando tenga tiempo libre"

**Estructura**:

```python
class Reminder:
    reminder_id: str
    user_id: str
    content: str
    reminder_type: str  # "one_time", "recurring", "conditional"
    trigger_type: str   # "time", "location", "context", "pattern"

    # Para time-based
    trigger_time: Optional[datetime]
    recurrence: Optional[str]  # "daily", "weekly", "monthly"

    # Para context-based
    trigger_context: Optional[str]  # "when free", "after work", "on weekend"

    # Metadata
    importance: float  # 0-1
    created_at: datetime
    last_reminded: Optional[datetime]
    times_snoozed: int
    completed: bool
```

**Ejemplos**:

```python
# One-time
Reminder(
    content="Llamar al doctor",
    reminder_type="one_time",
    trigger_type="time",
    trigger_time=datetime(2025, 10, 29, 10, 0),
    importance=0.8
)

# Recurring
Reminder(
    content="Llamar a la abuela",
    reminder_type="recurring",
    trigger_type="time",
    recurrence="weekly_sunday_17:00",
    importance=0.9
)

# Conditional
Reminder(
    content="Revisar progreso del proyecto Sendell",
    reminder_type="conditional",
    trigger_type="context",
    trigger_context="when_free_time_2hours",
    importance=0.7
)
```

---

### 5. Sistema de Atención Temporal Adaptativo (Urgency Scoring)

**Qué es**: Sendell decide **cuándo** intervenir basándose en múltiples factores, no en intervalos fijos.

**Cálculo de urgencia**:

```python
def calculate_urgency_score(context: Context) -> float:
    """
    Retorna score 0-1 que determina cuándo actuar

    0.0-0.3: Low urgency (puede esperar días)
    0.3-0.6: Medium urgency (puede esperar horas)
    0.6-0.8: High urgency (actuar en próxima hora)
    0.8-1.0: Critical (actuar inmediatamente)
    """
    urgency = 0.0

    # Factor 1: Deadlines cercanos mencionados
    if has_deadline_within_24h(context):
        urgency += 0.4
    elif has_deadline_within_48h(context):
        urgency += 0.2

    # Factor 2: Hábito no cumplido
    if habit_overdue(context):
        days_overdue = days_since_last_done(context.habit)
        urgency += min(0.3, days_overdue * 0.1)

    # Factor 3: Tiempo sin contacto vs promesa de acción
    if promised_action_not_done(context):
        urgency += 0.3

    # Factor 4: Patrón de procrastinación detectado
    if procrastination_pattern_matches(context):
        urgency += 0.2

    # Factor 5: Usuario pidió recordatorio
    if explicit_reminder_requested(context):
        urgency += 0.5

    # Factor 6: Tiempo óptimo del día
    if is_optimal_time_for_user(context):
        urgency += 0.1

    return min(1.0, urgency)
```

**Conversión de urgency a timing**:

```python
def urgency_to_next_interaction(urgency: float) -> timedelta:
    """
    Convierte score de urgencia a tiempo de espera
    """
    if urgency >= 0.8:
        return timedelta(minutes=15)  # Crítico: 15 minutos
    elif urgency >= 0.6:
        return timedelta(hours=1)     # Alto: 1 hora
    elif urgency >= 0.4:
        return timedelta(hours=4)     # Medio: 4 horas
    else:
        return timedelta(hours=24)    # Bajo: mañana
```

**Ejemplos de cálculo**:

Escenario 1: "Usuario mencionó deadline viernes, hoy es miércoles"
- has_deadline_within_48h = +0.2
- **Score: 0.2** → Esperar 24 horas, recordar mañana

Escenario 2: "Hábito 'llamar abuela' no cumplido en 7 días, es domingo 5pm"
- habit_overdue (7 días) = +0.3
- is_optimal_time = +0.1
- **Score: 0.4** → Esperar 4 horas, recordar a las 9pm

Escenario 3: "Usuario dijo 'recuérdame llamar al doctor mañana 10am', ya son las 10am"
- explicit_reminder_requested = +0.5
- has_deadline_within_24h = +0.4
- **Score: 0.9** → Crítico, notificar ahora

---

## Arquitectura de Software

### Nuevos Módulos

```
src/sendell/
├── proactive/                    # NUEVO
│   ├── __init__.py
│   ├── identity.py               # AgentIdentity, relationship phases
│   ├── temporal_clock.py         # Reloj interno, time awareness
│   ├── personal_memory.py        # Memoria personal expandida
│   ├── reminders.py              # Sistema de recordatorios
│   ├── attention_system.py       # Urgency scoring, timing optimizer
│   └── proactive_loop.py         # Loop principal proactivo
```

### Flujo del Loop Proactivo

```python
async def proactive_monitoring_loop():
    """
    Loop principal que corre en background
    """
    while True:
        # 1. Observar (passive, siempre activo)
        signals = await observe_user_context()

        # 2. Analizar significancia
        important_signals = await filter_important_signals(signals)

        # 3. Calcular urgencia para cada signal
        for signal in important_signals:
            urgency = calculate_urgency_score(signal)
            timing = urgency_to_next_interaction(urgency)

            # 4. Decidir si actuar ahora o programar
            if urgency >= 0.8:
                await take_proactive_action(signal)
            else:
                await schedule_action(signal, timing)

        # 5. Revisar recordatorios pendientes
        due_reminders = await check_due_reminders()
        for reminder in due_reminders:
            await send_reminder(reminder)

        # 6. Actualizar identidad y memoria
        await update_relationship_age()
        await update_patterns()

        # 7. Reflexión diaria (si es fin del día)
        if is_end_of_day():
            await daily_reflection()

        # 8. Esperar próximo ciclo
        await asyncio.sleep(check_interval)
```

---

## Implementación por Fases

### Fase 1: Fundación (Semana 1)

**Objetivo**: Sendell tiene identidad temporal y reloj interno.

**Tareas**:
1. Crear módulo `identity.py`:
   - AgentIdentity con birth_date
   - Cálculo de relationship_age
   - Determinación de relationship_phase
2. Crear módulo `temporal_clock.py`:
   - TemporalClock con time contexts
   - Funciones para saber "qué hora es" y "qué significa"
3. Actualizar memoria JSON para incluir agent_identity
4. Testing: Verificar que Sendell sabe hace cuánto "nació"

**Validación**:
```python
# En chat
You: "Cuánto tiempo llevas conmigo?"
Sendell: "Es mi 5to día contigo. Aún estoy en fase de nacimiento, aprendiendo tu ritmo."
```

---

### Fase 2: Memoria Personal (Semana 2)

**Objetivo**: Sendell conoce al usuario como persona.

**Tareas**:
1. Crear módulo `personal_memory.py`:
   - Clases Habit, Routine, PersonalProject, Goal
   - CRUD de memoria personal
2. Actualizar memoria JSON con estructura expandida
3. GUI: Agregar tab "Vida Personal" en brain_gui
4. Testing: Agregar hábitos y rutinas manualmente

**Validación**:
```python
# Agregar desde GUI o chat
You: "Quiero que me recuerdes llamar a mi abuela todos los domingos"
Sendell: "Entendido. Agregué hábito 'Llamar a la abuela' con frecuencia semanal los domingos. ¿A qué hora prefieres que te recuerde?"
```

---

### Fase 3: Recordatorios Básicos (Semana 3)

**Objetivo**: Sendell recuerda cosas que le pides.

**Tareas**:
1. Crear módulo `reminders.py`:
   - Clase Reminder con tipos (one_time, recurring, conditional)
   - CRUD de recordatorios
2. Implementar trigger system para time-based reminders
3. Integrar con loop proactivo
4. Testing: Crear recordatorios y verificar que se disparan

**Validación**:
```python
You: "Recuérdame llamar al doctor mañana a las 10am"
Sendell: "Listo. Te recordaré mañana 29 de octubre a las 10:00 AM."

# Al día siguiente a las 10am
Sendell: "¡Recordatorio! Debes llamar al doctor."
```

---

### Fase 4: Urgency Scoring (Semana 4)

**Objetivo**: Sendell decide cuándo intervenir inteligentemente.

**Tareas**:
1. Crear módulo `attention_system.py`:
   - Función calculate_urgency_score
   - Función urgency_to_next_interaction
2. Implementar factores de urgencia (deadlines, hábitos, patrones)
3. Integrar con loop proactivo
4. Testing: Verificar que intervenciones son oportunas

**Validación**:
```python
# Hábito "llamar abuela" no cumplido en 7 días, es domingo 5pm
Sendell: "Es domingo 5pm. Hace 7 días que no llamas a tu abuela. Dijiste que querías hacerlo semanalmente. ¿Te gustaría que te recordara?"
```

---

### Fase 5: Loop Proactivo Completo (Semana 5)

**Objetivo**: Sendell monitorea proactivamente sin intervenciones constantes.

**Tareas**:
1. Crear módulo `proactive_loop.py`:
   - Loop completo con todos los sistemas
2. Implementar daily_reflection (reflexión al final del día)
3. Sistema de feedback (¿Esto te ayudó?)
4. Testing: Dejar correr 7 días y validar comportamiento

**Validación**:
```python
# Al final del día
Sendell: "Día completado. Hoy tuvimos 2 interacciones. Te ayudé con 1 recordatorio que cumpliste. He notado que trabajaste 6 horas en código, ¿cómo te sientes con el progreso?"
```

---

## Principios de Diseño

### 1. Respeto al Usuario

- **Nunca spam**: Prefiere 1 intervención valiosa que 10 molestas
- **Siempre pregunta primero** (si estás en L2): "¿Te gustaría que...?"
- **Respeta contexto**: No interrumpas en momentos malos (reuniones, noche)

### 2. Transparencia

- **Explica por qué**: "Te recuerdo esto porque dijiste que querías..."
- **Muestra confianza**: "Estoy 85% seguro que esto te ayudará"
- **Admite errores**: "Me equivoqué, esto no fue útil. ¿Cómo lo mejoro?"

### 3. Evolución Gradual

- **Fase 1 (días 1-7)**: Tímido, solo recordatorios explícitos
- **Fase 2 (días 8-30)**: Empieza a sugerir basado en patrones
- **Fase 3 (días 30+)**: Intervenciones anticipatorias

### 4. Medición

- **Track everything**:
  - Cuántas intervenciones proactivas
  - Cuántas fueron útiles vs molestas
  - Accuracy de predicciones
  - Tiempo de respuesta del usuario
- **Aprende del feedback**: Si usuario ignora recordatorio 3 veces, ajustar

---

## Métricas de Éxito

### Fase 1-2 (Fundación)
- ✅ Sendell sabe hace cuánto "nació"
- ✅ Usuario puede agregar hábitos/rutinas
- ✅ Memoria personal se persiste correctamente

### Fase 3 (Recordatorios)
- ✅ 95%+ de recordatorios se disparan a tiempo
- ✅ Usuario puede crear/editar/eliminar recordatorios
- ✅ Recurring reminders funcionan correctamente

### Fase 4-5 (Proactividad)
- ✅ Urgency score correlaciona con importancia real
- ✅ Intervenciones proactivas útiles >80%
- ✅ Falsos positivos (molestias) <10%
- ✅ Usuario siente que Sendell "lo conoce"

---

## Próximos Pasos (Después de v0.2)

### v0.3: Detección de Patrones
- Sendell detecta automáticamente hábitos sin que se lo digas
- "He notado que siempre revisas email 8:30am. ¿Te envío resumen justo antes?"

### v0.4: Integración con Calendario/Email
- Sendell sincroniza con Google Calendar
- Detecta conflictos, sugiere optimizaciones
- Lee emails importantes y extrae action items

### v0.5: Análisis de Productividad
- Trackea tiempo en cada actividad
- Sugiere mejoras: "Pasas 3h/día en meetings, ¿reducir?"
- Identifica cuándo eres más productivo

### v1.0: Maestría
- Intervenciones quirúrgicas de alto valor
- Anticipa necesidades antes que las pidas
- Se siente como extensión de ti mismo

---

## Notas de Implementación

### Almacenamiento

**Actualizar** `data/sendell_memory.json`:

```json
{
  "agent_identity": {
    "birth_date": "2025-10-28T14:30:00",
    "relationship_age_days": 5,
    "confidence_level": 0.15,
    "relationship_phase": "birth",
    "milestones": []
  },
  "personal_memory": {
    "personal_info": {...},
    "habits": [...],
    "routines": [...],
    "personal_projects": [...],
    "goals": [...],
    "patterns": [...]
  },
  "reminders": [...],
  "facts": [...],
  "conversations": [...],
  "sessions": [...]
}
```

### Comandos CLI Nuevos

```powershell
# Agregar hábito
uv run python -m sendell habit add "Llamar a la abuela" --frequency weekly --day sunday --time 17:00

# Agregar recordatorio
uv run python -m sendell remind "Llamar al doctor" --when "tomorrow 10am"

# Ver estado del agente
uv run python -m sendell status
# Output: "Es mi día 5 contigo. Fase: Birth. Tienes 3 hábitos configurados, 2 recordatorios pendientes."

# Reflexión del día
uv run python -m sendell reflect
# Output muestra resumen del día
```

---

## Conclusión

Esta arquitectura transforma Sendell de un agente reactivo a uno verdaderamente proactivo. El enfoque en el **usuario como persona** (no solo trabajador) es el diferenciador clave. La implementación es **progresiva**, **medida**, y **adaptable**.

**El objetivo**: Que después de 90 días, Daniel sienta que Sendell realmente lo conoce y las intervenciones sean tan valiosas que las espere con gusto.

---

**Última actualización**: 2025-10-28
**Próximo paso**: Implementar Fase 1 (Fundación)
