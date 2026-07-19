import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getProvider } from "../api/providersApi";
import { createAppointmentRequest } from "../api/appointmentsApi";
import AppointmentSlotPicker from "../components/AppointmentSlotPicker";
import { useAuth } from "../context/AuthContext";

export default function ProviderDetailPage() {
  const { providerId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [provider, setProvider] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bookingError, setBookingError] = useState(null);
  const [booking, setBooking] = useState(false);

  const fetchProvider = useCallback(() => {
    setLoading(true);
    setError(null);
    return getProvider(providerId)
      .then(setProvider)
      .catch(() => setError("Could not load this provider."))
      .finally(() => setLoading(false));
  }, [providerId]);

  useEffect(() => {
    fetchProvider();
  }, [fetchProvider]);

  async function handleBook(slotId, reason) {
    setBooking(true);
    setBookingError(null);
    try {
      const appointment = await createAppointmentRequest({
        provider_id: provider.id,
        slot_id: slotId,
        reason,
      });
      navigate(`/appointment-confirmation/${appointment.id}`, {
        state: { appointment, providerName: provider.full_name },
      });
    } catch (err) {
      setBookingError(err.response?.data?.detail || "Could not book this slot.");
      setBooking(false);
    }
  }

  if (loading) {
    return (
      <div className="page">
        <p className="page-loading">Loading provider...</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="page">
        <p className="form-error">{error}</p>
      </div>
    );
  }
  if (!provider) return null;

  return (
    <div className="page">
      <Link to="/" className="back-link">
        &larr; Back to search
      </Link>
      <div className="provider-detail">
        <div className="provider-detail-header">
          <h1>{provider.full_name}</h1>
          {!provider.accepting_new_patients && (
            <span className="tag tag-muted">Not accepting new patients</span>
          )}
        </div>
        <p className="provider-specialty">
          {provider.specialty} &middot; {provider.location}
        </p>
        <dl className="provider-detail-facts">
          <div>
            <dt>Insurance accepted</dt>
            <dd>{provider.accepted_insurance || "Not specified"}</dd>
          </div>
          <div>
            <dt>Languages</dt>
            <dd>{provider.languages || "Not specified"}</dd>
          </div>
          <div>
            <dt>Years of experience</dt>
            <dd>{provider.years_experience ?? "Not specified"}</dd>
          </div>
          <div>
            <dt>General availability</dt>
            <dd>{provider.available_days || "Not specified"}</dd>
          </div>
        </dl>
        {provider.bio && <p className="provider-bio">{provider.bio}</p>}

        <h2>Book an appointment</h2>
        {!user && (
          <p>
            Please <Link to="/login">log in</Link> to book an appointment.
          </p>
        )}
        {user && (
          <>
            {bookingError && <p className="form-error">{bookingError}</p>}
            <AppointmentSlotPicker
              slots={provider.available_slots}
              onBook={handleBook}
              booking={booking}
            />
          </>
        )}
      </div>
    </div>
  );
}
