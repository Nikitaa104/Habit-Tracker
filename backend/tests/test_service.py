from datetime import date, timedelta
import pytest

from app import db
from app.models import Habit, Completion
from app.services.habit_service import HabitService, DuplicateCompletionError, HabitNotFoundError


def _create_habit(name="Test", frequency="daily"):
    habit = Habit(name=name, frequency=frequency, color="#6366f1")
    db.session.add(habit)
    db.session.commit()
    return habit


def _complete_on(habit, target_date):
    c = Completion(habit_id=habit.id, completed_on=target_date)
    db.session.add(c)
    db.session.commit()


# ── Streak logic ──────────────────────────────────────────────────


def test_streak_zero_when_no_completions(app):
    with app.app_context():
        habit = _create_habit()
        assert habit.current_streak() == 0


def test_streak_one_today(app):
    with app.app_context():
        habit = _create_habit()
        _complete_on(habit, date.today())
        assert habit.current_streak() == 1


def test_streak_counts_consecutive_days(app):
    with app.app_context():
        habit = _create_habit()
        for i in range(3):
            _complete_on(habit, date.today() - timedelta(days=i))
        assert habit.current_streak() == 3


def test_streak_breaks_on_gap(app):
    with app.app_context():
        habit = _create_habit()
        _complete_on(habit, date.today())
        # Skip yesterday — gap
        _complete_on(habit, date.today() - timedelta(days=2))
        assert habit.current_streak() == 1


def test_streak_still_counts_if_today_not_logged(app):
    with app.app_context():
        habit = _create_habit()
        _complete_on(habit, date.today() - timedelta(days=1))
        _complete_on(habit, date.today() - timedelta(days=2))
        assert habit.current_streak() == 2


def test_streak_zero_for_weekly_habits(app):
    with app.app_context():
        habit = _create_habit(frequency="weekly")
        _complete_on(habit, date.today())
        assert habit.current_streak() == 0


# ── is_completed_on ───────────────────────────────────────────────


def test_is_completed_on_true(app):
    with app.app_context():
        habit = _create_habit()
        _complete_on(habit, date.today())
        assert habit.is_completed_on(date.today()) is True


def test_is_completed_on_false(app):
    with app.app_context():
        habit = _create_habit()
        assert habit.is_completed_on(date.today()) is False


# ── Service error paths ───────────────────────────────────────────


def test_get_habit_not_found_raises(app):
    with app.app_context():
        with pytest.raises(HabitNotFoundError):
            HabitService.get_habit(99999)


def test_duplicate_completion_raises(app):
    with app.app_context():
        habit = _create_habit()
        HabitService.log_completion(habit.id, date.today(), None)
        with pytest.raises(DuplicateCompletionError):
            HabitService.log_completion(habit.id, date.today(), None)


def test_delete_cascades_completions(app):
    with app.app_context():
        habit = _create_habit()
        _complete_on(habit, date.today())
        habit_id = habit.id
        HabitService.delete_habit(habit_id)
        remaining = Completion.query.filter_by(habit_id=habit_id).count()
        assert remaining == 0
