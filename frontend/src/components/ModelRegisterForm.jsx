import { useState } from 'react'
import {
  Box, Heading, Input, Button, VStack, Alert, AlertIcon, Text, Checkbox, CheckboxGroup, Stack,
  FormControl, FormLabel, Select, Checkbox as ChakraCheckbox
} from '@chakra-ui/react'
import { createModel } from '../api/model' // 根據你的實際檔案路徑調整


export default function ModelRegisterForm({ showToast }) {
  const [ticker, setTicker] = useState('')
  const [exchange, setExchange] = useState('US')

  // config states
  const [modelType, setModelType] = useState('random_forest')
  const [featureColumns, setFeatureColumns] = useState([]) // array of strings
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
    const [shuffle, setShuffle] = useState(true)  // 新增 shuffle state，預設 true


  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  // 常見特徵欄位範例
  const allFeatures = ['MA5', 'MA10', 'EMA12', 'EMA26', 'MACD', 'RSI', 'Volume']

  // 取得今天日期(yyyy-MM-dd)
  const today = new Date().toISOString().split('T')[0]

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
    if (!startDate || !endDate) {
      setError('請選擇訓練起始及結束日期')
      setLoading(false)
      return
    }
    if (new Date(startDate) > new Date(endDate)) {
      setError('訓練起始日期不能晚於結束日期')
      setLoading(false)
      return
    }
    if (new Date(endDate) > new Date(today)) {
      setError('訓練結束日期不能晚於今天')
      setLoading(false)
      return
    }

    try {

      const payload = {
        ticker,
        exchange,
        model_type: modelType,
        features: featureColumns,
        train_start_date: startDate,
        train_end_date: endDate,
        shuffle: shuffle,
      }
      console.log("payload", payload)
      const data = await createModel(payload)
      setStatus({ modelId: data.id, message: '模型註冊成功' })

      showToast && showToast('成功', '模型註冊成功', 'success')

      // 清空欄位
      // setTicker('')
      // setExchange('US')
      // setModelType('random_forest')
      // setFeatureColumns([])
      // setStartDate('')
      // setEndDate('')
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

        <FormControl>
          <FormLabel>訓練起始日期</FormLabel>
          <Input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            isDisabled={loading}
          />
        </FormControl>

        <FormControl>
          <FormLabel>訓練結束日期</FormLabel>
          <Input
            type="date"
            value={endDate}
            onChange={e => setEndDate(e.target.value)}
            isDisabled={loading}
            max={today}
          />
        </FormControl>

        <FormControl>
          <FormLabel>是否打亂訓練數據 (Shuffle)</FormLabel>
          <ChakraCheckbox
            isChecked={shuffle}
            onChange={e => setShuffle(e.target.checked)}
            isDisabled={loading}
          >
            打亂數據
          </ChakraCheckbox>
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
