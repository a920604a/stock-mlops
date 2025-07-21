import React, { useEffect, useState , useRef} from 'react';
import { getModels, getMLflowModels, deleteModelById  } from '../api/model';
import {
  Box, Table, Thead, Tbody, Tr, Th, Td, TableContainer,
  Spinner, Alert, AlertIcon, IconButton, Text, Flex,
  useDisclosure, Checkbox, useToast
} from '@chakra-ui/react';

import { DeleteIcon, ViewIcon,  SearchIcon } from '@chakra-ui/icons';
import { Zap, TrendingUp, Play } from 'lucide-react'; // 預測趨勢
import DeleteConfirmDialog from './DeleteConfirmDialog';
import ModelDetailModal from './ModelDetailModal';
import { trainModel, predictModel } from './ModelActions';
import PredictDateModal from './PredictDateModal';


export default function ModelList({ showToast }) {
  const cancelRef = useRef();
  const [showColumns, setShowColumns] = useState({
    run_id: false,
    model_uri: false,
    train_size: false,
    val_size: false,
    percentage: false,
    rmse:false,
  });
  const toggleColumn = (col) => {
    setShowColumns((prev) => ({ ...prev, [col]: !prev[col] }));
  };

  const [isPredictModalOpen, setPredictModalOpen] = useState(false);
  const [modelToPredict, setModelToPredict] = useState(null);


  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const [modelToDelete, setModelToDelete] = useState(null);

  const [predictions, setPredictions] = useState([]);
  const toast = useToast();

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMLflowModels();
      console.log('data', data)
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

    useEffect(() => {
      const ws = new WebSocket("ws://localhost:8010/ws/predictions");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setPredictions((prev) => [data, ...prev]);

        // 觸發 Toast 彈窗通知
        toast({
          title: `股票 ${data.ticker} 新預測`,
          description: `預測收盤價: ${data.predicted_close}，實際: ${data.actual_close ?? '無資料'}`,
          status: "info",
          duration: 2000,
          isClosable: true,
          position: "top-right",
        });
      };
      return () => ws.close();
    }, [toast]);


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
    await trainModel(model, showToast);
  };

  const openPredictModal = (model) => {
    setModelToPredict(model);
    setPredictModalOpen(true);
  };
  const handlePredictSubmit = async(model, target_date) => {

    predictModel(model, target_date, showToast);
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
      {/* 控制顯示欄位的 checkbox */}
      <Box mb={4}>
        {Object.keys(showColumns).map((col) => (
          <Checkbox
            key={col}
            isChecked={showColumns[col]}
            onChange={() => toggleColumn(col)}
            mr={4}
          >
            <Text as="span">{col}</Text>
          </Checkbox>
        ))}
      </Box>

      <Text fontSize="xl" mb={4} fontWeight="bold" color="teal.700">模型列表</Text>
      {models.length === 0 ? (
        <Text>目前沒有已訓練的模型。</Text>
      ) : (
        <TableContainer border="1px" borderColor="gray.200" rounded="md" shadow="sm" maxWidth="100%" overflowX="auto">
          <Table variant="simple" size="sm" whiteSpace="nowrap">
            <Thead bg="teal.50">
              <Tr>
                <Th
                  position="sticky"
                  left={0}
                  bg="white"
                  zIndex={10}
                  borderRight="1px solid #ddd"
                  minWidth="60px"
                >
                  ID
                </Th>
                <Th
                  position="sticky"
                  left="60px"  // 第二欄貼齊第一欄寬度
                  bg="white"
                  zIndex={10}
                  borderRight="1px solid #ddd"
                  minWidth="100px" // 自行調整寬度
                >
                  股票代號
                </Th>
                <Th>模型類型</Th>
                {/* <Th>運行ID</Th> */}
                {showColumns.run_id && <Th>運行ID</Th>}
                {showColumns.train_size && <Th>訓練資料筆數</Th>}
                {showColumns.val_size && <Th>驗證資料筆數</Th>}
                {showColumns.percentage && <Th>percentage (%)</Th>}
                {showColumns.rmse && <Th>rmse </Th>}
                <Th>建立時間</Th>
                <Th>操作</Th>
              </Tr>
            </Thead>
            <Tbody>
              {models.map((model) => {
                const runId = model.run_id ?? 'N/A';
                const artifactUri = model.model_uri ?? 'N/A';
                const trainSize = model.metrics?.train_size ?? null;
                const valSize = model.metrics?.val_size ?? null;
                const percentage =
                  trainSize !== null && valSize !== null && valSize !== 0
                    ? (valSize / (valSize + trainSize)*100).toFixed(2)
                    : 'N/A';
                const rmse = model.metrics?.rmse.toFixed(2) ;

                return (
                  <Tr key={`${model.id}-${model.run_id}`} _hover={{ bg: "gray.50" }}>
                    <Td
                      position="sticky"
                      left={0}
                      bg="white"
                      zIndex={9}
                      borderRight="1px solid #ddd"
                      minWidth="60px"
                    >
                      {model.id}
                    </Td>
                    <Td
                      position="sticky"
                      left="60px"  // 跟表頭對齊
                      bg="white"
                      zIndex={9}
                      borderRight="1px solid #ddd"
                      minWidth="100px"
                    >
                      {model.ticker}
                    </Td>
                    <Td>{model.model_type || 'N/A'}</Td>
                    {/* <Td>{runId}</Td> */}
                    {showColumns.run_id && <Td>{runId}</Td>}

                    {showColumns.model_uri && <Td>{artifactUri}</Td>}
                    {showColumns.train_size && <Td>{trainSize !== null ? trainSize : 'N/A'}</Td>}
                    {showColumns.val_size && <Td>{valSize !== null ? valSize : 'N/A'}</Td>}
                    {showColumns.percentage && <Td>{percentage} % </Td>}
                    {showColumns.rmse && <Td>{rmse} </Td>}
                    <Td>{model.created_at ? new Date(model.created_at).toLocaleString() : 'N/A'}</Td>
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
                        onClick={() => openPredictModal(model)}
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
                );
              })}
            </Tbody>
          </Table>
        </TableContainer>

      )}

      <ModelDetailModal
        isOpen={isOpen}
        onClose={onClose}
        model={selectedModel}
      />
      <PredictDateModal
        isOpen={isPredictModalOpen}
        onClose={() => setPredictModalOpen(false)}
        model={modelToPredict}
        onSubmit={handlePredictSubmit}
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
