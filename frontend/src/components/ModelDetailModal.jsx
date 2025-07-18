// frontend/src/components/ModelDetailModal.jsx
import React from 'react';
import {
  Box, Text, Stack, Divider,
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalCloseButton, ModalBody, ModalFooter, Button,
} from '@chakra-ui/react';

export default function ModelDetailModal({ isOpen, onClose, model }) {
  if (!model) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent rounded="lg" shadow="xl" maxH="80vh">
        <ModalHeader bg="teal.600" color="white" roundedTop="lg" fontWeight="extrabold" fontSize="xl">
          模型詳情
        </ModalHeader>
        <ModalCloseButton color="white" />
        <ModalBody p={6}>
          <Stack spacing={4} fontSize="md" color="gray.700">
            <Box>
              <Text><Text as="span" fontWeight="bold" mr={2}>ID:</Text> {model.id}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>股票代號:</Text> {model.ticker}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>交易所:</Text> {model.exchange}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>模型類型:</Text> {model.model_type || 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>特徵:</Text> {(model.features || []).join(', ')}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>訓練開始日期:</Text> {model.train_start_date ? new Date(model.train_start_date).toLocaleDateString() : 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>訓練結束日期:</Text> {model.train_end_date ? new Date(model.train_end_date).toLocaleDateString() : 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>是否打亂數據:</Text> {model.params?.shuffle ? '是' : '否'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>運行ID:</Text> {model.run_id || '尚未訓練'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>模型URI:</Text> {model.artifact_uri || '尚未訓練'}</Text>
            </Box>

            <Divider />

            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={2} color="teal.600">訓練結果</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>RMSE:</Text> {model.metrics?.rmse ?? 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>訓練筆數:</Text> {model.metrics?.train_size ?? 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>驗證筆數:</Text> {model.metrics?.val_size ?? 'N/A'}</Text>
            </Box>

            <Divider />

            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={2} color="teal.600">訓練參數</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>n_estimators:</Text> {model.params?.n_estimators ?? 'N/A'}</Text>
              <Text><Text as="span" fontWeight="bold" mr={2}>模型類型:</Text> {model.params?.model_type ?? 'N/A'}</Text>
            </Box>
          </Stack>
        </ModalBody>
        <ModalFooter bg="gray.50" borderTop="1px" borderColor="gray.200">
          <Button colorScheme="teal" onClick={onClose} rounded="full" fontWeight="semibold" px={6}>
            關閉
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
