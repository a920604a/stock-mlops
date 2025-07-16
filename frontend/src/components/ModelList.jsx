// frontend/src/components/ModelList.jsx
import React, { useEffect, useState } from 'react';
// 導入新的 API 函數
import { getModels, deleteModelById } from '../api/model';
import {
    Box, Table, Thead, Tbody, Tr, Th, Td, TableContainer,
    Spinner, Alert, AlertIcon, Button, IconButton, Text, Flex,
    Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
    useDisclosure,
} from '@chakra-ui/react';
import { DeleteIcon, ViewIcon } from '@chakra-ui/icons';

// API_BASE_URL 不再需要在此文件中定義，因為它已移至 api/models.js

export default function ModelList({ showToast }) {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedModel, setSelectedModel] = useState(null);
    const { isOpen, onOpen, onClose } = useDisclosure(); // For the detail modal
    const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure(); // For delete confirmation modal
    const [modelToDelete, setModelToDelete] = useState(null);

    // Function to fetch models from the backend
    const fetchModels = async () => {
        setLoading(true);
        setError(null);
        try {
            // 調用新的 API 函數
            const data = await getModels();
            setModels(data);
        } catch (err) {
            console.error("獲取模型列表失敗:", err);
            setError("無法加載模型列表。請檢查後端服務是否運行。");
            showToast("錯誤", "無法加載模型列表。", "error");
        } finally {
            setLoading(false);
        }
    };

    // Fetch models when the component mounts
    useEffect(() => {
        fetchModels();
    }, []);

    // Handle view details button click
    const handleViewDetails = (model) => {
        setSelectedModel(model);
        onOpen(); // Open the detail modal
    };

    // Handle delete button click (opens confirmation modal)
    const handleDeleteClick = (model) => {
        setModelToDelete(model);
        onDeleteOpen(); // Open the delete confirmation modal
    };

    // Handle actual deletion after confirmation
    const confirmDelete = async () => {
        if (!modelToDelete) return;

        try {
            // 調用新的 API 函數
            await deleteModelById(modelToDelete.id);
            showToast("成功", `模型 ID: ${modelToDelete.id} 已成功刪除。`, "success");
            fetchModels(); // Refresh the list after deletion
            onDeleteClose(); // Close the confirmation modal
        } catch (err) {
            console.error("刪除模型失敗:", err);
            setError(`刪除模型 ID: ${modelToDelete.id} 失敗。`);
            showToast("錯誤", `刪除模型 ID: ${modelToDelete.id} 失敗。`, "error");
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

            {/* Model Detail Modal */}
            <Modal isOpen={isOpen} onClose={onClose} size="xl">
                <ModalOverlay />
                <ModalContent rounded="lg" shadow="xl">
                    <ModalHeader bg="teal.500" color="white" roundedTop="lg">模型詳情</ModalHeader>
                    <ModalCloseButton color="white" />
                    <ModalBody p={6}>
                        {selectedModel && (
                            <Box>
                                <Text mb={2}><Text as="span" fontWeight="bold">ID:</Text> {selectedModel.id}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">股票代號:</Text> {selectedModel.ticker}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">運行ID:</Text> {selectedModel.run_id}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">模型URI:</Text> {selectedModel.model_uri}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">特徵:</Text> {selectedModel.features.join(', ')}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">模型類型:</Text> {selectedModel.model_type || 'N/A'}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">是否打亂數據:</Text> {selectedModel.shuffle ? '是' : '否'}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">建立時間:</Text> {new Date(selectedModel.created_at).toLocaleString()}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">訓練開始日期:</Text> {selectedModel.train_start_date ? new Date(selectedModel.train_start_date).toLocaleDateString() : 'N/A'}</Text>
                                <Text mb={2}><Text as="span" fontWeight="bold">訓練結束日期:</Text> {selectedModel.train_end_date ? new Date(selectedModel.train_end_date).toLocaleDateString() : 'N/A'}</Text>
                            </Box>
                        )}
                    </ModalBody>
                    <ModalFooter>
                        <Button colorScheme="blue" onClick={onClose} rounded="full">關閉</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal isOpen={isDeleteOpen} onClose={onDeleteClose}>
                <ModalOverlay />
                <ModalContent rounded="lg" shadow="xl">
                    <ModalHeader bg="red.500" color="white" roundedTop="lg">確認刪除</ModalHeader>
                    <ModalCloseButton color="white" />
                    <ModalBody p={6}>
                        <Text>您確定要刪除模型 <Text as="span" fontWeight="bold">{modelToDelete?.run_id}</Text> (ID: {modelToDelete?.id}) 嗎？此操作無法撤銷。</Text>
                    </ModalBody>
                    <ModalFooter>
                        <Button variant="ghost" onClick={onDeleteClose} mr={3} rounded="full">取消</Button>
                        <Button colorScheme="red" onClick={confirmDelete} rounded="full">確認刪除</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </Box>
    );
}
