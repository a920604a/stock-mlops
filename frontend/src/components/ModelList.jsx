import React, { useEffect, useState , useRef} from 'react';
import { getModels, deleteModelById, submitTrainJob, submitPredictJob  } from '../api/model';
import {
  Box, Table, Thead, Tbody, Tr, Th, Td, TableContainer,
  Spinner, Alert, AlertIcon, IconButton, Text, Flex,
  useDisclosure
} from '@chakra-ui/react';
import { DeleteIcon, ViewIcon,  SearchIcon } from '@chakra-ui/icons';
import { Zap, TrendingUp, Play } from 'lucide-react'; // 預測趨勢
import DeleteConfirmDialog from './DeleteConfirmDialog';
import ModelDetailModal from './ModelDetailModal';

export default function ModelList({ showToast }) {
  const cancelRef = useRef();

  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const [modelToDelete, setModelToDelete] = useState(null);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getModels();
      setModels(data);
    } catch (err) {
      setError("無法加載模型列表。");
      showToast && showToast("錯誤", "無法加載模型列表。", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);


  const handleViewDetails = (model) => {
    setSelectedModel(model);
    onOpen();
  };

  const handleDeleteClick = (model) => {
    setModelToDelete(model);
    onDeleteOpen();
  };

  const confirmDelete = async () => {
    if (!modelToDelete) return;
    try {
      await deleteModelById(modelToDelete.id);
      showToast && showToast("成功", `模型 ID: ${modelToDelete.id} 已成功刪除。`, "success");
      fetchModels();
      onDeleteClose();
    } catch {
      showToast && showToast("錯誤", `刪除模型 ID: ${modelToDelete.id} 失敗。`, "error");
    }
  };

  const handleTrain = async (model) => {
    try {
      showToast && showToast('通知', `開始提交訓練任務，模型 ID: ${model.id}`, 'info');
      const taskId = await submitTrainJob(model.id); // 直接拿字串
      console.log('taskId ', taskId)
      // setTrainTaskId(taskId);
      showToast && showToast('成功', `訓練任務已建立，Task ID: ${taskId}`, 'success');
    } catch (error) {
      showToast && showToast('錯誤', `提交訓練任務失敗: ${error.message}`, 'error');
    }
  };

  const handlePredict = async(model) => {
     try {
      showToast && showToast('通知', `開始提交預測任務，模型 ID: ${model.id}`, 'info');
      const data = await submitPredictJob(model.id);
      showToast && showToast('成功', `預測任務已建立，Task ID: ${data.task_id}`, 'success');
      // 同理可做狀態輪詢或跳轉
    } catch (error) {
      showToast && showToast('錯誤', `提交預測任務失敗: ${error.message}`, 'error');
    }
  };
  if (loading) {
    return (
      <Flex justify="center" align="center" height="200px">
        <Spinner size="xl" color="teal.500" />
        <Text ml={4}>加載模型中...</Text>
      </Flex>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Text fontSize="xl" mb={4} fontWeight="bold" color="teal.700">模型列表</Text>
      {models.length === 0 ? (
        <Text>目前沒有已訓練的模型。</Text>
      ) : (
        <TableContainer border="1px" borderColor="gray.200" rounded="md" shadow="sm">
          <Table variant="simple" size="sm">
            <Thead bg="teal.50">
              <Tr>
                <Th>ID</Th>
                <Th>股票代號</Th>
                <Th>模型類型</Th>
                <Th>運行ID</Th>
                <Th>建立時間</Th>
                <Th>操作</Th>
              </Tr>
            </Thead>
            <Tbody>
              {models.map((model) => (
                <Tr key={model.id} _hover={{ bg: "gray.50" }}>
                  <Td>{model.id}</Td>
                  <Td>{model.ticker}</Td>
                  <Td>{model.model_type || 'N/A'}</Td>
                  <Td>{model.run_id}</Td>
                  <Td>{new Date(model.created_at).toLocaleString()}</Td>
                  <Td>
                    <IconButton
                      icon={<Play />}
                      aria-label="訓練模型"
                      size="sm"
                      mr={2}
                      colorScheme="green"
                      variant="outline"
                      rounded="full"
                      onClick={() => handleTrain(model)}
                    />
                    <IconButton
                      icon={<Zap />}
                      aria-label="模型預測"
                      size="sm"
                      mr={2}
                      colorScheme="purple"
                      variant="outline"
                      rounded="full"
                      onClick={() => handlePredict(model)}
                    />
                    <IconButton
                      icon={<ViewIcon />}
                      aria-label="查看詳情"
                      onClick={() => handleViewDetails(model)}
                      size="sm"
                      mr={2}
                      colorScheme="blue"
                      variant="outline"
                      rounded="full"
                    />
                    <IconButton
                      icon={<DeleteIcon />}
                      aria-label="刪除模型"
                      onClick={() => handleDeleteClick(model)}
                      size="sm"
                      colorScheme="red"
                      variant="outline"
                      rounded="full"
                    />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      )}

      <ModelDetailModal
        isOpen={isOpen}
        onClose={onClose}
        model={selectedModel}
      />
      <DeleteConfirmDialog
        isOpen={isDeleteOpen}
        onClose={onDeleteClose}
        onConfirm={confirmDelete}
        itemName={`模型 ID: ${modelToDelete?.id}`}
      />

    </Box>
  );
}
