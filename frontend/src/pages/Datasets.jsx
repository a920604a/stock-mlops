import {
  Box, Heading, Table, Thead, Tr, Th, Tbody, Td,
  Spinner, Text,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { fetchDatasets } from '../api/datasets'

export default function Datasets() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)

  const loadDatasets = async () => {
    setLoading(true)
    try {
      const data = await fetchDatasets()
      setDatasets(data)
    } catch (err) {
      console.error('❌ 載入資料集失敗', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  return (
    <Box p={6}>
      <Heading size="lg" mb={4}>📊 資料集概況</Heading>

      {loading ? (
        <Spinner />
      ) : datasets.length === 0 ? (
        <Text>目前尚無資料集紀錄。</Text>
      ) : (
        <Table variant="simple" size="sm">
          <Thead bg="gray.100">
            <Tr>
              <Th>Ticker</Th>
              <Th>Exchange</Th>
              <Th>期間</Th>
              <Th>資料筆數</Th>
              <Th>已轉檔</Th>
            </Tr>
          </Thead>
          <Tbody>
            {datasets.map((d, idx) => (
              <Tr key={idx}>
                <Td>{d.ticker}</Td>
                <Td>{d.exchange}</Td>
                <Td>{d.start_date} ~ {d.end_date}</Td>
                <Td>{d.count}</Td>
                <Td>{d.parquet_ready ? '✅' : '❌'}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  )
}
