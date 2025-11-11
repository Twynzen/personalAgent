# 📚 SENDELL DOCUMENTATION GUIDE

**Propósito**: Guía clara de qué documentos leer, cuándo, y por qué.

---

## 🎯 PARA CLAUDE: ORDEN DE LECTURA

### 1. **SIEMPRE LEER PRIMERO** (Context critical)

#### `claude.md` (root) - ⭐ MEMORIA PERMANENTE
- **Qué es**: Estado actual del proyecto + historial condensado
- **Cuándo leer**: Al inicio de CADA sesión
- **Última actualización**: 2025-11-11 (730 líneas, optimizado)
- **Contenido clave**:
  - Estado actual (primeras 50 líneas)
  - Workflow establecido Daniel-Claude
  - Arquitectura completa (Python + Angular)
  - Versiones completadas (v0.1, v0.2, v0.3)
  - Decisiones arquitectónicas críticas
  - Próximos pasos

### 2. **LEER SEGÚN TAREA ACTUAL** (Context for specific work)

#### `docs/plans/NEXT_SESSION_PLAN.md` - 📋 PLAN INMEDIATO
- **Qué es**: Plan detallado para continuar v0.3 Fase 4
- **Cuándo leer**: Cuando Daniel dice "continúa donde lo dejamos"
- **Contenido**: Build dashboard, Testing E2E, Phase 4 implementation
- **Fecha**: 2025-11-11 (450 líneas)

#### `docs/core/TERMINAL_ISSUES.md` - 🐛 BUG REPORT ACTUAL
- **Qué es**: Problemas identificados en Captura.png con soluciones
- **Cuándo leer**: Cuando Daniel dice "arregla las terminales"
- **Contenido**: 3 bugs críticos + soluciones propuestas
- **Fecha**: 2025-11-11 (500 líneas)

#### `docs/plans/V03_RESUMEN.md` - 📊 RESUMEN v0.3
- **Qué es**: Qué se implementó en v0.3, por qué, cómo
- **Cuándo leer**: Si necesitas context de decisiones v0.3
- **Contenido**: Dashboard Angular, terminales, arquitectura
- **Fecha**: 2025-11-06 (250 líneas)

### 3. **REFERENCE DOCS** (Consultar cuando necesario)

#### `README.md` (root) - 📖 USUARIO FINAL
- **Qué es**: Documentación para usuarios (no para desarrollo)
- **Cuándo leer**: Nunca (a menos que Daniel pregunte sobre UX)

#### `TUTORIAL.md` (root) - 🎓 TUTORIAL USUARIO
- **Qué es**: Tutorial paso a paso para usar Sendell
- **Cuándo leer**: Nunca (documentación de usuario)

### 4. **ARCHIVED** (NO leer a menos que Daniel lo solicite)

**Ubicación**: `docs/archive/`

Estos docs son históricos o de planes abandonados:
- `CLAUDE_CODE_INTEGRATION_PLAN.md` - Plan futuro (v0.4+)
- `V03_SIMPLIFIED_PLAN.md` - Plan original v0.3 (modificado)
- `IMPLEMENTATION_STATUS.md` - Status obsoleto
- `MIGRATION_PLAN_ANGULAR.md` - Plan de migración (completado)
- `PROACTIVITY_DESIGN.md` - Diseño v0.2 (completado)
- `MISSING_INTEGRATION.md` - Gaps identificados (resueltos parcialmente)

### 5. **RESEARCH** (Investigaciones de Daniel)

**Ubicación**: `docs/research/`

Investigaciones técnicas de Daniel (SOLO leer si Daniel lo menciona):
- `investigacionterminalsguide.txt` - Terminal control research
- `investigacionvscodeextensionintegration.txt` - VS Code extension research
- `investigacionvscodemonitoring.txt` - VS Code monitoring methods
- `iapersonal.txt` - Stack tecnológico original
- `proactividad.txt` - Diseño proactividad v0.2
- `sendellguia.txt` - Guía original del proyecto
- `asciiguia.txt` - ASCII art research (v0.2)
- `langgraph.txt` - LangGraph API documentation

**IMPORTANTE**: Estas investigaciones son HISTÓRICAS. NO implementar nada sin que Daniel lo confirme primero.

---

## 🗂️ ESTRUCTURA FINAL

