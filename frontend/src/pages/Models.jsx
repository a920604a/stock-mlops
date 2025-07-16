// frontend/src/pages/Models.jsx
import React from 'react';
import {
    Box, Tabs, TabList, TabPanels, Tab, TabPanel,
    Heading, useToast
} from '@chakra-ui/react';
import ModelList from '../components/ModelList';
import PredictForm from '../components/PredictForm';
import TrainForm from '../components/TrainForm';

export default function ModelsPage() {
    const toast = useToast();

    // Function to show a toast message
    const showToast = (title, description, status) => {
        toast({
            title: title,
            description: description,
            status: status,
            duration: 5000,
            isClosable: true,
            position: "top-right",
        });
    };

    return (
        <Box p={6} maxW="1200px" mx="auto">
            <Heading size="lg" mb={6} textAlign="center" color="teal.600">📦 模型管理中心</Heading>
            <Tabs isFitted variant="enclosed" colorScheme="teal" rounded="lg" overflow="hidden" shadow="md">
                <TabList mb="1em" bg="teal.500" color="white" borderBottom="none">
                    <Tab _selected={{ bg: "teal.700", color: "white" }} _hover={{ bg: "teal.600" }} py={3} fontWeight="bold" fontSize="lg" roundedTop="lg">已訓練模型</Tab>
                    <Tab _selected={{ bg: "teal.700", color: "white" }} _hover={{ bg: "teal.600" }} py={3} fontWeight="bold" fontSize="lg" roundedTop="lg">模型預測</Tab>
                    <Tab _selected={{ bg: "teal.700", color: "white" }} _hover={{ bg: "teal.600" }} py={3} fontWeight="bold" fontSize="lg" roundedTop="lg">模型訓練</Tab>
                </TabList>
                <TabPanels bg="white" p={6} roundedBottom="lg" shadow="inner">
                    <TabPanel>
                        <ModelList showToast={showToast} />
                    </TabPanel>
                    <TabPanel>
                        <PredictForm showToast={showToast} />
                    </TabPanel>
                    <TabPanel>
                        <TrainForm showToast={showToast} />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
}
