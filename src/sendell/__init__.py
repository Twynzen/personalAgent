"""
Sendell - Autonomous AI Agent for System Monitoring and Control

A proactive AI agent that monitors your system, detects issues,
and helps manage your device using LangGraph + MCP + psutil.
"""

__version__ = "0.1.0"
__author__ = "Daniel"
__description__ = "Autonomous AI Agent for System Monitoring and Control"

from sendell.agent.core import SendellAgent, get_agent
from sendell.config import get_settings, validate_settings
from sendell.device.automation import AppController
from sendell.device.monitor import SystemMonitor

__all__ = [
    "SendellAgent",
    "get_agent",
    "SystemMonitor",
    "AppController",
    "get_settings",
    "validate_settings",
]
