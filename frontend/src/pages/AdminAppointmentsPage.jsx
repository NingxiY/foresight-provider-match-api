import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAllAppointments, updateAppointmentStatus } from "../api/appointmentsApi";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/formatDate";

const STATUS_OPTIONS = ["pending", "approved", "declined", "cancelled"];

export default function AdminAppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);
  const [rowErrors, setRowErrors] = useState({});

  const fetchAll = useCallback(() => {
    setLoading(true);
    setError(null);
    return listAllAppointments()
      .then(setAppointments)
      .catch(() => setError("Could not load appointment requests."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  async function handleStatusChange(id, status) {
    setUpdatingId(id);
    setRowErrors((errs) => ({ ...errs, [id]: null }));
    try {
      await updateAppointmentStatus(id, status);
      await fetchAll();
    } catch (err) {
      setRowErrors((errs) => ({
        ...errs,
        [id]: err.response?.data?.detail || "Could not update status.",
      }));
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div className="page">
      <h1>Admin: Appointment Requests</h1>
      <p className="page-subtitle">
        Review and update the status of all patient appointment requests.
      </p>
      {loading && <p className="page-loading">Loading...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && appointments.length === 0 && <p>No appointment requests yet.</p>}
      {!loading && !error && appointments.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient ID</th>
              <th>Provider</th>
              <th>Slot</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Update</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>{a.id}</td>
                <td>{a.patient_id}</td>
                <td>
                  <Link to={`/providers/${a.provider_id}`}>#{a.provider_id}</Link>
                </td>
                <td>{a.slot ? formatDateTime(a.slot.start_time) : "Slot released"}</td>
                <td>{a.reason || "-"}</td>
                <td>
                  <StatusBadge status={a.status} />
                </td>
                <td>
                  <select
                    value={a.status}
                    disabled={updatingId === a.id}
                    onChange={(e) => handleStatusChange(a.id, e.target.value)}
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                  {rowErrors[a.id] && <p className="form-error form-error-small">{rowErrors[a.id]}</p>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
