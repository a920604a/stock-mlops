import { useState } from 'react'
import {
  Box, Heading, Input, Button, VStack, Alert, AlertIcon, Text, Checkbox, CheckboxGroup, Stack,
  FormControl, FormLabel, Select
} from '@chakra-ui/react'

export default function ModelRegisterForm({ showToast }) {
  const [ticker, setTicker] = useState('')
  const [exchange, setExchange] = useState('US')

  // config states
  const [modelType, setModelType] = useState('random_forest')
  const [featureColumns, setFeatureColumns] = useState([]) // array of strings

  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  // 常見特徵欄位範例，讓使用者可以選擇
  const allFeatures = [
    'MA5', 'MA10', 'EMA12', 'EMA26', 'MACD', 'RSI', 'Volume'
  ]

  const handleFeatureChange = (values) => {
    setFeatureColumns(values)
  }

  const handleRegister = async () => {
    setError(null)
    setStatus(null)
    setLoading(true)

    if (!ticker) {
      setError('請輸入股票代號')
      setLoading(false)
      return
    }
    if (!exchange) {
      setError('請輸入交易所')
      setLoading(false)
      return
    }

    try {
      // 模擬 API 呼叫，2 秒後回傳成功
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 假設後端回傳 modelId 與訊息
      const fakeModelId = Math.floor(Math.random() * 10000)
      setStatus({ modelId: fakeModelId, message: '模型註冊成功' })

      showToast && showToast('成功', '模型註冊成功', 'success')

      // 清空欄位
      setTicker('')
      setExchange('US')
      setModelType('random_forest')
      setFeatureColumns([])

    } catch (err) {
      setError('模型註冊失敗')
      showToast && showToast('錯誤', '模型註冊失敗', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box p={6} maxW="md" mx="auto">
      <Heading size="lg" mb={6}>➕ 模型註冊</Heading>

      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>股票代號</FormLabel>
          <Input
            placeholder="ex: AAPL"
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            isDisabled={loading}
          />
        </FormControl>

        <FormControl>
          <FormLabel>交易所</FormLabel>
          <Input
            placeholder="ex: US"
            value={exchange}
            onChange={e => setExchange(e.target.value.toUpperCase())}
            isDisabled={loading}
          />
        </FormControl>

        <FormControl>
          <FormLabel>模型類型</FormLabel>
          <Select
            value={modelType}
            onChange={e => setModelType(e.target.value)}
            isDisabled={loading}
          >
            <option value="random_forest">Random Forest</option>
            <option value="xgboost">XGBoost</option>
            <option value="linear_regression">Linear Regression</option>
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel>特徵欄位 (Feature Columns)</FormLabel>
          <CheckboxGroup
            colorScheme="green"
            value={featureColumns}
            onChange={handleFeatureChange}
            isDisabled={loading}
          >
            <Stack spacing={1} direction="column">
              {allFeatures.map(f => (
                <Checkbox key={f} value={f}>{f}</Checkbox>
              ))}
            </Stack>
          </CheckboxGroup>
        </FormControl>

        <Button
          colorScheme="blue"
          onClick={handleRegister}
          isLoading={loading}
          loadingText="註冊中"
        >
          提交模型註冊
        </Button>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {status && (
          <Box bg="gray.100" p={4} borderRadius="md" mt={4}>
            <Text>{status.message}</Text>
            <Text>模型 ID：{status.modelId}</Text>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
