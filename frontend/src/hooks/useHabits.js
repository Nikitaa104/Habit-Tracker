import { useState, useEffect, useCallback } from "react";
import {
  listHabits,
  createHabit,
  updateHabit,
  deleteHabit,
  logCompletion,
  undoCompletion,
} from "../api";

export function useHabits() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listHabits();
      setHabits(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addHabit = async (payload) => {
    const habit = await createHabit(payload);
    setHabits((prev) => [habit, ...prev]);
    return habit;
  };

  const editHabit = async (id, payload) => {
    const updated = await updateHabit(id, payload);
    setHabits((prev) => prev.map((h) => (h.id === id ? updated : h)));
    return updated;
  };

  const removeHabit = async (id) => {
    await deleteHabit(id);
    setHabits((prev) => prev.filter((h) => h.id !== id));
  };

  const toggleCompletion = async (habit) => {
    const today = new Date().toISOString().split("T")[0];
    try {
      if (habit.completed_today) {
        await undoCompletion(habit.id, today);
        setHabits((prev) =>
          prev.map((h) =>
            h.id === habit.id
              ? { ...h, completed_today: false, streak: Math.max(0, h.streak - 1) }
              : h
          )
        );
      } else {
        const completion = await logCompletion(habit.id, {});
        setHabits((prev) =>
          prev.map((h) =>
            h.id === habit.id
              ? { ...h, completed_today: true, streak: h.streak + 1 }
              : h
          )
        );
        return completion;
      }
    } catch (err) {
      // Bubble up for the UI to handle
      throw err;
    }
  };

  return { habits, loading, error, refresh, addHabit, editHabit, removeHabit, toggleCompletion };
}
