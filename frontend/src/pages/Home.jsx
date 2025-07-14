import { Box, Heading, Text } from '@chakra-ui/react'

export default function Home() {
    return (
        <Box p={6}>
            <Heading as="h1" size="xl" mb={4}>
                📈 股票 MLOps 系統
            </Heading>
            <Text>這是一個包含訓練、預測、監控的完整專案。</Text>
        </Box>
    )
}
