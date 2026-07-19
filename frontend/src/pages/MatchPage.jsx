import { useState } from "react";
import ProviderCard from "../components/ProviderCard";
import { requestMatch } from "../api/matchesApi";

export default function MatchPage() {
  const [form, setForm] = useState({ state: "", insurance: "", concern: "", preferred_day: "" });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await requestMatch({
        state: form.state,
        concern: form.concern,
        insurance: form.insurance || undefined,
        preferred_day: form.preferred_day || undefined,
      });
      setResults(data.matched_providers);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not fetch matches.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Get Matched</h1>
      <p className="page-subtitle">
        Tell us what you're looking for and we'll rank providers for you.
      </p>
      <form className="form-card" onSubmit={handleSubmit}>
        <label>
          State
          <input
            value={form.state}
            onChange={(e) => handleChange("state", e.target.value)}
            placeholder="NY"
            required
          />
        </label>
        <label>
          Concern
          <input
            value={form.concern}
            onChange={(e) => handleChange("concern", e.target.value)}
            placeholder="Anxiety"
            required
          />
        </label>
        <label>
          Insurance (optional)
          <input
            value={form.insurance}
            onChange={(e) => handleChange("insurance", e.target.value)}
            placeholder="BlueCross"
          />
        </label>
        <label>
          Preferred day (optional)
          <input
            value={form.preferred_day}
            onChange={(e) => handleChange("preferred_day", e.target.value)}
            placeholder="Monday"
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Matching..." : "Find my matches"}
        </button>
      </form>

      {results && (
        <div className="match-results">
          <h2>Ranked matches</h2>
          {results.length === 0 && <p>No providers matched your preferences.</p>}
          <div className="provider-grid">
            {results.map(({ provider, score }) => (
              <div key={provider.id} className="match-result">
                <ProviderCard provider={provider} />
                <span className="match-score">Score: {score}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
