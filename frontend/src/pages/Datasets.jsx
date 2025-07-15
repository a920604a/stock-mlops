import {
    Box, Heading, VStack, Input, Button, Table, Thead, Tr, Th, Tbody, Td,
    Alert, AlertIcon, Text, Spinner,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Datasets() {
    const [ticker, setTicker] = useState('')
    const [exchange, setExchange] = useState('US')
    const [startDate, setStartDate] = useState('')
    const [endDate, setEndDate] = useState('')
    const [datasets, setDatasets] = useState([])
    const [loading, setLoading] = useState(false)

    const fetchDatasets = async () => {
        setLoading(true)
        try {
            const res = await axios.get('http://localhost:8001/api/datasets')
            setDatasets(res.data)
        } catch (err) {
            console.error('載入資料集失敗')
        } finally {
            setLoading(false)
        }
    }

    const handleIngest = async () => {
        await axios.post('http://localhost:8001/api/datasets', {
            ticker,
            exchange,
            start_date: startDate,
            end_date: endDate,
        })
        fetchDatasets()
    }

    useEffect(() => {
        fetchDatasets()
    }, [])

    return (
        <Box p={6}>
            <Heading size="lg" mb={4}>📂 資料集管理</Heading>

            <VStack spacing={4} align="stretch" mb={6}>
                <Input placeholder="股票代號 (ex: AAPL)" value={ticker} onChange={e => setTicker(e.target.value)} />
                <Input placeholder="交易所 (ex: US)" value={exchange} onChange={e => setExchange(e.target.value)} />
                <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
                <Input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
                <Button colorScheme="blue" onClick={handleIngest}>新增 / 更新資料</Button>
            </VStack>

            {loading ? (
                <Spinner />
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
