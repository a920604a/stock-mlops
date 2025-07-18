// frontend/src/components/ModelActions.js
import { submitTrainJob, submitPredictJob, deleteModelById } from '../api/model';

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

export async function predictModel(model, target_date, showToast) {
  try {
    showToast && showToast('通知', `開始提交預測任務，模型 ID: ${model.id}`, 'info');
    const data = await submitPredictJob(model.ticker, model.exchange, target_date);

    const actualCloseText = data.actual_close === 0.0 ? '尚未收盤' : data.actual_close.toFixed(2);

    showToast && showToast(
      '成功',
      `✅ 預測 ${data.ticker} ${data.target_date} 收盤價：${data.predicted_close.toFixed(2)}\n` +
      `📊 實際收盤價：${actualCloseText}\n` +
      `🕒 預測時間：${new Date(data.predicted_at).toLocaleString()}`,
      'success'
    );
    return data;
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
