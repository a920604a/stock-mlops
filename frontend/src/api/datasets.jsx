// frontend/src/api/datasets.js
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const fetchDatasets = async (ticker = "") => {
  const res = await axios.get(`${BASE_URL}/datasets`, {
    params: { ticker },
  });
  return res.data;
};
