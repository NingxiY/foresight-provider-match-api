import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyAppointments } from "../api/appointmentsApi";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/formatDate";

export default function MyAppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMyAppointments()
      .then(setAppointments)
      .catch(() => setError("Could not load your appointment requests."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <h1>My Appointment Requests</h1>
      {loading && <p className="page-loading">Loading...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && appointments.length === 0 && (
        <p>You haven't requested any appointments yet.</p>
      )}
      {!loading && !error && appointments.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Provider</th>
              <th>Slot</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Requested</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/providers/${a.provider_id}`}>Provider #{a.provider_id}</Link>
                </td>
                <td>{a.slot ? formatDateTime(a.slot.start_time) : "Slot released"}</td>
                <td>{a.reason || "-"}</td>
                <td>
                  <StatusBadge status={a.status} />
                </td>
                <td>{new Date(a.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
