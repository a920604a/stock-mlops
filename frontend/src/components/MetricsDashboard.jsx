import React, { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";

export default function MetricsDashboard() {
  const maxPoints = 50;

  // 各指標的時間序列資料
  const [cpuData, setCpuData] = useState([]);
  const [memData, setMemData] = useState([]);
  const [httpReqData, setHttpReqData] = useState([]);
  const [httpDurData, setHttpDurData] = useState([]);
  const [predictSuccData, setPredictSuccData] = useState([]);
  const [predictFailData, setPredictFailData] = useState([]);
  const [predictDurData, setPredictDurData] = useState([]);

  const addDataPoint = (data, value) => {
    const newData = [...data, value];
    if (newData.length > maxPoints) newData.shift();
    return newData;
  };

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8010/ws/metrics");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const timeLabel = new Date(data.timestamp * 1000).toLocaleTimeString();

      const m = data.metrics || {};

      if (typeof m.cpu_usage_seconds_total === "number") {
        setCpuData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.cpu_usage_seconds_total] }));
      }
      if (typeof m.memory_resident_bytes === "number") {
        const mbValue = m.memory_resident_bytes / (1024 * 1024);
        setMemData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, mbValue] }));
      }

      if (typeof m.http_requests_total === "number") {
        setHttpReqData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.http_requests_total] }));
      }
      if (typeof m.http_request_duration_avg === "number") {
        setHttpDurData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.http_request_duration_avg] }));
      }
      if (typeof m.predict_success_total === "number") {
        setPredictSuccData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.predict_success_total] }));
      }
      if (typeof m.predict_failure_total === "number") {
        setPredictFailData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.predict_failure_total] }));
      }
      if (typeof m.predict_duration_avg === "number") {
        setPredictDurData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.predict_duration_avg] }));
      }
    };

    ws.onopen = () => console.log("WebSocket connected");
    ws.onclose = () => console.log("WebSocket disconnected");

    return () => ws.close();
  }, []);

  // 各指標的 ECharts 配置
  const makeLineOption = (title, data, yName, unit = "") => ({
    title: { text: title },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", boundaryGap: false, data: data.map((item) => item.name) },
    yAxis: { type: "value", name: yName, axisLabel: { formatter: `{value}${unit}` } },
    series: [
      {
        name: title,
        type: "line",
        smooth: true,
        data: data.map((item) => item.value[1]),
        showSymbol: false,
        areaStyle: {},
      },
    ],
  });

  return (
    <div style={{ width: "100%", maxWidth: 900, margin: "auto" }}>
      <ReactECharts option={makeLineOption("CPU 使用秒數 (total)", cpuData, "秒")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("記憶體常駐大小", memData, "MB")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("HTTP 請求總數", httpReqData, "次數")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("HTTP 請求平均處理時間", httpDurData, "秒")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("成功預測次數", predictSuccData, "次")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("失敗預測次數", predictFailData, "次")} style={{ height: 250, marginBottom: 30 }} />
      <ReactECharts option={makeLineOption("預測平均耗時", predictDurData, "秒")} style={{ height: 250, marginBottom: 30 }} />
    </div>
  );
}
