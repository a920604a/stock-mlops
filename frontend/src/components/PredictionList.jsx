// frontend/src/components/PredictionList.jsx
import React, { useEffect, useState } from 'react';
import {
  Box, Table, Thead, Tbody, Tr, Th, Td, TableContainer,
  Spinner, Alert, AlertIcon, Text, Flex,
} from '@chakra-ui/react';
import { fetchPredictionRecords } from '../api/predictions';  // 後端 API 呼叫


export default function PredictionList({ showToast }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPredictionRecords();
      setRecords(data);
    } catch (err) {
      setError('無法取得預測紀錄。');
      showToast && showToast('錯誤', '無法取得預測紀錄。', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecords();
  }, []);

  if (loading) {
    return (
      <Flex justify="center" align="center" height="200px">
        <Spinner size="xl" color="teal.500" />
        <Text ml={4}>加載預測紀錄中...</Text>
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

  if (records.length === 0) {
    return <Text>目前沒有預測紀錄。</Text>;
  }

  return (
    <Box>
      <TableContainer border="1px" borderColor="gray.200" rounded="md" shadow="sm" maxWidth="100%" overflowX="auto">
        <Table variant="simple" size="sm" whiteSpace="nowrap">
          <Thead bg="teal.50">
            <Tr>
              <Th>股票代號</Th>
              <Th>目標日期</Th>
              <Th>預測收盤價</Th>
              <Th>預測時間</Th>
              <Th>模型ID</Th>
            </Tr>
          </Thead>
          <Tbody>
            {records.map((rec, idx) => (
              <Tr key={`${rec.ticker}-${rec.target_date}-${idx}`}>
                <Td>{rec.ticker}</Td>
                <Td>{new Date(rec.target_date).toLocaleDateString()}</Td>
                <Td>{rec.predicted_close.toFixed(2)}</Td>
                <Td>{new Date(rec.predicted_at).toLocaleString()}</Td>
                <Td>{rec.model_metadata_id}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </Box>
  );
}
