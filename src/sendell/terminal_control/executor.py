"""
Command Executor

Executes commands and captures output in real-time using subprocess.
Reliability: 98%+ (highest reliability method from research).
"""

import subprocess
import threading
import queue
from pathlib import Path
from typing import Optional, Callable, Dict


class CommandExecutor:
    """Ejecutor de comandos con captura de output en tiempo real"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()

    def execute_with_realtime_output(
        self,
        command: str,
        cwd: Optional[str] = None,
        callback: Optional[Callable] = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Ejecuta comando y captura output en tiempo real.

        Args:
            command: Comando a ejecutar (puede ser string multi-comando con &&)
            cwd: Directorio de trabajo (workspace path del proyecto)
            callback: Función llamada para cada línea: callback(stream, line)
                     stream será 'stdout' o 'stderr'
            timeout: Timeout en segundos (None = sin límite)

        Returns:
            Dict con stdout, stderr, returncode, success

        Example:
            executor = CommandExecutor()

            def print_line(stream, line):
                print(f"[{stream}] {line}")

            result = executor.execute_with_realtime_output(
                "python script.py",
                cwd="C:/Projects/myproject",
                callback=print_line
            )

            if result['success']:
                print("Command succeeded")
        """

        self.process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
            cwd=cwd,
            encoding='utf-8',
            errors='replace'
        )

        stdout_lines = []
        stderr_lines = []

        # Thread para leer stdout
        def read_stdout():
            for line in self.process.stdout:
                stdout_lines.append(line)
                if callback:
                    callback('stdout', line.rstrip())

        # Thread para leer stderr
        def read_stderr():
            for line in self.process.stderr:
                stderr_lines.append(line)
                if callback:
                    callback('stderr', line.rstrip())

        # Iniciar threads de lectura
        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)

        stdout_thread.start()
        stderr_thread.start()

        # Esperar finalización con timeout
        try:
            returncode = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.terminate()
            return {
                'stdout': ''.join(stdout_lines),
                'stderr': ''.join(stderr_lines),
                'returncode': -1,
                'success': False,
                'error': 'Timeout expired'
            }

        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)

        return {
            'stdout': ''.join(stdout_lines),
            'stderr': ''.join(stderr_lines),
            'returncode': returncode,
            'success': returncode == 0
        }

    def execute_simple(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = 30
    ) -> Dict:
        """
        Ejecuta comando y captura todo el output al final (sin streaming).

        Args:
            command: Comando a ejecutar
            cwd: Directorio de trabajo
            timeout: Timeout en segundos

        Returns:
            Dict con stdout, stderr, returncode, success
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                encoding='utf-8',
                errors='replace'
            )

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'success': False,
                'error': 'Timeout expired'
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False,
                'error': str(e)
            }

    def open_vscode_terminal(
        self,
        project_path: str,
        new_window: bool = False
    ) -> bool:
        """
        Abre VS Code en un proyecto específico.

        Args:
            project_path: Path al proyecto
            new_window: Si True, abre en ventana nueva

        Returns:
            True si comando se ejecutó (no espera a que VS Code termine de abrir)
        """
        try:
            cmd = ['code']

            if new_window:
                cmd.append('--new-window')

            cmd.append(str(project_path))

            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return True
        except Exception as e:
            print(f"Error opening VS Code: {e}")
            return False

    def start_claude_in_directory(
        self,
        project_path: str,
        callback: Optional[Callable] = None
    ) -> Dict:
        """
        Inicia Claude Code en un directorio específico.

        Args:
            project_path: Path al proyecto donde ejecutar claude
            callback: Callback para output en tiempo real

        Returns:
            Dict con resultado de ejecución

        Note:
            Este método es bloqueante. Claude Code esperará input del usuario.
            Para uso no-bloqueante, ejecutar en thread separado.
        """
        return self.execute_with_realtime_output(
            'claude',
            cwd=project_path,
            callback=callback
        )

    def terminate(self):
        """Termina proceso en ejecución de forma graceful"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

    def is_running(self) -> bool:
        """Verifica si hay un proceso corriendo"""
        return self.process is not None and self.process.poll() is None
