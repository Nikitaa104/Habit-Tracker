from datetime import date, timedelta
from app import db


class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    frequency = db.Column(
        db.Enum("daily", "weekly", name="frequency_enum"),
        nullable=False,
        default="daily",
    )
    color = db.Column(db.String(7), nullable=False, default="#6366f1")
    archived = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    completions = db.relationship(
        "Completion", back_populates="habit", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name={self.name!r}>"

    # ── Domain logic ──────────────────────────────────────────────

    def is_completed_on(self, target_date: date) -> bool:
        """Return True if the habit was completed on target_date."""
        return any(c.completed_on == target_date for c in self.completions)

    def current_streak(self) -> int:
        """
        Count consecutive days (ending today or yesterday) on which
        the habit was completed.  Weekly habits are not streak-tracked.
        """
        if self.frequency != "daily":
            return 0

        completed_days = {c.completed_on for c in self.completions}
        streak = 0
        cursor = date.today()

        # Allow the streak to still count if today hasn't been logged yet
        if cursor not in completed_days:
            cursor -= timedelta(days=1)

        while cursor in completed_days:
            streak += 1
            cursor -= timedelta(days=1)

        return streak

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "color": self.color,
            "archived": self.archived,
            "created_at": self.created_at.isoformat(),
            "streak": self.current_streak(),
            "completed_today": self.is_completed_on(date.today()),
        }
