import React, { useEffect, useState } from 'react';
import { getModels, deleteModelById } from '../api/model';
import {
  Box, Table, Thead, Tbody, Tr, Th, Td, TableContainer,
  Spinner, Alert, AlertIcon, IconButton, Text, Flex,
  useDisclosure,
} from '@chakra-ui/react';
import { DeleteIcon, ViewIcon, TriangleUpIcon, SearchIcon } from '@chakra-ui/icons';
import ModelDetailModal from './ModelDetailModal';

export default function ModelList({ showToast }) {
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

  const handleTrain = (model) => {
    showToast && showToast('通知', `已開始訓練模型 ID: ${model.id}`, 'info');
  };

  const handlePredict = (model) => {
    showToast && showToast('通知', `已開始模型預測 ID: ${model.id}`, 'info');
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
      <Text fontSize="xl" mb={4} fontWeight="bold" color="teal.700">已訓練模型列表</Text>
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
                      icon={<TriangleUpIcon />}
                      aria-label="訓練模型"
                      size="sm"
                      mr={2}
                      colorScheme="green"
                      variant="outline"
                      rounded="full"
                      onClick={() => handleTrain(model)}
                    />
                    <IconButton
                      icon={<SearchIcon />}
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

      {/* 刪除確認 Modal 依舊寫在這 */}
      {/* ...刪除 Modal 程式碼不變... */}
    </Box>
  );
}
