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


async def run_chat_loop():
    """Run interactive chat loop"""
    agent = get_agent()
    conversation_history = []

    # Start proactive loop in background
    await agent.proactive_loop.start()
    console.print("[dim]⏰ Proactive reminders active (checking every 60s)[/dim]\n")

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
            raise
        except Exception as e:
            logger.error(f"Chat error: {e}")
            console.print(f"[red]Error: {e}[/red]")


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
    Open Sendell Brain GUI to manage memory, prompts, and tools.
    """
    try:
        console.print("\n[bold green]Opening Sendell Brain...[/bold green]\n")

        from sendell.agent.brain_gui import show_brain
        from sendell.agent.core import get_agent

        # Get agent to pass tools
        try:
            agent = get_agent()
            tools = agent.tools
        except:
            tools = []

        # Show GUI
        show_brain(tools=tools)

    except Exception as e:
        logger.error(f"Failed to open brain: {e}")
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
