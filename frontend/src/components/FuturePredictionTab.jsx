import React, { useState, useEffect } from "react";
import {
  Box,
  VStack,
  HStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Heading,
  useToast,
  Input,
  Select,
  Button,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  CloseButton,
  Divider,
  Collapse,
} from "@chakra-ui/react";
import { fetchFuturePrediction, fetchPredictStatus, fetchPartialPredictStatus } from "../api/predictions";

export default function FuturePredictionTab() {
  const toast = useToast();

  const [ticker, setTicker] = useState("AAPL");
  const [exchange, setExchange] = useState("US");
  const [days, setDays] = useState(3);

  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(false);

  // 控制詳細訊息區是否展開
  const [showMsg, setShowMsg] = useState(true);

  const startPrediction = async () => {
    setError(null);
    setStatus("提交中...");
    setPredictions([]);
    try {
      const data = await fetchFuturePrediction(ticker, exchange, days);
      if (!data.task_id) throw new Error("沒有收到任務 ID");
      setTaskId(data.task_id);
      setStatus("任務已提交，等待結果...");
      setPolling(true);
      toast({
        title: "任務已提交",
        description: `開始預測 ${days} 天的未來股價`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (e) {
      setError(e.message);
      setStatus(null);
      setPolling(false);
      toast({
        title: "提交失敗",
        description: e.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const reset = () => {
    setTicker("AAPL");
    setExchange("US");
    setDays(3);
    setTaskId(null);
    setStatus(null);
    setPredictions([]);
    setError(null);
    setPolling(false);
  };

  useEffect(() => {
  if (!polling || !taskId) return;

  const interval = setInterval(async () => {
    try {
      const data = await fetchPartialPredictStatus(taskId); // 從後端拿部分結果

      setStatus(data.status || "未知狀態");

      // 新增部分結果，避免重複加
      if (data.result && data.result.length > 0) {
        setPredictions((prev) => {
          // 取出新資料，從 data.result 跟 prev 比較，避免重複
          // 假設資料是累積且排序好的，可用 slice
          if (data.result.length > prev.length) {
            return [...prev, ...data.result.slice(prev.length)];
          } else {
            return prev;
          }
        });
      }

      if (data.status === "completed" || data.status === "failed") {
        setPolling(false);
        if (data.status === "completed") {
          toast({
            title: "預測完成",
            description: "未來股價預測已完成",
            status: "success",
            duration: 3000,
            isClosable: true,
          });
        } else {
          setError(data.error || "任務失敗");
          toast({
            title: "預測失敗",
            description: data.error || "任務失敗",
            status: "error",
            duration: 5000,
            isClosable: true,
          });
        }
      }
    } catch (e) {
      setError(e.message);
      setPolling(false);
      toast({
        title: "查詢狀態錯誤",
        description: e.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  }, 3000);

  return () => clearInterval(interval);
}, [polling, taskId, toast]);

  return (
    <Box maxW="900px" mx="auto">
      <Heading size="md" mb={6} textAlign="center">
        未來多天股價預測模擬
      </Heading>

      {/* 輸入區 */}
      <VStack spacing={3} mb={6} align="stretch">
        <HStack>
          <Input
            placeholder="股票代號"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            isDisabled={polling}
          />
          <Select
            value={exchange}
            onChange={(e) => setExchange(e.target.value)}
            isDisabled={polling}
            w="100px"
          >
            <option value="US">US</option>
            <option value="TW">TW</option>
          </Select>
          <Input
            type="number"
            min={1}
            max={30}
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            isDisabled={polling}
            w="80px"
          />
          <Button
            colorScheme="teal"
            onClick={startPrediction}
            isLoading={polling}
            loadingText="預測進行中"
          >
            開始預測
          </Button>
          <Button onClick={reset} variant="outline" isDisabled={polling}>
            重置
          </Button>
        </HStack>
      </VStack>

      {/* 狀態區 */}
      {status && (
        <Alert status={error ? "error" : "info"} mb={4} borderRadius="md">
          <AlertIcon />
          <AlertDescription flex="1">{status}</AlertDescription>
          <CloseButton
            onClick={() => setStatus(null)}
            position="relative"
            right={-2}
            top={-1}
          />
        </Alert>
      )}

      {/* 預測結果表格 */}
      {predictions.length > 0 && (
        <>
          <Divider mb={4} />
          <Button size="sm" mb={2} onClick={() => setShowMsg(!showMsg)}>
            {showMsg ? "隱藏訊息" : "顯示訊息"}
          </Button>
          <Box maxH="400px" overflowY="auto" borderWidth="1px" borderRadius="md" p={2}>
            <Table variant="simple" size="sm" whiteSpace="normal">
              <Thead>
                <Tr>
                  <Th>日期</Th>
                  <Th>預測收盤價</Th>
                  <Th>實際收盤價</Th>
                  {showMsg && <Th>訊息</Th>}
                </Tr>
              </Thead>
              <Tbody>
                {predictions.map((p, i) => (
                  <Tr key={i}>
                    <Td>{p.target_date}</Td>
                    <Td>{p.predicted_close.toFixed(2)}</Td>
                    <Td>{p.actual_close ? p.actual_close.toFixed(2) : "-"}</Td>
                    {showMsg && <Td style={{ whiteSpace: "pre-wrap" }}>{p.msg}</Td>}
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        </>
      )}

      {/* 輪詢時的 spinner */}
      {polling && (
        <Box textAlign="center" mt={4}>
          <Spinner size="lg" />
          <Text mt={2}>預測中，請稍候...</Text>
        </Box>
      )}
    </Box>
  );
}
