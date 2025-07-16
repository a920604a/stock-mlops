import {
  Box, Heading, Table, Thead, Tr, Th, Tbody, Td,
  Spinner, Text, useToast, Button, Input, HStack, VStack, List, ListItem, CloseButton
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { fetchDatasets, insertETL } from '../api/datasets'
import axios from 'axios'

export default function Datasets() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)

  const [tickerInput, setTickerInput] = useState('')
  const [exchangeInput, setExchangeInput] = useState('')
  const [etlList, setEtlList] = useState([]) // {ticker, exchange} 陣列

  const toast = useToast()

  // 載入現有資料集
  const loadDatasets = async () => {
    setLoading(true)
    try {
      const data = await fetchDatasets()
      setDatasets(data)
    } catch (err) {
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

  // 新增輸入的 ticker & exchange 到 ETL 清單
  const addToEtlList = () => {
    if (!tickerInput.trim() || !exchangeInput.trim()) {
      toast({
        title: '請輸入完整的 Ticker 與 Exchange',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      })
      return
    }

    // 避免重複加入同樣的 ticker-exchange
    const exists = etlList.some(
      item =>
        item.ticker.toUpperCase() === tickerInput.toUpperCase() &&
        item.exchange.toUpperCase() === exchangeInput.toUpperCase()
    )
    if (exists) {
      toast({
        title: '該股票已在 ETL 清單中',
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
      return
    }

    setEtlList(prev => [
      ...prev,
      { ticker: tickerInput.toUpperCase(), exchange: exchangeInput.toUpperCase() },
    ])

    // 清空輸入框
    setTickerInput('')
    setExchangeInput('')
  }

  // 從 ETL 清單移除項目
  const removeFromEtlList = (index) => {
    setEtlList(prev => prev.filter((_, i) => i !== index))
  }

  // 觸發 ETL API
  const triggerETL = async () => {
    try {
      const res = await insertETL(etlList)
      toast({
        title: '✅ ETL 任務已觸發',
        description: res.message || '執行成功',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

      // ✅ 清空清單與表單
      setEtlList([])
      setTickerInput('')
      setExchangeInput('')
    } catch (err) {
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

      {/* 輸入欄位 */}
      <HStack mb={4}>
        <Input
          placeholder="Ticker (例如 AAPL)"
          value={tickerInput}
          onChange={e => setTickerInput(e.target.value)}
          maxW="150px"
          textTransform="uppercase"
        />
        <Input
          placeholder="Exchange (例如 US)"
          value={exchangeInput}
          onChange={e => setExchangeInput(e.target.value)}
          maxW="100px"
          textTransform="uppercase"
        />
        <Button onClick={addToEtlList} colorScheme="blue">
          新增到 ETL 清單
        </Button>
      </HStack>

      {/* 顯示 ETL 清單 */}
      {etlList.length > 0 && (
        <Box mb={4}>
          <Heading size="md" mb={2}>待執行 ETL 的股票</Heading>
          <List spacing={2}>
            {etlList.map((item, idx) => (
              <ListItem
                key={idx}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                p={2}
              >
                <Box>
                  {item.ticker} / {item.exchange}
                </Box>
                <CloseButton onClick={() => removeFromEtlList(idx)} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* 執行 ETL 按鈕 */}
      <Button
        onClick={triggerETL}
        colorScheme="teal"
        size="md"
        mb={6}
        isDisabled={etlList.length === 0}
      >
        🚀 執行資料擷取（ETL）
      </Button>

      {/* 顯示資料集表格或提示 */}
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
