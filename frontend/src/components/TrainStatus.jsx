// src/components/TrainStatus.jsx
import { useState } from 'react'
import {
    Box, Heading, Input, Button, VStack, Alert, AlertIcon,
} from '@chakra-ui/react'
import { fetchTrainStatus } from '../api/model'

export default function TrainStatus() {
    const [taskId, setTaskId] = useState('')
    const [status, setStatus] = useState(null)
    const [error, setError] = useState(null)

    const handleFetchStatus = async () => {
        setError(null)
        setStatus(null)
        try {
            const data = await fetchTrainStatus(taskId)
            setStatus(data)
        } catch (err) {
            setError(err.response?.data?.detail || '查詢失敗')
        }
    }

    return (
        <Box p={6} maxW="md" mx="auto">
            <Heading size="lg" mb={4}>🕒 查詢訓練任務狀態</Heading>

            <VStack spacing={3} mb={4}>
                <Input
                    placeholder="輸入任務 ID"
                    value={taskId}
                    onChange={e => setTaskId(e.target.value)}
                />
                <Button colorScheme="teal" onClick={handleFetchStatus}>查詢狀態</Button>
            </VStack>

            {error && (
                <Alert status="error" mb={4}>
                    <AlertIcon />
                    {error}
                </Alert>
            )}

            {status && (
                <Box bg="gray.100" p={4} borderRadius="md" whiteSpace="pre-wrap">
                    <pre>{JSON.stringify(status, null, 2)}</pre>
                </Box>
            )}
        </Box>
    )
}
