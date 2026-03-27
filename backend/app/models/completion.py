from datetime import date
from app import db


class Completion(db.Model):
    __tablename__ = "completions"
    __table_args__ = (
        db.UniqueConstraint("habit_id", "completed_on", name="uq_habit_day"),
    )

    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(
        db.Integer, db.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )
    completed_on = db.Column(db.Date, nullable=False, default=date.today)
    note = db.Column(db.String(300), nullable=True)
    logged_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    habit = db.relationship("Habit", back_populates="completions")

    def __repr__(self) -> str:
        return f"<Completion habit_id={self.habit_id} date={self.completed_on}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "completed_on": self.completed_on.isoformat(),
            "note": self.note,
            "logged_at": self.logged_at.isoformat(),
        }
