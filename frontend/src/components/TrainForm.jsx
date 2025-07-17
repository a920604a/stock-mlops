import { useState } from 'react'
import axios from 'axios'
import {
  Box, Heading, Input, Button, VStack, Alert, AlertIcon, Text, Checkbox, CheckboxGroup, Stack,
  FormControl, FormLabel, Select
} from '@chakra-ui/react'

export default function TrainForm() {
  const [ticker, setTicker] = useState('')
  const [exchange, setExchange] = useState('US')

  // config states
  const [modelType, setModelType] = useState('random_forest')
  const [featureColumns, setFeatureColumns] = useState([]) // array of strings
  const [shuffle, setShuffle] = useState(false)
  const [nEstimators, setNEstimators] = useState(100)
  const [trainStartTime, setTrainStartTime] = useState('')
  const [trainEndTime, setTrainEndTime] = useState('')

  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  // 常見特徵欄位範例，讓使用者可以選擇
  const allFeatures = [
    'MA5', 'MA10', 'EMA12', 'EMA26', 'MACD', 'RSI', 'Volume'
  ]

  const handleFeatureChange = (values) => {
    setFeatureColumns(values)
  }

  const handleTrain = async () => {
    setError(null)
    setStatus(null)

    if (!ticker) {
      setError('請輸入股票代號')
      return
    }
    if (!exchange) {
      setError('請輸入交易所')
      return
    }
    if (!trainStartTime || !trainEndTime) {
      setError('請選擇訓練起訖時間')
      return
    }

    try {
      const res = await axios.post('http://localhost:8001/api/train', {
        ticker,
        exchange,
        config: {
          model_type: modelType,
          feature_columns: featureColumns,
          shuffle,
          n_estimators: nEstimators,
          train_start_date: trainStartTime,
          train_end_date: trainEndTime,
        }
      })
      setStatus({ task_id: res.data.task_id, message: '訓練任務已提交' })

       // 清空欄位
      setTicker('')
      setExchange('US')
      setModelType('random_forest')
      setFeatureColumns([])
      setShuffle(false)
      setNEstimators(100)
      setTrainStartTime('')
      setTrainEndTime('')

    } catch (err) {
      setError(err.response?.data?.detail || '訓練提交失敗')
    }
  }

  return (
    <Box p={6} maxW="md" mx="auto">
      <Heading size="lg" mb={6}>️ 模型訓練</Heading>

      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>股票代號</FormLabel>
          <Input
            placeholder="ex: AAPL"
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
          />
        </FormControl>

        <FormControl>
          <FormLabel>交易所</FormLabel>
          <Input
            placeholder="ex: US"
            value={exchange}
            onChange={e => setExchange(e.target.value.toUpperCase())}
          />
        </FormControl>

        <FormControl>
          <FormLabel>模型類型</FormLabel>
          <Select value={modelType} onChange={e => setModelType(e.target.value)}>
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
          >
            <Stack spacing={1} direction="column">
              {allFeatures.map(f => (
                <Checkbox key={f} value={f}>{f}</Checkbox>
              ))}
            </Stack>
          </CheckboxGroup>
        </FormControl>

        <FormControl display="flex" alignItems="center">
          <Checkbox
            isChecked={shuffle}
            onChange={e => setShuffle(e.target.checked)}
          >
            資料洗牌 (Shuffle)
          </Checkbox>
        </FormControl>

        <FormControl>
          <FormLabel>樹的數量 (n_estimators)</FormLabel>
          <Input
            type="number"
            min={1}
            value={nEstimators}
            onChange={e => setNEstimators(parseInt(e.target.value) || 100)}
          />
        </FormControl>

        <FormControl>
          <FormLabel>訓練起始時間</FormLabel>
          <Input
            type="date"
            value={trainStartTime}
            onChange={e => setTrainStartTime(e.target.value)}
          />
        </FormControl>

        <FormControl>
          <FormLabel>訓練結束時間</FormLabel>
          <Input
            type="date"
            value={trainEndTime}
            onChange={e => setTrainEndTime(e.target.value)}
          />
        </FormControl>

        <Button colorScheme="green" onClick={handleTrain}>提交訓練任務</Button>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {status && (
          <Box bg="gray.100" p={4} borderRadius="md" mt={4}>
            <Text>{status.message}</Text>
            <Text>任務 ID：{status.task_id}</Text>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
