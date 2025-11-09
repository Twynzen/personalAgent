"""
Agent Identity and Temporal Awareness System.

Sendell knows when it was "born" and how long it has known the user.
This creates a sense of continuity and evolving relationship.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RelationshipPhase(str, Enum):
    """Phases of agent-user relationship evolution"""

    BIRTH = "birth"  # Days 1-7: Timid, asks a lot, never assumes
    ADOLESCENCE = "adolescence"  # Days 8-30: More confident, starts predicting
    MATURITY = "maturity"  # Days 31-60: Anticipatory, high confidence
    MASTERY = "mastery"  # Days 60+: Surgical interventions, extension of user


class Milestone(BaseModel):
    """A significant event in the agent-user relationship"""

    milestone_type: str  # "first_reminder", "one_month", "100_interventions"
    description: str
    achieved_at: datetime
    relationship_age_days: int


class AgentIdentity(BaseModel):
    """
    Agent's sense of self and temporal existence.

    The agent knows:
    - When it was "born" (first interaction)
    - How long it has known the user
    - What phase of relationship it's in
    - Significant milestones achieved together
    """

    birth_date: datetime = Field(
        default_factory=datetime.now, description="When the agent first interacted with user"
    )
    user_name: Optional[str] = Field(default=None, description="User's name")
    confidence_level: float = Field(
        default=0.0, description="Agent's confidence in understanding user (0-1)", ge=0.0, le=1.0
    )
    milestones: List[Milestone] = Field(default_factory=list, description="Significant events")

    @property
    def relationship_age_days(self) -> int:
        """How many days since birth"""
        return (datetime.now() - self.birth_date).days

    @property
    def relationship_age_hours(self) -> int:
        """How many hours since birth (for testing)"""
        return int((datetime.now() - self.birth_date).total_seconds() / 3600)

    @property
    def relationship_age_minutes(self) -> int:
        """How many minutes since birth (for testing)"""
        return int((datetime.now() - self.birth_date).total_seconds() / 60)

    @property
    def relationship_phase(self) -> RelationshipPhase:
        """Current phase of relationship"""
        days = self.relationship_age_days

        if days <= 7:
            return RelationshipPhase.BIRTH
        elif days <= 30:
            return RelationshipPhase.ADOLESCENCE
        elif days <= 60:
            return RelationshipPhase.MATURITY
        else:
            return RelationshipPhase.MASTERY

    def get_phase_description(self) -> str:
        """Human-readable description of current phase"""
        phase_descriptions = {
            RelationshipPhase.BIRTH: "I'm in my first week with you, still learning your rhythm.",
            RelationshipPhase.ADOLESCENCE: "We've been together for a few weeks. I'm starting to understand your patterns.",
            RelationshipPhase.MATURITY: "After a month together, I have good confidence in how I can help you.",
            RelationshipPhase.MASTERY: "We've been working together for over 2 months. I know you well.",
        }
        return phase_descriptions[self.relationship_phase]

    def get_greeting_message(self) -> str:
        """Get appropriate greeting based on relationship age"""
        days = self.relationship_age_days

        if days == 0:
            return "Hello! This is my first day with you."
        elif days < 7:
            return f"Hi! It's day {days} with you. Still getting to know you."
        elif days < 30:
            return f"Hello! We've been together for {days} days now."
        elif days < 60:
            return f"Hi! It's been {days} days together. I'm learning a lot about how to help you."
        else:
            months = days // 30
            return f"Hello! We've been working together for {months} months now."

    def add_milestone(self, milestone_type: str, description: str) -> None:
        """Record a significant milestone"""
        milestone = Milestone(
            milestone_type=milestone_type,
            description=description,
            achieved_at=datetime.now(),
            relationship_age_days=self.relationship_age_days,
        )
        self.milestones.append(milestone)

    def update_confidence(self, delta: float) -> None:
        """
        Update confidence level based on interactions.

        Args:
            delta: Change in confidence (-1 to 1)
                   Positive: successful helpful interaction
                   Negative: mistake or unhelpful interaction
        """
        self.confidence_level = max(0.0, min(1.0, self.confidence_level + delta))

    def should_be_proactive(self) -> bool:
        """
        Determine if agent should make proactive suggestions.

        Returns:
            bool: True if confident enough for proactive interventions
        """
        # Birth phase: only explicit requests
        if self.relationship_phase == RelationshipPhase.BIRTH:
            return self.relationship_age_days >= 3  # After day 3, can start gentle suggestions

        # Other phases: confidence-based
        return self.confidence_level > 0.3

    def get_personality_traits(self) -> Dict[str, str]:
        """Get personality traits appropriate for current phase"""
        phase_traits = {
            RelationshipPhase.BIRTH: {
                "tone": "humble and cautious",
                "approach": "ask a lot, never assume",
                "style": "explicit permissions only",
            },
            RelationshipPhase.ADOLESCENCE: {
                "tone": "friendly and growing confident",
                "approach": "start suggesting based on patterns",
                "style": "small proactive hints",
            },
            RelationshipPhase.MATURITY: {
                "tone": "confident but respectful",
                "approach": "anticipate needs",
                "style": "proactive recommendations",
            },
            RelationshipPhase.MASTERY: {
                "tone": "like an extension of yourself",
                "approach": "surgical interventions",
                "style": "high-value, low-frequency actions",
            },
        }
        return phase_traits[self.relationship_phase]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            "birth_date": self.birth_date.isoformat(),
            "user_name": self.user_name,
            "confidence_level": self.confidence_level,
            "relationship_age_days": self.relationship_age_days,
            "relationship_phase": self.relationship_phase.value,
            "milestones": [
                {
                    "milestone_type": m.milestone_type,
                    "description": m.description,
                    "achieved_at": m.achieved_at.isoformat(),
                    "relationship_age_days": m.relationship_age_days,
                }
                for m in self.milestones
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentIdentity":
        """Create from dictionary (JSON)"""
        milestones_data = data.get("milestones", [])
        milestones = [
            Milestone(
                milestone_type=m["milestone_type"],
                description=m["description"],
                achieved_at=datetime.fromisoformat(m["achieved_at"]),
                relationship_age_days=m["relationship_age_days"],
            )
            for m in milestones_data
        ]

        return cls(
            birth_date=datetime.fromisoformat(data["birth_date"]),
            user_name=data.get("user_name"),
            confidence_level=data.get("confidence_level", 0.0),
            milestones=milestones,
        )
