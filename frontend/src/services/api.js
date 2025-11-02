// src/services/api.js
import axios from 'axios'

const API = axios.create({
  baseURL: 'http://127.0.0.1:5000'   // <-- no /api prefix unless you used it
})

// attach token
API.interceptors.request.use((req) => {
  const token = localStorage.getItem('token')
  if (token) req.headers.Authorization = `Bearer ${token}`
  return req
})

export default API
