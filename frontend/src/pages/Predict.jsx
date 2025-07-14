import { useState } from 'react'
import axios from 'axios'
import {
    Box, Heading, Input, Button, Text, VStack, Alert, AlertIcon,
} from '@chakra-ui/react'

export default function Predict() {
    const [ticker, setTicker] = useState('')
    const [exchange, setExchange] = useState('US')
    const [targetDate, setTargetDate] = useState('')
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)

    const handlePredict = async () => {
        setError(null)
        setResult(null)
        console.log(ticker)
        console.log(exchange)
        console.log(targetDate)
        try {
            const res = await axios.post('http://localhost:8001/api/predict', {
                ticker,
                exchange,
                target_date: targetDate,
            })
            setResult(res.data)
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

            {result && (
                <Box bg="gray.100" p={4} borderRadius="md">
                    <Text><b>股票代號：</b>{result.ticker}</Text>
                    <Text><b>交易所：</b>{result.exchange}</Text>
                    <Text><b>目標日期：</b>{new Date(result.target_date).toLocaleDateString()}</Text>
                    <Text><b>預測收盤價：</b>{result.predicted_close.toFixed(2)}</Text>
                    <Text><b>實際收盤價：</b>{result.actual_close !== null ? result.actual_close.toFixed(2) : '無資料'}</Text>
                    <Text><b>預測時間：</b>{new Date(result.predicted_at).toLocaleString()}</Text>
                    {result.msg && <Text mt={2} color="gray.600">{result.msg}</Text>}
                </Box>
            )}
        </Box>
    )
}
