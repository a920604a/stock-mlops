// frontend/src/api/datasets.js
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export const fetchDatasets = async () => {
  const res = await axios.get(`${BASE_URL}/datasets`, {
  });
  return res.data;
};
