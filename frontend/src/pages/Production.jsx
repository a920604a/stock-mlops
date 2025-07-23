import { Button, VStack } from '@chakra-ui/react';
import MetricsDashboard from '../components/MetricsDashboard.jsx';
export default function Production() {
    return (
        <VStack spacing={4} align="start">
            <Button
                as="a"
                href="http://localhost:3002/d/api-metrics/fastapi-metrics-dashboard?orgId=1&from=now-6h&to=now&timezone=browser&refresh=5s"
                target="_blank"
                rel="noopener noreferrer"
                colorScheme="blue"
            >
                開啟監控頁面
            </Button>
            <MetricsDashboard />
        </VStack>
    );
}
