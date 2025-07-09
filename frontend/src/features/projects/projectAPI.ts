import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:4000/api",
  withCredentials: true,
});

export async function fetchProjects() {
  const res = await api.get("/projects");
  return res.data;
}
