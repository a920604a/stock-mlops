import React, { useState } from 'react';
import {
  Box, Tabs, TabList, TabPanels, Tab, TabPanel,
  Heading, useToast
} from '@chakra-ui/react';
import ModelRegisterForm from '../components/ModelRegisterForm';
import ModelList from '../components/ModelList';
import TrainStatus from '../components/TrainStatus';
import PredictionList from '../components/PredictionList';
import FuturePredictionTab from '../components/FuturePredictionTab'; // 新增的未來預測 Tab

export default function ModelsPage() {
  const toast = useToast();
  const [tabIndex, setTabIndex] = useState(1);


  const showToast = (title, description, status) => {
    toast({
      title,
      description,
      status,
      duration: 5000,
      isClosable: true,
      position: "top-right",
    });
  };

  return (
    <Box p={6} maxW="1200px" mx="auto">
      <Heading size="lg" mb={6} textAlign="center" color="teal.600">
        📦 模型管理中心
      </Heading>
      <Tabs
        variant="enclosed"
        colorScheme="teal"
        isFitted
        index={tabIndex}
        onChange={(index) => setTabIndex(index)}
      >
        <TabList>
          <Tab>模型註冊</Tab>
          <Tab>模型清單</Tab>
          <Tab>訓練狀態</Tab>
          <Tab>預測紀錄</Tab>
          <Tab>未來多天預測</Tab> {/* 新增 Tab */}
        </TabList>
        <TabPanels>
          <TabPanel>
            <ModelRegisterForm
              showToast={showToast}
              key={tabIndex === 0 ? "register" : "other"}
            />
          </TabPanel>
          <TabPanel>
            <ModelList
              showToast={showToast}
              key={tabIndex === 1 ? "list" : "other"}
            />
          </TabPanel>
          <TabPanel>
            <TrainStatus
              showToast={showToast}
              key={tabIndex === 2 ? "train" : "other"}
            />
          </TabPanel>
          <TabPanel>
            <PredictionList
              showToast={showToast}
              key={tabIndex === 3 ? "predict" : "other"}
            />
          </TabPanel>
          <TabPanel>
            <FuturePredictionTab />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}
