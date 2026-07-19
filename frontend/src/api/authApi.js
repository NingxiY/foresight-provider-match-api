import client from "./client";

export function login(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return client
    .post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    .then((res) => res.data);
}

export function getMe() {
  return client.get("/auth/me").then((res) => res.data);
}
