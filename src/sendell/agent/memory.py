"""
Memory system for Sendell.

Manages:
- Conversation history
- Learned facts about Daniel
- User preferences
- Session memories
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sendell.config import get_settings
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class SendellMemory:
    """
    Sendell's memory system.

    Stores:
    - Conversations: Chat history
    - Facts: Things learned about Daniel
    - Preferences: User settings and preferences
    - Sessions: Historical sessions
    """

    def __init__(self, memory_file: Optional[Path] = None):
        """Initialize memory system"""
        settings = get_settings()

        if memory_file is None:
            # Default memory location
            self.memory_file = Path("data/sendell_memory.json")
        else:
            self.memory_file = memory_file

        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize memory
        self.memory = self._load_memory()

        logger.info(f"Memory system initialized: {self.memory_file}")

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info("Memory loaded from disk")
                    return data
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                return self._create_empty_memory()
        else:
            logger.info("No existing memory, creating new")
            return self._create_empty_memory()

    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create empty memory structure"""
        return {
            "facts": [],  # Things learned about Daniel
            "preferences": {
                "favorite_apps": [],
                "work_hours": None,
                "notification_style": "normal",
            },
            "conversations": [],  # Historical conversations
            "sessions": [],  # Session metadata
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

    def save(self) -> None:
        """Save memory to disk"""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            logger.debug("Memory saved to disk")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    # ==================== FACTS ====================

    def add_fact(self, fact: str, category: str = "general") -> None:
        """
        Add a learned fact about Daniel.

        Args:
            fact: The fact to remember
            category: Category (general, preference, work, personal)
        """
        fact_entry = {
            "fact": fact,
            "category": category,
            "learned_at": datetime.now().isoformat(),
        }

        self.memory["facts"].append(fact_entry)
        self.save()
        logger.info(f"Added fact: {fact}")

    def get_facts(self, category: Optional[str] = None) -> List[Dict]:
        """Get all facts, optionally filtered by category"""
        facts = self.memory["facts"]

        if category:
            facts = [f for f in facts if f.get("category") == category]

        return facts

    def remove_fact(self, index: int) -> bool:
        """Remove a fact by index"""
        try:
            removed = self.memory["facts"].pop(index)
            self.save()
            logger.info(f"Removed fact: {removed['fact']}")
            return True
        except IndexError:
            logger.error(f"Invalid fact index: {index}")
            return False

    def clear_facts(self) -> None:
        """Clear all facts"""
        count = len(self.memory["facts"])
        self.memory["facts"] = []
        self.save()
        logger.info(f"Cleared {count} facts")

    # ==================== PREFERENCES ====================

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference"""
        self.memory["preferences"][key] = value
        self.save()
        logger.info(f"Set preference: {key} = {value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        return self.memory["preferences"].get(key, default)

    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences"""
        return self.memory["preferences"]

    # ==================== CONVERSATIONS ====================

    def add_conversation(self, messages: List[Dict], summary: str = "") -> None:
        """
        Save a conversation.

        Args:
            messages: List of conversation messages
            summary: Optional summary of the conversation
        """
        conv_entry = {
            "messages": messages,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages),
        }

        self.memory["conversations"].append(conv_entry)

        # Keep only last 50 conversations
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]

        self.save()

    def get_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        return self.memory["conversations"][-limit:]

    def clear_conversations(self) -> None:
        """Clear all conversation history"""
        count = len(self.memory["conversations"])
        self.memory["conversations"] = []
        self.save()
        logger.info(f"Cleared {count} conversations")

    # ==================== SESSIONS ====================

    def start_session(self) -> str:
        """Start a new session and return session ID"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        session_entry = {
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "interactions": 0,
        }

        self.memory["sessions"].append(session_entry)
        self.save()

        logger.info(f"Started session: {session_id}")
        return session_id

    def end_session(self, session_id: str, interactions: int) -> None:
        """End a session"""
        for session in reversed(self.memory["sessions"]):
            if session["session_id"] == session_id:
                session["ended_at"] = datetime.now().isoformat()
                session["interactions"] = interactions
                self.save()
                logger.info(f"Ended session: {session_id}")
                break

    def get_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent sessions"""
        return self.memory["sessions"][-limit:]

    # ==================== UTILITY ====================

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory contents"""
        return {
            "total_facts": len(self.memory["facts"]),
            "total_conversations": len(self.memory["conversations"]),
            "total_sessions": len(self.memory["sessions"]),
            "preferences_count": len(self.memory["preferences"]),
            "created_at": self.memory["created_at"],
            "last_updated": self.memory["last_updated"],
            "memory_file": str(self.memory_file),
        }

    def export_memory(self, export_path: Path) -> None:
        """Export memory to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            logger.info(f"Memory exported to: {export_path}")
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")

    def import_memory(self, import_path: Path) -> bool:
        """Import memory from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
            self.save()
            logger.info(f"Memory imported from: {import_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import memory: {e}")
            return False


# Global memory instance
_memory: Optional[SendellMemory] = None


def get_memory() -> SendellMemory:
    """Get or create global memory instance"""
    global _memory
    if _memory is None:
        _memory = SendellMemory()
    return _memory
