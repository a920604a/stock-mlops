import { Flex, Box, Link, HStack, Text } from '@chakra-ui/react'
import { NavLink } from 'react-router-dom'

const navItems = [
    { label: '首頁', path: '/' },
    { label: '預測', path: '/predict' },
    { label: '訓練', path: '/train' },
    { label: '模型管理', path: '/models' },
]

export default function TopBar() {
    return (
        <Flex
            as="header"
            bg="gray.800"
            color="white"
            px="6"
            py="4"
            alignItems="center"
            justifyContent="space-between"
            boxShadow="md"
        >
            <Box fontWeight="bold" fontSize="xl" cursor="pointer">
                📊 MLOps Stocks
            </Box>

            <HStack spacing="6" fontSize="md">
                {navItems.map(({ label, path }) => (
                    <NavLink
                        key={path}
                        to={path}
                        style={({ isActive }) => ({
                            color: isActive ? '#f6e05e' : 'white',
                            textDecoration: isActive ? 'underline' : 'none',
                        })}
                    >
                        <Text cursor="pointer" _hover={{ color: 'yellow.400' }}>
                            {label}
                        </Text>
                    </NavLink>
                ))}
            </HStack>
        </Flex>
    )
}
