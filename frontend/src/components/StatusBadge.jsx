const STATUS_STYLES = {
  pending: "status-pending",
  approved: "status-approved",
  declined: "status-declined",
  cancelled: "status-cancelled",
};

export default function StatusBadge({ status }) {
  return <span className={`status-badge ${STATUS_STYLES[status] || ""}`}>{status}</span>;
}
