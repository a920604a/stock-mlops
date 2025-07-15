// frontend/src/pages/Models.jsx
import {
    Box, Tabs, TabList, TabPanels, Tab, TabPanel,
    Heading,
} from '@chakra-ui/react'
import ModelList from '../components/ModelList'
import PredictForm from '../components/PredictForm'
import TrainForm from '../components/TrainForm'

export default function ModelsPage() {
    return (
        <Box p={6}>
            <Heading size="lg" mb={6}>📦 模型管理中心</Heading>
            <Tabs isFitted variant="enclosed">
                <TabList mb="1em">
                    <Tab>已訓練模型</Tab>
                    <Tab>模型預測</Tab>
                    <Tab>模型訓練</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <ModelList />
                    </TabPanel>
                    <TabPanel>
                        <PredictForm />
                    </TabPanel>
                    <TabPanel>
                        <TrainForm />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    )
}
