import { useState } from "react";
import { formatDateTime } from "../utils/formatDate";

export default function AppointmentSlotPicker({ slots, onBook, booking }) {
  const [selectedSlotId, setSelectedSlotId] = useState(null);
  const [reason, setReason] = useState("");

  if (!slots || slots.length === 0) {
    return <p className="no-slots">No upcoming available slots for this provider right now.</p>;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!selectedSlotId) return;
    onBook(selectedSlotId, reason);
  }

  return (
    <form className="slot-picker" onSubmit={handleSubmit}>
      <div className="slot-list">
        {slots.map((slot) => (
          <label
            key={slot.id}
            className={`slot-option ${selectedSlotId === slot.id ? "slot-option-selected" : ""}`}
          >
            <input
              type="radio"
              name="slot"
              value={slot.id}
              checked={selectedSlotId === slot.id}
              onChange={() => setSelectedSlotId(slot.id)}
            />
            {formatDateTime(slot.start_time)}
          </label>
        ))}
      </div>
      <textarea
        placeholder="Reason for visit (optional)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        rows={2}
      />
      <button type="submit" className="btn btn-primary" disabled={!selectedSlotId || booking}>
        {booking ? "Booking..." : "Book this slot"}
      </button>
    </form>
  );
}
