import client from "./client";

export function requestMatch(payload) {
  return client.post("/provider-matches/", payload).then((res) => res.data);
}
