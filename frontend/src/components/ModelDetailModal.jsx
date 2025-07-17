// frontend/src/components/ModelDetailModal.jsx
import React from 'react';
import {
  Box, Text,
  Modal, ModalOverlay, ModalContent, ModalHeader,
  ModalCloseButton, ModalBody, ModalFooter, Button,
} from '@chakra-ui/react';

export default function ModelDetailModal({ isOpen, onClose, model }) {
  if (!model) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent rounded="lg" shadow="xl">
        <ModalHeader bg="teal.500" color="white" roundedTop="lg">模型詳情</ModalHeader>
        <ModalCloseButton color="white" />
        <ModalBody p={6}>
          <Box>
            <Text mb={2}><Text as="span" fontWeight="bold">ID:</Text> {model.id}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">股票代號:</Text> {model.ticker}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">運行ID:</Text> {model.run_id}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">模型URI:</Text> {model.model_uri}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">特徵:</Text> {(model.features || []).join(', ')}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">模型類型:</Text> {model.model_type || 'N/A'}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">是否打亂數據:</Text> {model.shuffle ? '是' : '否'}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">建立時間:</Text> {new Date(model.created_at).toLocaleString()}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">訓練開始日期:</Text> {model.train_start_date ? new Date(model.train_start_date).toLocaleDateString() : 'N/A'}</Text>
            <Text mb={2}><Text as="span" fontWeight="bold">訓練結束日期:</Text> {model.train_end_date ? new Date(model.train_end_date).toLocaleDateString() : 'N/A'}</Text>
          </Box>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" onClick={onClose} rounded="full">關閉</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
