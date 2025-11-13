"""
Sendell CLI - Main Entry Point

Commands:
- sendell start: Run proactive monitoring loop
- sendell chat: Interactive chat mode
- sendell health: Quick system health check
"""

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sendell.agent.core import get_agent
from sendell.config import get_settings, validate_settings
from sendell.device.monitor import SystemMonitor
from sendell.utils.logger import get_logger

# Initialize CLI
app = typer.Typer(
    name="sendell",
    help="Sendell - Autonomous AI Agent for System Monitoring and Control",
    add_completion=False,
)

console = Console()
logger = get_logger(__name__)


def show_banner():
    """Show Sendell banner"""
    banner = """
========================================
      SENDELL - AI Agent v0.2
  Autonomous & Proactive AI Assistant
========================================
"""
    console.print(banner, style="bold cyan")


@app.command()
def start(
    interval: int = typer.Option(None, "--interval", "-i", help="Loop interval in seconds"),
    max_cycles: Optional[int] = typer.Option(
        None, "--max-cycles", "-n", help="Max cycles to run (for testing)"
    ),
):
    """
    Start proactive monitoring loop (OODA).

    Sendell will monitor your system every N seconds and alert you to issues.
    """
    show_banner()

    try:
        # Validate configuration
        validate_settings()
        settings = get_settings()

        # Use provided interval or default from config
        loop_interval = interval if interval else settings.agent.loop_interval

        console.print(
            f"\n[bold green]Starting proactive monitoring...[/bold green]\n"
            f"Autonomy Level: [cyan]{settings.agent.autonomy_level.name}[/cyan]\n"
            f"Loop Interval: [cyan]{loop_interval}s[/cyan]\n"
            f"Press [bold red]Ctrl+C[/bold red] to stop\n"
        )

        # Run proactive loop
        asyncio.run(run_proactive_loop(loop_interval, max_cycles))

    except KeyboardInterrupt:
        console.print("\n[yellow]Sendell shutting down gracefully...[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start Sendell: {e}")
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


async def run_proactive_loop(interval: int, max_cycles: Optional[int] = None):
    """
    Run the proactive monitoring loop.

    Args:
        interval: Sleep interval between cycles in seconds
        max_cycles: Maximum number of cycles (None for infinite)
    """
    agent = get_agent()
    cycle_count = 0

    console.print("[dim]Proactive loop started. Monitoring system...[/dim]\n")

    try:
        while True:
            cycle_count += 1

            # Show cycle info
            console.print(f"[dim]--- Cycle {cycle_count} ---[/dim]")

            # Run proactive cycle
            result = await agent.run_proactive_cycle()

            if result["success"]:
                logger.debug(f"Cycle {cycle_count} completed successfully")
            else:
                logger.error(f"Cycle {cycle_count} failed: {result.get('error')}")
                console.print(f"[red]Cycle failed: {result.get('error')}[/red]")

            # Check if we've hit max cycles
            if max_cycles and cycle_count >= max_cycles:
                console.print(f"\n[yellow]Reached max cycles ({max_cycles}). Stopping.[/yellow]")
                break

            # Sleep until next cycle
            console.print(f"[dim]Sleeping for {interval}s...\n[/dim]")
            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        raise


