import { useEffect, useState } from 'react'
import axios from 'axios'
import {
    Box,
    Heading,
    Table,
    Thead,
    Tbody,   // 注意這裡是大寫 T 小寫 b
    Tr,
    Th,
    Td,
    Button,
    Spinner,
    Text,
} from '@chakra-ui/react'


export default function Models() {
    const [models, setModels] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        axios
            .get('http://localhost:8001/api/models') // 後端 API 路徑
            .then((res) => {
                setModels(res.data)
            })
            .catch(() => {
                alert('讀取模型清單失敗')
            })
            .finally(() => setLoading(false))
    }, [])

    if (loading) {
        return (
            <Box textAlign="center" mt="20">
                <Spinner size="xl" />
                <Text mt="4">模型資料載入中...</Text>
            </Box>
        )
    }

    return (
        <Box p="6">
            <Heading size="lg" mb="6">
                📦 已訓練模型管理
            </Heading>
            <Table variant="simple" size="md" borderWidth="1px" borderRadius="md">
                <Thead bg="gray.100">
                    <Tr>
                        <Th>Ticker</Th>
                        <Th>Exchange</Th>
                        <Th>訓練時間</Th>
                        <Th>RMSE</Th>
                        <Th>操作</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {models.map((model, idx) => (
                        <Tr key={idx} _hover={{ bg: 'gray.50' }}>
                            <Td>{model.ticker}</Td>
                            <Td>{model.exchange}</Td>
                            <Td>{new Date(model.trained_at).toLocaleString()}</Td>
                            <Td>{model.rmse.toFixed(4)}</Td>
                            <Td>
                                <Button
                                    size="sm"
                                    colorScheme="blue"
                                    variant="outline"
                                    onClick={() => alert('切換版本功能待實作')}
                                >
                                    切換版本
                                </Button>
                            </Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    )
}
