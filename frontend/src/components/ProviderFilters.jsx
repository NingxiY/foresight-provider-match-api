import { useState } from "react";

export default function ProviderFilters({ onApply }) {
  const [state, setState] = useState("");
  const [insurance, setInsurance] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [acceptingOnly, setAcceptingOnly] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    onApply({
      state: state || undefined,
      insurance: insurance || undefined,
      specialty: specialty || undefined,
      acceptingNewPatients: acceptingOnly ? true : undefined,
    });
  }

  function handleReset() {
    setState("");
    setInsurance("");
    setSpecialty("");
    setAcceptingOnly(false);
    onApply({});
  }

  return (
    <form className="filters" onSubmit={handleSubmit}>
      <div className="filters-row">
        <input
          placeholder="State (e.g. NY)"
          value={state}
          onChange={(e) => setState(e.target.value)}
        />
        <input
          placeholder="Insurance (e.g. Aetna)"
          value={insurance}
          onChange={(e) => setInsurance(e.target.value)}
        />
        <input
          placeholder="Specialty (e.g. Anxiety)"
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
        />
        <label className="filters-checkbox">
          <input
            type="checkbox"
            checked={acceptingOnly}
            onChange={(e) => setAcceptingOnly(e.target.checked)}
          />
          Accepting new patients only
        </label>
      </div>
      <div className="filters-actions">
        <button type="submit" className="btn btn-primary">
          Search
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleReset}>
          Reset
        </button>
      </div>
    </form>
  );
}
