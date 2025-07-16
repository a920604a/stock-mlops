import {
  Box, Heading, Table, Thead, Tr, Th, Tbody, Td,
  Spinner, Text, useToast, Button
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { fetchDatasets } from '../api/datasets'
import axios from 'axios'

export default function Datasets() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)
  const toast = useToast()  // ✅ 初始化 toast

  const loadDatasets = async () => {
    setLoading(true)
    try {
      const data = await fetchDatasets()
      setDatasets(data)
    } catch (err) {
      console.error('❌ 載入資料集失敗', err)
      toast({
        title: '資料集載入失敗',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const triggerETL = async () => {
    try {
      await axios.post('/api/run-etl', [
        { ticker: 'AAPL', exchange: 'US' },
        { ticker: 'TSM', exchange: 'US' },
        { ticker: '2330.TW', exchange: 'TW' },
      ])
      toast({
        title: '✅ ETL 任務已觸發',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      // 3 秒後自動重新載入
      setTimeout(() => {
        loadDatasets()
      }, 3000)

    } catch (err) {
      console.error('❌ 觸發 ETL 失敗', err)
      toast({
        title: 'ETL 觸發失敗',
        description: err?.response?.data?.detail || '伺服器錯誤',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  return (
    <Box p={6}>
      <Heading size="lg" mb={4}>📊 資料集概況</Heading>

      {/* ✅ 加上觸發 ETL 按鈕 */}
      <Button onClick={triggerETL} colorScheme="teal" size="sm" mb={4}>
        🚀 執行資料擷取（ETL）
      </Button>

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
