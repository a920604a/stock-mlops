// frontend/src/api/predictions.js
import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8002/api";


// 假設預測 API
export const submitPredictJob = async (ticker, exchange, target_date) => {
  try {
    const response = await axios.post(`${BASE_URL}/predict/`, { ticker: ticker, exchange: exchange, target_date: target_date });
    console.log('response', response.data)
    return response.data;
  } catch (error) {
    console.error("API 提交預測任務失敗:", error);
    throw error;
  }
};


export async function fetchPredictionRecords() {
  console.log("Fetching prediction records from:", `${BASE_URL}/predict/`);
  const response = await axios.get(`${BASE_URL}/predict/`);
  return response.data;
}

export async function fetchFuturePrediction(ticker, exchange, days) {
  console.log("Fetching future prediction from:", `${BASE_URL}/predict/future/`);
  const response = await axios.post(`${BASE_URL}/predict/future/`, {
    ticker,
    exchange,
    days,
  });
  return response.data;
}


export const fetchPredictStatus = async (taskId) => {
  const response = await axios.get(`${BASE_URL}/predict/future/status/${taskId}`)
  return response.data
}


export async function fetchPartialPredictStatus(taskId) {
  const response = await axios.get(`${BASE_URL}/predict/future/partial_status/${taskId}`);
  return response.data;
}
