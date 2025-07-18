// frontend/src/api/predictions.js
import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export async function fetchPredictionRecords() {
  const response = await axios.get(`${BASE_URL}/predict/`);
  return response.data;
}
