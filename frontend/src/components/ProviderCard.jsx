import { Link } from "react-router-dom";
import { formatDateTime } from "../utils/formatDate";

export default function ProviderCard({ provider }) {
  const nextSlot = formatDateTime(provider.next_available_slot);

  return (
    <Link to={`/providers/${provider.id}`} className="provider-card">
      <div className="provider-card-header">
        <h3>{provider.full_name}</h3>
        {!provider.accepting_new_patients && (
          <span className="tag tag-muted">Not accepting new patients</span>
        )}
      </div>
      <p className="provider-specialty">
        {provider.specialty} &middot; {provider.state}
      </p>
      {provider.headline && <p className="provider-headline">{provider.headline}</p>}
      <p className="provider-next-slot">
        {nextSlot ? `Next available: ${nextSlot}` : "No upcoming availability"}
      </p>
    </Link>
  );
}
