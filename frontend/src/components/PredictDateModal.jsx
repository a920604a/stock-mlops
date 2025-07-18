// components/PredictDateModal.jsx
import React, { useState } from 'react';
import {
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalCloseButton,
  ModalBody, ModalFooter, Button, Input, FormControl, FormLabel
} from '@chakra-ui/react';

export default function PredictDateModal({ isOpen, onClose, onSubmit, model }) {
  const [targetDate, setTargetDate] = useState('');

  const handleConfirm = () => {
    if (targetDate) {
      onSubmit(model, targetDate);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>預測模型（ID: {model?.id}）</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <FormControl>
            <FormLabel>請選擇預測日期</FormLabel>
            <Input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
            />
          </FormControl>
        </ModalBody>
        <ModalFooter>
          <Button onClick={onClose} mr={3}>取消</Button>
          <Button colorScheme="teal" onClick={handleConfirm}>送出預測</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
