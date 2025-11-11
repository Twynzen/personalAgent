"""
Test script para detección de terminales Claude Code

Ejecuta esto con Claude Code abierto para probar la detección.
"""

import json
from sendell.terminal_control import ClaudeTerminalDetector, CommandExecutor


def main():
    print("=" * 70)
    print("TEST: Detección de Terminales Claude Code")
    print("=" * 70)

    detector = ClaudeTerminalDetector()

    # TEST 1: Detectar procesos de VS Code
    print("\n[1/4] Buscando procesos VS Code...")
    vscode_procs = detector.find_vscode_processes()
    print(f"[OK] Encontrados {len(vscode_procs)} procesos VS Code")

    for proc in vscode_procs[:3]:  # Mostrar primeros 3
        print(f"  - PID {proc['pid']}: {proc['name']}")
        print(f"    CWD: {proc['cwd']}")

    if len(vscode_procs) > 3:
        print(f"  ... y {len(vscode_procs) - 3} más")

    # TEST 2: Detectar procesos de Claude Code
    print("\n[2/4] Buscando procesos Claude Code...")
    claude_procs = detector.find_claude_code_processes()

    if claude_procs:
        print(f"[OK] Encontrados {len(claude_procs)} procesos Claude Code\n")

        for proc in claude_procs:
            print(f"  PID: {proc['pid']}")
            print(f"  Nombre: {proc['name']}")
            print(f"  Estado: {'[ACTIVO]' if proc['is_active'] else '[IDLE]'}")
            print(f"  CPU: {proc['cpu_percent']}%")
            print(f"  Memoria: {proc['memory_mb']} MB")
            print(f"  CWD: {proc['cwd']}")
            print(f"  Cmdline: {proc['cmdline'][:100]}...")
            print()
    else:
        print("[!] No se encontraron procesos Claude Code")
        print("  Tip: Abre un terminal y ejecuta 'claude' primero")

    # TEST 3: Buscar sesiones activas
    print("\n[3/4] Buscando sesiones activas en ~/.claude/projects...")
    sessions = detector.find_active_sessions(max_age_minutes=60)

    if sessions:
        print(f"[OK] Encontradas {len(sessions)} sesiones activas\n")

        for session in sessions:
            print(f"  Proyecto: {session['project']}")
            print(f"  Estado: {session['state'].upper()}")
            print(f"  Eventos: {session['event_count']}")

            if 'token_usage' in session:
                tokens = session['token_usage']
                print(f"  Tokens: {tokens['total']} (in:{tokens['input']}, out:{tokens['output']})")

            if session.get('seconds_since_last_event'):
                print(f"  Ultima actividad: hace {session['seconds_since_last_event']:.0f}s")

            print()
    else:
        print("[!] No se encontraron sesiones activas")
        print("  Directorio ~/.claude/projects no existe o esta vacio")

    # TEST 4: Reporte completo
    print("\n[4/4] Generando reporte completo...")
    report = detector.get_full_report()

    print(f"\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"VS Code procesos: {len(report['vscode_processes'])}")
    print(f"Claude procesos:  {len(report['claude_processes'])}")
    print(f"Sesiones activas: {len(report['active_sessions'])}")
    print(f"Timestamp:        {report['timestamp']}")

    # Guardar reporte completo en JSON
    output_file = "terminal_detection_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Reporte completo guardado en: {output_file}")

    # TEST BONUS: Comando simple
    print("\n" + "=" * 70)
    print("TEST BONUS: Ejecutar comando simple")
    print("=" * 70)

    executor = CommandExecutor()
    result = executor.execute_simple("python --version")

    if result['success']:
        print(f"[OK] Comando exitoso")
        print(f"  Output: {result['stdout'].strip()}")
    else:
        print(f"[ERROR] Comando fallo")
        print(f"  Error: {result.get('error', 'Unknown')}")

    print("\n" + "=" * 70)
    print("Testing completado!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por usuario")
    except Exception as e:
        print(f"\n[ERROR] Error durante test: {e}")
        import traceback
        traceback.print_exc()
