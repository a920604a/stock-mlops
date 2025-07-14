import { useState } from 'react'
import axios from 'axios'
import { Box, Heading, Input, Button, Text, Code, VStack } from '@chakra-ui/react'

export default function Train() {
    const [ticker, setTicker] = useState('')
    const [exchange, setExchange] = useState('US')
    const [status, setStatus] = useState(null)

    const handleTrain = async () => {
        try {
            const res = await axios.post('http://localhost:8001/api/train', {
                ticker,
                exchange,
            })
            setStatus(res.data)
        } catch (err) {
            console.error(err)
            alert('訓練失敗')
        }
    }

    return (
        <Box p={6}>
            <Heading as="h2" size="lg" mb={4}>
                🛠️ 模型訓練
            </Heading>
            <VStack spacing={4} align="stretch" maxW="400px">
                <Input
                    placeholder="輸入股票代號 (ex: AAPL)"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                />
                <Input
                    placeholder="交易所 (ex: US)"
                    value={exchange}
                    onChange={(e) => setExchange(e.target.value)}
                />
                <Button colorScheme="green" onClick={handleTrain}>
                    啟動訓練任務
                </Button>
            </VStack>

            {status && (
                <Box mt={6} maxW="600px">
                    <Heading as="h3" size="md" mb={2}>
                        ✅ 任務結果
                    </Heading>
                    <Code
                        p={4}
                        w="100%"
                        whiteSpace="pre-wrap"
                        children={JSON.stringify(status, null, 2)}
                    />
                </Box>
            )}
        </Box>
    )
}
