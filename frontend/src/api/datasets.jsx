// frontend/src/api/datasets.js
import axios from "axios";
import { BASE_URL } from "./config";

export const fetchDatasets = async () => {
  console.log(`${BASE_URL}/datasets`)
  const res = await axios.get(`${BASE_URL}/datasets`, {
  });
  return res.data;
};


// 觸發 ETL 任務
export const insertETL = async (etlList) => {
  const res = await axios.post(`${BASE_URL}/run-etl`, etlList);
  return res.data;
};
