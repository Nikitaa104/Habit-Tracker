import React from "react";

export default function StatsBar({ habits }) {
  if (!habits.length) return null;

  const total = habits.length;
  const done = habits.filter((h) => h.completed_today).length;
  const pct = Math.round((done / total) * 100);
  const topStreak = Math.max(...habits.map((h) => h.streak));

  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius)",
      padding: "20px 24px",
      marginBottom: "24px",
      display: "grid",
      gridTemplateColumns: "1fr 1fr 1fr",
      gap: "16px",
      textAlign: "center",
    }}>
      <Stat label="Today" value={`${done}/${total}`} />
      <Stat label="Completion" value={`${pct}%`} highlight />
      <Stat label="Best Streak" value={topStreak > 0 ? `🔥 ${topStreak}` : "—"} />
    </div>
  );
}

function Stat({ label, value, highlight }) {
  return (
    <div>
      <div style={{
        fontFamily: "var(--font-display)",
        fontSize: "26px",
        color: highlight ? "var(--accent)" : "var(--text)",
        lineHeight: 1.1,
      }}>{value}</div>
      <div style={{
        fontSize: "11px", textTransform: "uppercase",
        letterSpacing: "0.08em", color: "var(--muted)", marginTop: "4px",
      }}>{label}</div>
    </div>
  );
}
