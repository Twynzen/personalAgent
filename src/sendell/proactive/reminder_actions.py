"""
Reminder Actions - Executable actions for reminders.

Actions:
- chat_message: Send message in chat
- popup: Windows notification/toast
- notepad: Open notepad with message
- sound: Play notification sound
"""

import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ActionType(str, Enum):
    """Types of reminder actions"""

    CHAT_MESSAGE = "chat_message"  # Send message in chat
    POPUP = "popup"  # Windows notification
    NOTEPAD = "notepad"  # Open notepad with message
    SOUND = "sound"  # Play notification sound


class ReminderAction(BaseModel):
    """Configuration for a reminder action"""

    action_type: ActionType
    parameters: Dict = {}


def send_chat_message(content: str) -> Dict:
    """
    Send reminder as chat message.

    This will be picked up by the chat interface.

    Args:
        content: Message content

    Returns:
        dict: Result of action
    """
    logger.info(f"Reminder chat message: {content}")

    # This returns the message to be displayed in chat
    return {"success": True, "action": "chat_message", "message": content}


def show_windows_popup(title: str, content: str) -> Dict:
    """
    Show Windows notification/toast.

    Uses Windows 10/11 native notification system.

    Args:
        title: Notification title
        content: Notification content

    Returns:
        dict: Result of action
    """
    try:
        # Use PowerShell to show Windows toast notification
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
        <toast>
            <visual>
                <binding template="ToastText02">
                    <text id="1">{title}</text>
                    <text id="2">{content}</text>
                </binding>
            </visual>
        </toast>
        "@

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Sendell")
        $notifier.Show($toast)
        """

        subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            shell=False,
            timeout=5,
        )

        logger.info(f"Windows popup shown: {title} - {content}")
        return {"success": True, "action": "popup", "title": title, "message": content}

    except Exception as e:
        logger.error(f"Failed to show Windows popup: {e}")
        # Fallback: use simple message box
        try:
            subprocess.run(
                ["msg", "*", f"{title}\n\n{content}"], shell=False, timeout=5, check=False
            )
            return {"success": True, "action": "popup_fallback", "message": content}
        except:
            return {"success": False, "action": "popup", "error": str(e)}


def open_notepad_with_message(content: str) -> Dict:
    """
    Open notepad with reminder message.

    Creates a temporary file with the reminder and opens it in notepad.

    Args:
        content: Message to display in notepad

    Returns:
        dict: Result of action
    """
    try:
        # Create temp file with reminder
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", prefix="sendell_reminder_"
        ) as f:
            # Write formatted reminder
            f.write("=" * 60 + "\n")
            f.write("SENDELL REMINDER\n")
            f.write("=" * 60 + "\n\n")
            f.write(content + "\n\n")
            f.write("=" * 60 + "\n")
            temp_path = f.name

        # Open in notepad
        subprocess.Popen(["notepad.exe", temp_path], shell=False)

        logger.info(f"Notepad opened with reminder: {content}")
        return {
            "success": True,
            "action": "notepad",
            "message": content,
            "temp_file": temp_path,
        }

    except Exception as e:
        logger.error(f"Failed to open notepad: {e}")
        return {"success": False, "action": "notepad", "error": str(e)}


def play_notification_sound() -> Dict:
    """
    Play a notification sound.

    Uses Windows default notification sound.

    Returns:
        dict: Result of action
    """
    try:
        # Play Windows default notification sound
        import winsound

        winsound.MessageBeep(winsound.MB_ICONASTERISK)

        logger.info("Notification sound played")
        return {"success": True, "action": "sound"}

    except Exception as e:
        logger.error(f"Failed to play sound: {e}")
        return {"success": False, "action": "sound", "error": str(e)}


async def execute_reminder_action(action_type: str, content: str, title: str = "Reminder") -> Dict:
    """
    Execute a reminder action.

    Args:
        action_type: Type of action (chat_message, popup, notepad, sound)
        content: Reminder content
        title: Title for popup (optional)

    Returns:
        dict: Result of execution
    """
    try:
        action = ActionType(action_type)
    except ValueError:
        logger.error(f"Unknown action type: {action_type}")
        return {"success": False, "error": f"Unknown action type: {action_type}"}

    try:
        if action == ActionType.CHAT_MESSAGE:
            return send_chat_message(content)

        elif action == ActionType.POPUP:
            return show_windows_popup(title, content)

        elif action == ActionType.NOTEPAD:
            return open_notepad_with_message(content)

        elif action == ActionType.SOUND:
            return play_notification_sound()

        else:
            return {"success": False, "error": f"Action not implemented: {action}"}

    except Exception as e:
        logger.error(f"Error executing action {action}: {e}")
        return {"success": False, "error": str(e)}


async def execute_reminder_actions(actions: List[str], content: str, title: str = "Reminder") -> List[Dict]:
    """
    Execute multiple reminder actions.

    Args:
        actions: List of action types
        content: Reminder content
        title: Title for popup

    Returns:
        list: Results of each action execution
    """
    results = []

    for action_type in actions:
        result = await execute_reminder_action(action_type, content, title)
        results.append(result)

    return results
