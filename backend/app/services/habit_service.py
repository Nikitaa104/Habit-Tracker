from datetime import date
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Habit, Completion


class DuplicateCompletionError(Exception):
    """Raised when a habit is already logged for the given date."""


class HabitNotFoundError(Exception):
    """Raised when a habit does not exist (or is archived and inaccessible)."""


class HabitService:

    # ── Habits ────────────────────────────────────────────────────

    @staticmethod
    def list_habits(include_archived: bool = False) -> list[Habit]:
        query = Habit.query
        if not include_archived:
            query = query.filter_by(archived=False)
        return query.order_by(Habit.created_at.desc()).all()

    @staticmethod
    def get_habit(habit_id: int) -> Habit:
        habit = db.session.get(Habit, habit_id)
        if habit is None:
            raise HabitNotFoundError(f"Habit {habit_id} not found.")
        return habit

    @staticmethod
    def create_habit(name: str, description: Optional[str], frequency: str, color: str) -> Habit:
        habit = Habit(name=name, description=description, frequency=frequency, color=color)
        db.session.add(habit)
        db.session.commit()
        return habit

    @staticmethod
    def update_habit(habit_id: int, **fields) -> Habit:
        habit = HabitService.get_habit(habit_id)
        allowed = {"name", "description", "frequency", "color", "archived"}
        for key, value in fields.items():
            if key in allowed and value is not None:
                setattr(habit, key, value)
        db.session.commit()
        return habit

    @staticmethod
    def delete_habit(habit_id: int) -> None:
        habit = HabitService.get_habit(habit_id)
        db.session.delete(habit)
        db.session.commit()

    # ── Completions ───────────────────────────────────────────────

    @staticmethod
    def log_completion(habit_id: int, completed_on: Optional[date], note: Optional[str]) -> Completion:
        habit = HabitService.get_habit(habit_id)
        target_date = completed_on or date.today()

        completion = Completion(habit_id=habit.id, completed_on=target_date, note=note)
        db.session.add(completion)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise DuplicateCompletionError(
                f"Habit {habit_id} is already logged for {target_date}."
            )
        return completion

    @staticmethod
    def undo_completion(habit_id: int, target_date: date) -> None:
        """Remove a completion for a given date (idempotent — no error if absent)."""
        HabitService.get_habit(habit_id)
        Completion.query.filter_by(habit_id=habit_id, completed_on=target_date).delete()
        db.session.commit()

    @staticmethod
    def list_completions(habit_id: int) -> list[Completion]:
        HabitService.get_habit(habit_id)
        return (
            Completion.query
            .filter_by(habit_id=habit_id)
            .order_by(Completion.completed_on.desc())
            .all()
        )
