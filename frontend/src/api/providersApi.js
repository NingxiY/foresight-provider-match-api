import client from "./client";

export function listProviders(filters = {}) {
  const params = {};
  if (filters.state) params.state = filters.state;
  if (filters.insurance) params.insurance = filters.insurance;
  if (filters.specialty) params.specialty = filters.specialty;
  if (filters.acceptingNewPatients !== undefined) {
    params.accepting_new_patients = filters.acceptingNewPatients;
  }
  return client.get("/providers/", { params }).then((res) => res.data);
}

export function getProvider(providerId) {
  return client.get(`/providers/${providerId}`).then((res) => res.data);
}
