// components/DeleteConfirmDialog.jsx
import {
  AlertDialog, AlertDialogOverlay, AlertDialogContent,
  AlertDialogHeader, AlertDialogBody, AlertDialogFooter,
  Button
} from '@chakra-ui/react';
import { useRef } from 'react';

export default function DeleteConfirmDialog({ isOpen, onClose, onConfirm, itemName }) {
  const cancelRef = useRef();

  return (
    <AlertDialog
      isOpen={isOpen}
      leastDestructiveRef={cancelRef}
      onClose={onClose}
    >
      <AlertDialogOverlay>
        <AlertDialogContent>
          <AlertDialogHeader fontSize="lg" fontWeight="bold">
            刪除確認
          </AlertDialogHeader>

          <AlertDialogBody>
            確定要刪除 {itemName} 嗎？此操作無法復原。
          </AlertDialogBody>

          <AlertDialogFooter>
            <Button ref={cancelRef} onClick={onClose}>
              取消
            </Button>
            <Button colorScheme="red" onClick={onConfirm} ml={3}>
              確定刪除
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
}