@app.command()
def chat():
    """
    Start interactive chat mode.

    Chat with Sendell to ask questions and request actions.
    """
    show_banner()

    try:
        # Validate configuration
        validate_settings()

        console.print(
            "\n[bold green]Interactive chat mode started![/bold green]\n"
            "Type your messages below. Commands:\n"
            "  [cyan]/quit[/cyan] or [cyan]/exit[/cyan] - Exit chat\n"
            "  [cyan]/health[/cyan] - Quick system health check\n"
            "  [cyan]/help[/cyan] - Show available commands\n"
        )

        # Run chat loop
        asyncio.run(run_chat_loop())

    except KeyboardInterrupt:
        console.print("\n[yellow]Chat ended.[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Chat mode failed: {e}")
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def start_dashboard_server():
    """Start dashboard server in background if not already running."""
    import socket
    import subprocess
    import os
    import time

    def is_server_running():
        """Check if server is running on port 8765"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', 8765))
                return result == 0
        except:
            return False

    if is_server_running():
        logger.info("Dashboard server already running on port 8765")
        console.print("[dim]📊 Dashboard server running on http://localhost:8765[/dim]")
        return

    logger.info("Starting dashboard server on port 8765...")
    console.print("[dim]🚀 Starting dashboard server...[/dim]")

    project_root = os.path.dirname(os.path.dirname(__file__))

    try:
        if os.name == 'nt':  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            subprocess.Popen(
                ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                cwd=project_root,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  # Linux/Mac
            subprocess.Popen(
                ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Wait for server to start (dashboard takes ~4-5 seconds to initialize)
        time.sleep(6)

        if is_server_running():
            logger.info("Dashboard server started successfully")
            console.print("[green]✅ Dashboard server started on http://localhost:8765[/green]")
        else:
            logger.warning("Dashboard server may not have started correctly")
            console.print("[yellow]⚠️  Dashboard server may not have started correctly[/yellow]")

    except Exception as e:
        logger.error(f"Failed to start dashboard server: {e}")
        console.print(f"[yellow]⚠️  Failed to start dashboard server: {e}[/yellow]")


async def run_chat_loop():
    """Run interactive chat loop"""
    # Dashboard server is started on-demand via open_dashboard() tool
    # No need to auto-start it here

    agent = get_agent()
    conversation_history = []

    # Start proactive loop in background
    await agent.proactive_loop.start()
    console.print("[dim]⏰ Proactive reminders active (checking every 60s)[/dim]\n")

    try:
        while True:
            try:
                # Get user input (non-blocking using asyncio.to_thread)
                user_input = await asyncio.to_thread(
                    console.input, "\n[bold cyan]You:[/bold cyan] "
                )
                user_input = user_input.strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["/quit", "/exit", "/q"]:
                    console.print("[yellow]Stopping services...[/yellow]")
                    await agent.proactive_loop.stop()

                    # Kill dashboard server if running
                    from sendell.web.server_tracker import kill_server
                    kill_server()

                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == "/health":
                    # Quick health check
                    monitor = SystemMonitor()
                    health = monitor.get_system_health()
                    display_health(health)
                    continue

                if user_input.lower() == "/help":
                    console.print(
                        "\n[bold]Available Commands:[/bold]\n"
                        "  /quit, /exit - Exit chat\n"
                        "  /health - Quick system health check\n"
                        "  /help - Show this help\n\n"
                        "[bold]You can also ask:[/bold]\n"
                        "  'How's my system?'\n"
                        "  'What's using all my RAM?'\n"
                        "  'Open notepad'\n"
                        "  'Show me top processes'\n"
                    )
                    continue

                # Send to agent
                console.print("[dim]Thinking...[/dim]")
                result = await agent.chat(user_input, conversation_history)

                if result["success"]:
                    # Update conversation history
                    conversation_history = result.get("conversation_history", [])

                    # Display response
                    response = result.get("response", "No response")
                    console.print(f"\n[bold green]Sendell:[/bold green] {response}")
                else:
                    console.print(f"[red]Error: {result.get('error')}[/red]")

            except KeyboardInterrupt:
                # User pressed Ctrl+C - break out of loop
                break
            except Exception as e:
                logger.error(f"Chat error: {e}")
                console.print(f"[red]Error: {e}[/red]")

    finally:
        # Always cleanup dashboard server on exit (Ctrl+C or /quit)
        console.print("\n[yellow]Cleaning up dashboard server...[/yellow]")
        from sendell.web.server_tracker import kill_server
        kill_server()
        console.print("[green]✅ Cleanup complete[/green]")
        console.print("[yellow]Goodbye![/yellow]")


@app.command()
def health():
    """
    Quick system health check (no agent, direct monitoring).
    """
    try:
        console.print("\n[bold]Checking system health...[/bold]\n")

        monitor = SystemMonitor()
        health = monitor.get_system_health()

        display_health(health)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def display_health(health):
    """Display system health in a nice table"""
    table = Table(title="System Health", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    # CPU
    cpu_status = "[!] High" if health.cpu_percent > 80 else "[OK]"
    table.add_row("CPU Usage", f"{health.cpu_percent}%", cpu_status)

    # RAM
    ram_status = "[!] High" if health.ram_percent > 85 else "[OK]"
    table.add_row(
        "RAM Usage", f"{health.ram_percent}% ({health.ram_used_gb:.1f}GB / {health.ram_total_gb:.1f}GB)", ram_status
    )

    # Disk
    disk_status = "[!] High" if health.disk_percent > 90 else "[OK]"
    table.add_row(
        "Disk Usage",
        f"{health.disk_percent}% ({health.disk_used_gb:.1f}GB / {health.disk_total_gb:.1f}GB)",
        disk_status,
    )

    console.print(table)


@app.command()
def brain():
    """
    Open Sendell Dashboard (web interface) to manage projects and terminals.

    Opens the Angular web dashboard at http://localhost:8765
    Replaces the old tkinter/Qt GUI with a modern web interface.
    """
    try:
        console.print("\n[bold green]Opening Sendell Dashboard...[/bold green]")
        console.print("[dim]Web interface at http://localhost:8765[/dim]\n")

        import webbrowser
        import socket
        import subprocess
        import os
        import time

        def is_server_running():
            """Check if server is running on port 8765"""
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', 8765))
                    return result == 0
            except:
                return False

        dashboard_url = "http://localhost:8765"

        # Check if server is running
        if not is_server_running():
            console.print("[yellow]Starting dashboard server...[/yellow]")

            # Start server in background
            project_root = os.path.dirname(os.path.dirname(__file__))

            # Use CREATE_NO_WINDOW flag to hide cmd window
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                subprocess.Popen(
                    ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                    cwd=project_root,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                    cwd=project_root,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Wait for server to start (with retry logic)
            console.print("[dim]Waiting for server to initialize...[/dim]")
            max_retries = 15  # 15 seconds total
            for i in range(max_retries):
                time.sleep(1)
                if is_server_running():
                    break
                if i % 3 == 0:  # Show progress every 3 seconds
                    console.print(f"[dim]Still waiting... ({i+1}s)[/dim]")

            # Final verify
            if not is_server_running():
                console.print("[bold red]Error:[/bold red] Server failed to start within 15 seconds")
                console.print("Please start manually: [cyan]uv run uvicorn sendell.web.server:app --port 8765[/cyan]")
                sys.exit(1)

            console.print("[green]✓ Server started successfully[/green]\n")

        # Open browser
        webbrowser.open(dashboard_url)
        console.print(f"[bold green]✓ Dashboard opened at {dashboard_url}[/bold green]")

    except Exception as e:
        logger.error(f"Failed to open dashboard: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def status():
    """
    Show proactive system status.

    Displays agent identity, relationship phase, proactive loop status,
    and upcoming reminders.
    """
    try:
        console.print("\n[bold]Proactive System Status[/bold]\n")

        agent = get_agent()
        status_data = agent.get_proactive_status()

        # Agent Identity
        identity = status_data["identity"]
        console.print(f"[bold cyan]Agent Identity[/bold cyan]")
        console.print(f"  Age: {identity['age_days']} days")
        console.print(f"  Phase: {identity['phase']}")
        console.print(f"  Confidence: {identity['confidence']:.2f}")

        # Proactive Loop
        loop = status_data["loop"]
        console.print(f"\n[bold cyan]Proactive Loop[/bold cyan]")
        console.print(f"  Running: {'Yes' if loop['running'] else 'No'}")
        console.print(f"  Check interval: {loop['check_interval_seconds']}s")
        console.print(f"  Cycles run: {loop['cycles_run']}")
        console.print(f"  Reminders triggered: {loop['reminders_triggered']}")
        if loop['last_check_at']:
            console.print(f"  Last check: {loop['last_check_at']}")

        # Reminders
        reminders = status_data["reminders"]
        console.print(f"\n[bold cyan]Reminders[/bold cyan]")
        console.print(f"  Total: {reminders['total']}")
        console.print(f"  Due now: {reminders['due']}")
        console.print(f"  Upcoming (24h): {reminders['upcoming_24h']}")

        # Show upcoming reminders
        upcoming = agent.reminder_manager.get_upcoming_reminders(hours=24)
        if upcoming:
            console.print(f"\n[bold cyan]Upcoming Reminders (next 24h)[/bold cyan]")
            for r in upcoming:
                due_time = r.due_at.strftime("%I:%M %p")
                console.print(f"  - {r.content} at {due_time} ({', '.join(r.actions)})")
        else:
            console.print(f"\n[dim]No upcoming reminders in the next 24 hours[/dim]")

        console.print()

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def version():
    """Show Sendell version"""
    console.print("\n[bold cyan]Sendell v0.2.0[/bold cyan] - Proactive System")
    console.print("Autonomous & Proactive AI Assistant\n")


@app.callback()
def main():
    """
    Sendell - Autonomous AI Agent

    Monitor your system, manage processes, and automate tasks.
    """
    pass


if __name__ == "__main__":
    app()
