import { useParams, useLocation, useNavigate, Link } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils/formatDate";

export default function AppointmentConfirmationPage() {
  const { appointmentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const appointment = location.state?.appointment;
  const providerName = location.state?.providerName;
  const hasMatchingState = appointment && String(appointment.id) === appointmentId;

  if (!hasMatchingState) {
    return (
      <div className="page page-narrow">
        <h1>Confirmation not available</h1>
        <p className="page-subtitle">
          We couldn't find the details for this appointment request — this can happen after a page
          refresh, since this demo doesn't store confirmation details separately. Your request was
          still saved.
        </p>
        <Link to="/appointments" className="btn btn-primary">
          View My Appointments
        </Link>
      </div>
    );
  }

  return (
    <div className="page page-narrow">
      <div className="confirmation-card">
        <span className="confirmation-check">&#10003;</span>
        <h1>Appointment Request Submitted</h1>
        <p className="page-subtitle">
          Your request has been sent and is pending review by the provider or an admin.
        </p>

        <dl className="provider-detail-facts confirmation-facts">
          <div>
            <dt>Provider</dt>
            <dd>{providerName || `Provider #${appointment.provider_id}`}</dd>
          </div>
          <div>
            <dt>Appointment time</dt>
            <dd>
              {appointment.slot
                ? `${formatDateTime(appointment.slot.start_time)} - ${new Date(
                    appointment.slot.end_time,
                  ).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}`
                : "Not available"}
            </dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>
              <StatusBadge status={appointment.status} />
            </dd>
          </div>
          {appointment.reason && (
            <div>
              <dt>Reason</dt>
              <dd>{appointment.reason}</dd>
            </div>
          )}
        </dl>

        <div className="confirmation-actions">
          <button type="button" className="btn btn-primary" onClick={() => navigate("/appointments")}>
            View My Appointments
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate("/")}>
            Find More Providers
          </button>
        </div>
      </div>
    </div>
  );
}
