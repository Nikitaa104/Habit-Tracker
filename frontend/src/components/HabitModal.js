import React, { useState, useEffect } from "react";

const COLORS = [
  "#a78bfa", "#34d399", "#fb923c", "#f472b6",
  "#60a5fa", "#facc15", "#f87171", "#4ade80",
];

const styles = {
  overlay: {
    position: "fixed", inset: 0,
    background: "rgba(0,0,0,0.7)",
    backdropFilter: "blur(4px)",
    display: "flex", alignItems: "center", justifyContent: "center",
    zIndex: 1000, padding: "16px",
    animation: "fadeIn 0.15s ease",
  },
  modal: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "28px",
    width: "100%",
    maxWidth: "460px",
    boxShadow: "var(--shadow)",
    animation: "slideUp 0.2s ease",
  },
  title: {
    fontFamily: "var(--font-display)",
    fontSize: "22px",
    marginBottom: "24px",
  },
  field: { marginBottom: "16px" },
  label: {
    display: "block",
    fontSize: "12px",
    fontWeight: 600,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: "var(--muted)",
    marginBottom: "6px",
  },
  colorRow: { display: "flex", gap: "10px", flexWrap: "wrap" },
  colorDot: (color, selected) => ({
    width: 28, height: 28,
    borderRadius: "50%",
    background: color,
    border: selected ? "3px solid var(--text)" : "3px solid transparent",
    cursor: "pointer",
    outline: selected ? `2px solid ${color}` : "none",
    outlineOffset: "2px",
    transition: "transform 0.1s",
    transform: selected ? "scale(1.15)" : "scale(1)",
  }),
  errorText: { color: "var(--danger)", fontSize: "12px", marginTop: "4px" },
  actions: { display: "flex", gap: "10px", justifyContent: "flex-end", marginTop: "24px" },
  btnPrimary: {
    background: "var(--accent)", color: "#0f0f11",
    border: "none", borderRadius: "8px",
    padding: "10px 22px", fontWeight: 600, fontSize: "14px",
  },
  btnSecondary: {
    background: "transparent", color: "var(--muted)",
    border: "1px solid var(--border)", borderRadius: "8px",
    padding: "10px 18px", fontSize: "14px",
  },
};

export default function HabitModal({ open, onClose, onSave, initial }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [frequency, setFrequency] = useState("daily");
  const [color, setColor] = useState(COLORS[0]);
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setName(initial?.name || "");
      setDescription(initial?.description || "");
      setFrequency(initial?.frequency || "daily");
      setColor(initial?.color || COLORS[0]);
      setFieldErrors({});
    }
  }, [open, initial]);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFieldErrors({});
    setSubmitting(true);
    try {
      await onSave({ name, description, frequency, color });
      onClose();
    } catch (err) {
      if (err.errors) setFieldErrors(err.errors);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <style>{`
        @keyframes fadeIn { from { opacity:0 } to { opacity:1 } }
        @keyframes slideUp { from { transform:translateY(16px); opacity:0 } to { transform:translateY(0); opacity:1 } }
      `}</style>
      <div style={styles.modal}>
        <h2 style={styles.title}>{initial ? "Edit habit" : "New habit"}</h2>
        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Name *</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Morning run"
              autoFocus
            />
            {fieldErrors.name && <p style={styles.errorText}>{fieldErrors.name}</p>}
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="Optional details..."
              style={{ resize: "vertical" }}
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Frequency</label>
            <select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Color</label>
            <div style={styles.colorRow}>
              {COLORS.map((c) => (
                <button
                  key={c} type="button"
                  style={styles.colorDot(c, color === c)}
                  onClick={() => setColor(c)}
                  aria-label={`Select color ${c}`}
                />
              ))}
            </div>
          </div>
          <div style={styles.actions}>
            <button type="button" style={styles.btnSecondary} onClick={onClose}>
              Cancel
            </button>
            <button type="submit" style={styles.btnPrimary} disabled={submitting}>
              {submitting ? "Saving…" : initial ? "Save changes" : "Create habit"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
