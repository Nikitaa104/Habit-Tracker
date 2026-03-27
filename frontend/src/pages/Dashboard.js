import React, { useState } from "react";
import { useHabits } from "../hooks/useHabits";
import HabitCard from "../components/HabitCard";
import HabitModal from "../components/HabitModal";
import StatsBar from "../components/StatsBar";

export default function Dashboard() {
  const { habits, loading, error, addHabit, editHabit, removeHabit, toggleCompletion } = useHabits();
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [toast, setToast] = useState(null);
  const [filter, setFilter] = useState("all"); // all | pending | done

  const showToast = (msg, type = "info") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 2800);
  };

  const handleSave = async (payload) => {
    if (editTarget) {
      await editHabit(editTarget.id, payload);
      showToast("Habit updated.");
    } else {
      await addHabit(payload);
      showToast("Habit created!");
    }
    setEditTarget(null);
  };

  const handleEdit = (habit) => {
    setEditTarget(habit);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this habit? This cannot be undone.")) return;
    await removeHabit(id);
    showToast("Habit deleted.");
  };

  const handleToggle = async (habit) => {
    await toggleCompletion(habit);
  };

  const filtered = habits.filter((h) => {
    if (filter === "pending") return !h.completed_today;
    if (filter === "done") return h.completed_today;
    return true;
  });

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      {/* Header */}
      <header style={{
        borderBottom: "1px solid var(--border)",
        padding: "18px 0",
        position: "sticky", top: 0,
        background: "rgba(15,15,17,0.85)",
        backdropFilter: "blur(12px)",
        zIndex: 100,
      }}>
        <div style={{ maxWidth: 680, margin: "0 auto", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "24px", letterSpacing: "-0.01em" }}>
            Streaks
          </h1>
          <button
            onClick={() => { setEditTarget(null); setModalOpen(true); }}
            style={{
              background: "var(--accent)", color: "#0f0f11",
              border: "none", borderRadius: "8px",
              padding: "9px 18px", fontWeight: 600, fontSize: "14px",
              display: "flex", alignItems: "center", gap: "6px",
            }}
          >
            <span style={{ fontSize: "18px", lineHeight: 1 }}>+</span> New habit
          </button>
        </div>
      </header>

      {/* Main content */}
      <main style={{ maxWidth: 680, margin: "0 auto", padding: "32px 24px" }}>

        {/* Date label */}
        <p style={{ color: "var(--muted)", fontSize: "13px", marginBottom: "20px", fontFamily: "var(--font-mono)" }}>
          {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
        </p>

        {habits.length > 0 && <StatsBar habits={habits} />}

        {/* Filter tabs */}
        {habits.length > 0 && (
          <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
            {["all", "pending", "done"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                style={{
                  background: filter === f ? "var(--surface2)" : "transparent",
                  border: `1px solid ${filter === f ? "var(--border)" : "transparent"}`,
                  color: filter === f ? "var(--text)" : "var(--muted)",
                  borderRadius: "8px", padding: "6px 14px",
                  fontSize: "13px", fontWeight: 500, textTransform: "capitalize",
                  transition: "all 0.15s",
                }}
              >
                {f}
              </button>
            ))}
          </div>
        )}

        {/* States */}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px 0", color: "var(--muted)" }}>
            Loading…
          </div>
        )}

        {error && (
          <div style={{
            background: "#f8717122", border: "1px solid var(--danger)",
            borderRadius: "var(--radius)", padding: "16px 20px",
            color: "var(--danger)", marginBottom: "20px",
          }}>
            ⚠️ {error} — make sure the backend is running.
          </div>
        )}

        {!loading && !error && habits.length === 0 && (
          <div style={{ textAlign: "center", padding: "80px 0" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🌱</div>
            <p style={{ fontFamily: "var(--font-display)", fontSize: "22px", marginBottom: "8px" }}>
              No habits yet
            </p>
            <p style={{ color: "var(--muted)", marginBottom: "24px" }}>
              Create your first habit to start building your streaks.
            </p>
            <button
              onClick={() => setModalOpen(true)}
              style={{
                background: "var(--accent)", color: "#0f0f11",
                border: "none", borderRadius: "8px",
                padding: "10px 22px", fontWeight: 600,
              }}
            >
              Create a habit
            </button>
          </div>
        )}

        {!loading && filtered.length === 0 && habits.length > 0 && (
          <p style={{ color: "var(--muted)", textAlign: "center", padding: "32px 0" }}>
            No habits match this filter.
          </p>
        )}

        {/* Habit list */}
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {filtered.map((habit) => (
            <HabitCard
              key={habit.id}
              habit={habit}
              onToggle={handleToggle}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      </main>

      {/* Modal */}
      <HabitModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditTarget(null); }}
        onSave={handleSave}
        initial={editTarget}
      />

      {/* Toast */}
      {toast && (
        <div style={{
          position: "fixed", bottom: "24px", left: "50%",
          transform: "translateX(-50%)",
          background: "var(--surface2)",
          border: "1px solid var(--border)",
          color: "var(--text)",
          borderRadius: "10px", padding: "12px 20px",
          fontSize: "14px", fontWeight: 500,
          boxShadow: "var(--shadow)",
          zIndex: 2000,
          animation: "slideUp 0.2s ease",
          whiteSpace: "nowrap",
        }}>
          {toast.msg}
        </div>
      )}
    </div>
  );
}
