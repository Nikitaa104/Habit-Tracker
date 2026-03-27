import React, { useState } from "react";

export default function HabitCard({ habit, onToggle, onEdit, onDelete }) {
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'ok' | 'error'

  const handleToggle = async () => {
    if (busy) return;
    setBusy(true);
    setFeedback(null);
    try {
      await onToggle(habit);
      setFeedback("ok");
      setTimeout(() => setFeedback(null), 600);
    } catch {
      setFeedback("error");
      setTimeout(() => setFeedback(null), 1500);
    } finally {
      setBusy(false);
    }
  };

  const streakLabel = habit.frequency === "weekly"
    ? null
    : habit.streak > 0
      ? `🔥 ${habit.streak} day${habit.streak !== 1 ? "s" : ""}`
      : null;

  return (
    <div style={{
      background: "var(--surface)",
      border: `1px solid ${habit.completed_today ? habit.color + "55" : "var(--border)"}`,
      borderLeft: `4px solid ${habit.color}`,
      borderRadius: "var(--radius)",
      padding: "18px 20px",
      display: "flex",
      alignItems: "center",
      gap: "16px",
      transition: "border-color 0.2s, box-shadow 0.2s",
      boxShadow: habit.completed_today ? `0 0 0 1px ${habit.color}33` : "none",
    }}>
      {/* Toggle button */}
      <button
        onClick={handleToggle}
        disabled={busy}
        style={{
          flexShrink: 0,
          width: 32, height: 32,
          borderRadius: "50%",
          border: `2px solid ${habit.completed_today ? habit.color : "var(--border)"}`,
          background: habit.completed_today ? habit.color : "transparent",
          display: "flex", alignItems: "center", justifyContent: "center",
          transition: "all 0.15s",
          fontSize: "14px",
          transform: feedback === "ok" ? "scale(1.2)" : "scale(1)",
        }}
        aria-label={habit.completed_today ? "Mark incomplete" : "Mark complete"}
      >
        {habit.completed_today && (
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2.5 7L6 10.5L11.5 4" stroke="#0f0f11" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </button>

      {/* Info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 600,
          fontSize: "15px",
          textDecoration: habit.completed_today ? "line-through" : "none",
          color: habit.completed_today ? "var(--muted)" : "var(--text)",
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          {habit.name}
        </div>
        <div style={{ display: "flex", gap: "10px", marginTop: "3px", flexWrap: "wrap" }}>
          <span style={{
            fontSize: "11px", fontFamily: "var(--font-mono)",
            color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em",
          }}>
            {habit.frequency}
          </span>
          {streakLabel && (
            <span style={{ fontSize: "12px", color: habit.color, fontWeight: 500 }}>
              {streakLabel}
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: "flex", gap: "6px", flexShrink: 0 }}>
        <button
          onClick={() => onEdit(habit)}
          style={{
            background: "transparent", border: "none",
            color: "var(--muted)", padding: "6px",
            borderRadius: "6px", fontSize: "15px",
            transition: "color 0.15s",
          }}
          title="Edit"
          onMouseEnter={e => e.currentTarget.style.color = "var(--text)"}
          onMouseLeave={e => e.currentTarget.style.color = "var(--muted)"}
        >✏️</button>
        <button
          onClick={() => onDelete(habit.id)}
          style={{
            background: "transparent", border: "none",
            color: "var(--muted)", padding: "6px",
            borderRadius: "6px", fontSize: "15px",
            transition: "color 0.15s",
          }}
          title="Delete"
          onMouseEnter={e => e.currentTarget.style.color = "var(--danger)"}
          onMouseLeave={e => e.currentTarget.style.color = "var(--muted)"}
        >🗑</button>
      </div>
    </div>
  );
}