```
sendell/
├── claude.md                          ⭐ LEER SIEMPRE PRIMERO
├── README.md                          📖 Usuario final
├── TUTORIAL.md                        🎓 Tutorial usuario
│
├── docs/
│   ├── README_DOCS.md                 📚 ESTA GUÍA
│   │
│   ├── core/                          📋 Documentos activos actuales
│   │   ├── TERMINAL_ISSUES.md         🐛 Bugs actuales + soluciones
│   │   └── NEXT_SESSION_PLAN.md       📋 Próximos pasos inmediatos
│   │
│   ├── plans/                         📊 Planes y resúmenes
│   │   ├── V03_RESUMEN.md             v0.3 resumen ejecutivo
│   │   └── V03_SIMPLIFIED_PLAN.md     v0.3 plan original (ref)
│   │
│   ├── archive/                       🗄️ Histórico / No leer
│   │   ├── CLAUDE_CODE_INTEGRATION_PLAN.md
│   │   ├── IMPLEMENTATION_STATUS.md
│   │   ├── MIGRATION_PLAN_ANGULAR.md
│   │   ├── PROACTIVITY_DESIGN.md
│   │   ├── MISSING_INTEGRATION.md
│   │   ├── VSCODE_INTEGRATION_README.md
│   │   ├── VSCODE_EXTENSION_SUMMARY.md
│   │   ├── PROJECT_MANAGEMENT_SUMMARY.md
│   │   ├── INVESTIGATION_PROMPT_VSCODE_EXTENSION_DEEP.md
│   │   └── COMMIT_MESSAGE.txt
│   │
│   └── research/                      🔬 Investigaciones de Daniel
│       ├── investigacionterminalsguide.txt
│       ├── investigacionvscodeextensionintegration.txt
│       ├── investigacionvscodemonitoring.txt
│       ├── iapersonal.txt
│       ├── proactividad.txt
│       ├── sendellguia.txt
│       ├── asciiguia.txt
│       └── langgraph.txt
```

---

## 📖 WORKFLOW DE LECTURA

### Escenario 1: "Nueva sesión, continúa el trabajo"
1. ✅ Leer `claude.md` (primeras 100 líneas para contexto)
2. ✅ Leer `docs/core/NEXT_SESSION_PLAN.md` (plan específico)
3. ✅ Verificar `docs/core/TERMINAL_ISSUES.md` (bugs pendientes)
4. ✅ Continuar trabajo

### Escenario 2: "Arregla los bugs de las terminales"
1. ✅ Leer `docs/core/TERMINAL_ISSUES.md` (problema + soluciones)
2. ✅ Consultar `claude.md` si necesitas context de arquitectura
3. ✅ Implementar fixes

### Escenario 3: "Revisa la investigación de X que te pasé"
1. ✅ Daniel especificará archivo (ej: `investigacionterminalsguide.txt`)
2. ✅ Leer ese archivo en `docs/research/`
3. ✅ NO asumir, preguntar dudas a Daniel

### Escenario 4: "Documenta lo que hiciste hoy"
1. ✅ Actualizar `claude.md` (sección "Estado Actual")
2. ✅ Si es plan futuro → crear en `docs/plans/`
3. ✅ Si es bug encontrado → crear en `docs/core/`

---

## ⚠️ REGLAS IMPORTANTES

1. **NUNCA leer docs de `archive/` sin que Daniel lo pida**
   - Son planes obsoletos o completados
   - Pueden tener info contradictoria con estado actual

2. **NUNCA leer research de `docs/research/` proactivamente**
   - Son investigaciones históricas de Daniel
   - NO implementar nada sin confirmación

3. **SIEMPRE empezar con `claude.md`**
   - Es la fuente de verdad
   - Estado actual + decisiones críticas

4. **Preferir docs en `docs/core/` sobre archive**
   - Core = trabajo actual
   - Archive = historia

5. **Actualizar `claude.md` al final de cada sesión significativa**
   - Mantener "Estado Actual" actualizado
   - Condensar trabajo en historial

---

## 🔄 MANTENIMIENTO

### Cuando crear nuevo documento:

**Crear en `docs/core/`** si:
- Es bug report actual
- Es plan inmediato (próxima sesión)
- Es decisión crítica que afecta desarrollo

**Crear en `docs/plans/`** si:
- Es resumen de fase completada
- Es plan a mediano plazo (v0.4+)

**Mover a `docs/archive/`** cuando:
- Plan completado (ya no relevante)
- Bug resuelto y no hay seguimiento
- Investigación superada por nueva decisión

### Limpieza periódica:

Cada 5 sesiones o al completar versión mayor:
1. Revisar `docs/core/` → mover docs resueltos a `archive/`
2. Actualizar `claude.md` con lecciones aprendidas
3. Eliminar duplicados o docs redundantes

---

## 📊 JERARQUÍA DE IMPORTANCIA

1. ⭐⭐⭐ **`claude.md`** - Memoria permanente, SIEMPRE actualizado
2. ⭐⭐ **`docs/core/*`** - Trabajo actual, bugs, planes inmediatos
3. ⭐ **`docs/plans/*`** - Context de decisiones pasadas
4. 📦 **`docs/archive/*`** - Referencia histórica, NO leer por defecto
5. 🔬 **`docs/research/*`** - Solo cuando Daniel lo indique

---

**Última actualización**: 2025-11-11
**Próxima revisión**: Después de completar v0.3

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
