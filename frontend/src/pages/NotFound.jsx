import { Link as RouterLink } from 'react-router-dom'
import { Box, Heading, Text, Link } from '@chakra-ui/react'

export default function NotFound() {
    return (
        <Box p={6}>
            <Heading as="h1" size="xl">
                🚫 找不到頁面
            </Heading>
            <Text mt={2}>
                請回到{' '}
                <Link as={RouterLink} to="/" color="blue.500" textDecoration="underline">
                    首頁
                </Link>
            </Text>
        </Box>
    )
}
