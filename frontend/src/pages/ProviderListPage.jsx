import { useCallback, useEffect, useState } from "react";
import ProviderCard from "../components/ProviderCard";
import ProviderFilters from "../components/ProviderFilters";
import { listProviders } from "../api/providersApi";

export default function ProviderListPage() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProviders = useCallback((filters = {}) => {
    setLoading(true);
    setError(null);
    listProviders(filters)
      .then(setProviders)
      .catch(() => setError("Could not load providers. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  return (
    <div className="page">
      <h1>Find a Provider</h1>
      <p className="page-subtitle">
        Browse mental health providers by state, insurance, and specialty.
      </p>
      <ProviderFilters onApply={fetchProviders} />
      {loading && <p className="page-loading">Loading providers...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && providers.length === 0 && <p>No providers match these filters.</p>}
      <div className="provider-grid">
        {providers.map((p) => (
          <ProviderCard key={p.id} provider={p} />
        ))}
      </div>
    </div>
  );
}
