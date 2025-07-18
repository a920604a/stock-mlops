// frontend/src/api/models.js
import axios from 'axios';

// 後端 FastAPI 的基礎 URL
// 根據您的環境，這可能是 'http://localhost:8000' 或 'http://backend:8001'
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

/**
 * 從後端獲取所有模型元數據。
 * @returns {Promise<Array>} 包含模型數據的 Promise。
 */
export const getModels = async () => {
    try {
        // 更新 API 路徑為 /api/models/
        const response = await axios.get(`${BASE_URL}/models/`);
        return response.data;
    } catch (error) {
        console.error("API 獲取模型列表失敗:", error);
        throw error; // 重新拋出錯誤以便調用者處理
    }
};

export const getMLflowModels = async () => {
    try {
        // 更新 API 路徑為 /api/models/
        const response = await axios.get(`${BASE_URL}/mlflow/models`);
        return response.data;
    } catch (error) {
        console.error("API 獲取模型列表失敗:", error);
        throw error; // 重新拋出錯誤以便調用者處理
    }
};


/**
 * 根據 ID 刪除一個模型元數據。
 * @param {number} modelId 要刪除的模型 ID。
 * @returns {Promise<Object>} 包含刪除結果的 Promise。
 */
export const deleteModelById = async (modelId) => {
    try {
        // 更新 API 路徑為 /api/models/{id}
        const response = await axios.delete(`${BASE_URL}/models/${modelId}`);
        return response.data;
    } catch (error) {
        console.error(`API 刪除模型 ID: ${modelId} 失敗:`, error);
        throw error; // 重新拋出錯誤以便調用者處理
    }
};

/**
 * 創建一個新的模型元數據。
 * @param {Object} modelData 包含新模型數據的物件。
 * @returns {Promise<Object>} 包含新創建模型數據的 Promise。
 */
export const createModel = async (modelData) => {
    try {
        console.log("createModel ", modelData)
        const response = await axios.post(`${BASE_URL}/models/`, modelData);
        return response.data;
    } catch (error) {
        console.error("API 創建模型失敗:", error);
        throw error;
    }
};

/**
 * 更新一個現有的模型元數據。
 * @param {number} modelId 要更新的模型 ID。
 * @param {Object} updateData 包含要更新字段的物件。
 * @returns {Promise<Object>} 包含更新後模型數據的 Promise。
 */
export const updateModel = async (modelId, updateData) => {
    try {
        const response = await axios.put(`${BASE_URL}/models/${modelId}`, updateData);
        return response.data;
    } catch (error) {
        console.error(`API 更新模型 ID: ${modelId} 失敗:`, error);
        throw error;
    }
};

/**
 * 根據 ID 獲取單個模型元數據詳情。
 * @param {number} modelId 要獲取詳情的模型 ID。
 * @returns {Promise<Object>} 包含模型詳情數據的 Promise。
 */
export const getModelDetails = async (modelId) => {
    try {
        const response = await axios.get(`${BASE_URL}/models/${modelId}`);
        return response.data;
    } catch (error) {
        console.error(`API 獲取模型詳情 ID: ${modelId} 失敗:`, error);
        throw error;
    }
};


export const fetchTrainStatus = async (taskId) => {
    const response = await axios.get(`${BASE_URL}/train/status/${taskId}`)
    return response.data
}


// 新增訓練任務的 API 呼叫
export const submitTrainJob = async (modelId) => {
  try {
    // 假設後端需要接收 modelId，可以改成適合你的結構
    const response = await axios.post(`${BASE_URL}/train`, { model_id: modelId });
    return response.data.task_id;  // 從物件取出 task_id 字串或數字
  } catch (error) {
    console.error("API 提交訓練任務失敗:", error);
    throw error;
  }
};


// 假設預測 API
export const submitPredictJob = async (ticker, exchange, target_date) => {
  try {
    const response = await axios.post(`${BASE_URL}/predict/`, {ticker: ticker, exchange: exchange, target_date: target_date});
    console.log('response', response.data)
    return response.data;
  } catch (error) {
    console.error("API 提交預測任務失敗:", error);
    throw error;
  }
};
