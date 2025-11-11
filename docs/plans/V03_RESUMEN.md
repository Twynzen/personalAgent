# V0.3 - RESUMEN EJECUTIVO

**Branch**: `feature/brain-projects-tab`
**Estado**: Listo para implementar
**Tiempo estimado**: 4-5 sesiones

---

## 🎯 QUÉ VAMOS A HACER

Agregar **Tab 4 "Proyectos"** al Brain GUI existente = **Centro de Control Multi-Proyecto**

### Antes (Brain GUI actual):
```
uv run python -m sendell brain
├── Tab 1: Memorias
├── Tab 2: Prompts
└── Tab 3: Herramientas
```

### Después (Brain GUI mejorado):
```
uv run python -m sendell brain
├── Tab 1: Memorias
├── Tab 2: Prompts
├── Tab 3: Herramientas
└── Tab 4: PROYECTOS ← NUEVO
    ├── Métricas (CPU, RAM, Terminales)
    ├── Lista de proyectos VS Code detectados
    ├── Gráficos de actividad animados
    └── Paneles de configuración por proyecto
```

---

## ✨ CARACTERÍSTICAS PRINCIPALES

### 1. Monitor Multi-Proyecto
- Detecta **todos los proyectos VS Code abiertos** (usando psutil)
- Muestra: nombre, ruta, status (running/idle)
- Actualiza cada 5 segundos automáticamente

### 2. Gráficos Animados
- Canvas con animaciones tipo cyberpunk
- Línea verde pulsante si el proyecto está activo
- Línea gris si está idle
- Actualiza en tiempo real

### 3. Métricas del Sistema
- CPU total (%)
- RAM total (%)
- Total de terminales activas
- Colores neón cyberpunk (#00ff41, #ffed4e, #00d4ff)

### 4. Paneles Expandibles
- Click en "⚙ CONFIG" para expandir
- Muestra ruta completa del proyecto
- Botones de acción:
  - 📂 Abrir en Explorador
  - 🗑️ Remover de Lista

### 5. Threading Correcto
- **GARANTÍA: UI NUNCA SE CONGELA**
- Background worker hace el trabajo pesado
- Queue thread-safe para comunicación
- UI siempre responsive

---

## 🏗️ ARQUITECTURA

```
Brain GUI (ventana principal)
├── Tab 1-3: Existentes (sin cambios)
└── Tab 4: ProjectControlWidget
    ├── Header (botones, reloj)
    ├── MetricsPanel (lado izquierdo)
    │   ├── CPU gauge
    │   ├── RAM gauge
    │   └── Terminales count
    └── ProjectsList (lado derecho, scrollable)
        └── ProjectCard (x N proyectos)
            ├── Header (emoji + nombre + CONFIG)
            ├── PulseGraph (Canvas animado)
            └── ConfigPanel (expandible)

Background Thread (daemon)
├── Escanea cada 5 segundos
├── Detecta proyectos VS Code
├── Calcula métricas
└── Envía updates vía Queue
```

---

## 📋 FASES DE IMPLEMENTACIÓN

### **Fase 0: Integración** (0.5 sesión)
- Modificar `brain_gui.py`
- Agregar Tab 4
- Crear módulo `dashboard/`
- Placeholder funcional

### **Fase 1: Threading** (0.5 sesión)
- Background worker
- Queue pattern
- Detección de proyectos

### **Fase 2: Métricas** (0.5 sesión)
- Panel izquierdo
- CPU, RAM, Terminales
- Colores cyberpunk

### **Fase 3: Lista de Proyectos** (1 sesión)
- ProjectCard widgets
- Scrollable list
- Grid placeholders

### **Fase 4: Gráficos** (1 sesión)
- Canvas animations
- Pulse graphs
- Real-time updates

### **Fase 5: Config Panels** (1 sesión)
- Expandible panels
- Botones de acción
- "Abrir en Explorador" funcional

### **Fase 6: Polish** (0.5 sesión)
- Header completo
- Reloj en tiempo real
- Botones ESCANEAR/ACTUALIZAR

---

## 🧪 TESTING

### Test crítico: No-Freeze
```
1. Abre Brain GUI
2. Ve a Tab "Proyectos"
3. Mueve ventana mientras actualiza
4. Click en tabs mientras actualiza
5. Expand/collapse panels

✅ PASS: UI responde instantáneamente
❌ FAIL: Cualquier congelamiento
```

### Test funcional: Detección
```
1. Abre 3 VS Code con proyectos diferentes
2. Dashboard debe mostrar los 3 correctamente
3. Abre nueva terminal en uno
4. Espera 5 segundos
5. Dashboard muestra cambio

✅ PASS: Detección 100% precisa
```

---

## 🎨 ASPECTO VISUAL

**Inspiración**: React cyberpunk dashboard de Daniel

**Colores**:
- Background: `#0a0a0a` (negro profundo)
- Paneles: `#1a1a1a` (gris oscuro)
- Activo: `#00ff41` (verde neón)
- Métricas: `#ffed4e` (amarillo neón)
- Acciones: `#00d4ff` (cyan)

**Diseño**:
- Minimalista pero funcional
- Animaciones suaves (no distracciones)
- Información clara y legible
- Separación visual entre proyectos

---

## ✅ CRITERIOS DE ÉXITO

Al finalizar v0.3, el usuario debe poder:

1. ✅ Abrir `sendell brain` y ver 4 tabs
2. ✅ Ver todos sus proyectos VS Code activos
3. ✅ Ver métricas del sistema en tiempo real
4. ✅ Ver actividad de cada proyecto (gráficos)
5. ✅ Expandir config de cualquier proyecto
6. ✅ Abrir proyecto en explorador con 1 click
7. ✅ **UI NUNCA se congela** (threading correcto)

---

## 🚫 NO ES OBJETIVO v0.3

- ❌ Enviar comandos a terminales
- ❌ WebSocket como fuente primaria
- ❌ Control avanzado de proyectos
- ❌ Coordinación multi-agente
- ❌ Features complejas sin valor claro

Esas features van para **v0.4+** cuando tengamos base sólida.

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
src/sendell/
├── agent/
│   └── brain_gui.py          # MODIFICAR (agregar Tab 4)
│
└── dashboard/                # NUEVO módulo
    ├── __init__.py
    ├── project_control.py    # Widget principal del tab
    ├── components/
    │   ├── __init__.py
    │   ├── header.py         # Header con botones
    │   ├── metrics_panel.py  # Panel de métricas
    │   └── project_card.py   # Card de proyecto con graph
    └── utils/
        ├── __init__.py
        ├── colors.py         # Constantes de colores
        └── threading.py      # Threading helpers
```

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Branch creada: `feature/brain-projects-tab`
2. ⏳ Implementar Fase 0 (integración con Brain GUI)
3. ⏳ Implementar Fases 1-6 secuencialmente
4. ⏳ Testing exhaustivo
5. ⏳ Merge a main cuando esté 100% funcional

---

**🎯 Objetivo final**: Un centro de control hermoso, funcional y que NO se congele, integrado naturalmente en el Brain GUI existente.

**💡 Filosofía**: Simple > Complex. Features que funcionan > Arquitectura fancy.
