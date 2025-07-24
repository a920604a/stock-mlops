// frontend/src/components/ModelActions.js
import { submitTrainJob, deleteModelById } from '../api/model';
import { submitPredictJob } from '../api/predictions';

export async function trainModel(model, showToast) {
  try {
    showToast && showToast('通知', `開始提交訓練任務，模型 ID: ${model.id}`, 'info');
    const taskId = await submitTrainJob(model.id);
    showToast && showToast('成功', `訓練任務已建立，Task ID: ${taskId}`, 'success');
    return taskId;
  } catch (error) {
    showToast && showToast('錯誤', `提交訓練任務失敗: ${error.message}`, 'error');
    throw error;
  }
}

export function predictModel(model, target_date, showToast) {
  try {
    showToast && showToast('通知', `開始提交預測任務，模型 ID: ${model.id}`, 'info');
    // 呼叫後端 API 提交預測任務，不需接收結果
    submitPredictJob(model.ticker, model.exchange, target_date);
  } catch (error) {
    showToast && showToast('錯誤', `提交預測任務失敗: ${error.message}`, 'error');
    throw error;
  }
}



export async function deleteModel(modelId, showToast) {
  try {
    await deleteModelById(modelId);
    showToast && showToast("成功", `模型 ID: ${modelId} 已成功刪除。`, "success");
  } catch (error) {
    showToast && showToast("錯誤", `刪除模型 ID: ${modelId} 失敗。`, "error");
    throw error;
  }
}
