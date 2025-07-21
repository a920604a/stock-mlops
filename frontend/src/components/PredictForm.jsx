import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Box, Heading, Input, Button, VStack, Alert, AlertIcon, useToast, List, ListItem
} from '@chakra-ui/react'

export default function PredictForm() {
  const [ticker, setTicker] = useState('')
  const [exchange, setExchange] = useState('US')
  const [targetDate, setTargetDate] = useState('')
  const [error, setError] = useState(null)
  const [predictions, setPredictions] = useState([]) // 新增狀態儲存 WebSocket 資料
  const toast = useToast() // 使用 Chakra UI toast

  // WebSocket 連線，接收即時推播結果
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8010/ws/predictions")

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      // 新資料放最前面
      setPredictions(prev => [data, ...prev])

      // Toast 通知
      toast({
        title: `股票 ${data.ticker} 新預測`,
        description: `預測收盤價: ${data.predicted_close}，實際: ${data.actual_close ?? "無資料"}`,
        status: "info",
        duration: 3000,
        isClosable: true,
        position: "top-right",
      })
    }

    ws.onerror = (err) => {
      console.error("WebSocket 發生錯誤", err)
    }

    return () => {
      ws.close()
    }
  }, [toast])

  const handlePredict = async () => {
    setError(null)
    try {
      await axios.post('http://localhost:8001/api/predict', {
        ticker,
        exchange,
        target_date: targetDate,
      })
    } catch (err) {
      setError(err.response?.data?.detail || '預測失敗')
    }
  }

  return (
    <Box p={6} maxW="md" mx="auto">
      <Heading size="lg" mb={4}>🔮 股票預測</Heading>

      <VStack spacing={3} mb={4}>
        <Input
          placeholder="股票代號 (ex: AAPL)"
          value={ticker}
          onChange={e => setTicker(e.target.value.toUpperCase())}
        />
        <Input
          placeholder="交易所 (ex: US)"
          value={exchange}
          onChange={e => setExchange(e.target.value.toUpperCase())}
        />
        <Input
          type="date"
          value={targetDate}
          onChange={e => setTargetDate(e.target.value)}
        />
        <Button colorScheme="blue" onClick={handlePredict}>開始預測</Button>
      </VStack>

      {error && (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error}
        </Alert>
      )}

      {/* 顯示從 WebSocket 收到的預測結果 */}
      <Box>
        <Heading size="md" mb={2}>即時預測結果</Heading>
        <List spacing={2}>
          {predictions.map((p, idx) => (
            <ListItem key={idx}>
              {p.ticker} - 預測收盤價: {p.predicted_close} - 實際: {p.actual_close ?? "無資料"}
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  )
}
