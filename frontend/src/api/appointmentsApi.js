import client from "./client";

export function createAppointmentRequest(payload) {
  return client.post("/appointment-requests/", payload).then((res) => res.data);
}

export function getMyAppointments() {
  return client.get("/appointment-requests/me").then((res) => res.data);
}

export function listAllAppointments() {
  return client.get("/appointment-requests/").then((res) => res.data);
}

export function updateAppointmentStatus(requestId, status) {
  return client
    .patch(`/appointment-requests/${requestId}/status`, { status })
    .then((res) => res.data);
}
