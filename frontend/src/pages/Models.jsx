// frontend/src/pages/Models.jsx
import React from 'react';
import {
    Box, Tabs, TabList, TabPanels, Tab, TabPanel,
    Heading, useToast
} from '@chakra-ui/react';
import ModelRegisterForm from '../components/ModelRegisterForm'
import ModelList from '../components/ModelList';
import TrainStatus from '../components/TrainStatus'
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
            <Heading size="lg" mb={6} textAlign="TrainStatuscenter" color="teal.600">📦 模型管理中心</Heading>
            <Tabs variant="enclosed" colorScheme="teal" isFitted defaultIndex={1}>

                <TabList>
                    <Tab>模型註冊</Tab>
                    <Tab>模型清單</Tab>
                    <Tab>訓練狀態</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                    <ModelRegisterForm showToast={showToast} />
                    </TabPanel>
                    <TabPanel>
                    <ModelList showToast={showToast} />
                    </TabPanel>
                    <TabPanel>
                    <TrainStatus showToast={showToast} />
                    </TabPanel>
                </TabPanels>
            </Tabs>

        </Box>
    );
}
