import { useState } from 'react'
import axios from 'axios'
import {
    Box, Heading, Input, Button, VStack, Alert, AlertIcon, Text,
} from '@chakra-ui/react'

export default function Train() {
    const [ticker, setTicker] = useState('')
    const [exchange, setExchange] = useState('US')
    const [status, setStatus] = useState(null)
    const [error, setError] = useState(null)

    const handleTrain = async () => {
        setError(null)
        setStatus(null)
        try {
            const res = await axios.post('http://localhost:8001/api/train', {
                ticker,
                exchange,
                config: {}, // 可以先空物件或依後端需求調整
            })
            setStatus({ task_id: res.data.task_id, message: '訓練任務已提交' })
        } catch (err) {
            setError(err.response?.data?.detail || '訓練提交失敗')
        }
    }

    return (
        <Box p={6} maxW="md" mx="auto">
            <Heading size="lg" mb={4}>🛠️ 模型訓練</Heading>

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
                <Button colorScheme="green" onClick={handleTrain}>提交訓練任務</Button>
            </VStack>

            {error && (
                <Alert status="error" mb={4}>
                    <AlertIcon />
                    {error}
                </Alert>
            )}

            {status && (
                <Box bg="gray.100" p={4} borderRadius="md">
                    <Text>{status.message}</Text>
                    <Text>任務 ID：{status.task_id}</Text>
                </Box>
            )}
        </Box>
    )
}
