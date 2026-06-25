import axios from "axios"

// Vite dev proxy forwards /api → localhost:8000
// In production set VITE_API_BASE_URL to your deployed backend
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api"

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
})
