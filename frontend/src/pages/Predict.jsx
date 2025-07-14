import { useState } from 'react'
import axios from 'axios'
import {
    Box,
    Heading,
    Input,
    Button,
    Code,
    VStack,
} from '@chakra-ui/react'

export default function Predict() {
    const [ticker, setTicker] = useState('')
    const [exchange, setExchange] = useState('US')
    const [targetDate, setTargetDate] = useState('')
    const [result, setResult] = useState(null)

    const handlePredict = async () => {
        try {
            const response = await axios.post('http://localhost:8001/api/predict', {
                ticker,
                exchange,
                target_date: targetDate,
            })
            setResult(response.data)
        } catch (err) {
            console.error(err)
            alert('預測失敗')
        }
    }

    return (
        <Box p={6}>
            <Heading as="h2" size="lg" mb={4}>
                🔮 股票預測
            </Heading>
            <VStack spacing={4} align="stretch" maxW="400px">
                <Input
                    placeholder="輸入股票代號 (ex: AAPL)"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                />
                <Input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                />
                <Input
                    placeholder="交易所 (ex: US)"
                    value={exchange}
                    onChange={(e) => setExchange(e.target.value)}
                />
                <Button colorScheme="blue" onClick={handlePredict}>
                    預測收盤價
                </Button>
            </VStack>

            {result && (
                <Box mt={6} maxW="600px">
                    <Heading as="h3" size="md" mb={2}>
                        📊 預測結果
                    </Heading>
                    <Code
                        p={4}
                        w="100%"
                        whiteSpace="pre-wrap"
                        children={JSON.stringify(result, null, 2)}
                    />
                </Box>
            )}
        </Box>
    )
}
