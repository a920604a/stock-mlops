import React from "react";
import ReactECharts from "echarts-for-react";
import { useMetricsWS } from "../hooks/useMetricsWS";
import { useAlertsWS } from "../hooks/useAlertsWS";

export default function MetricsDashboard() {
  const { cpuData, memData, httpReqData, httpDurData, predictSuccData, predictFailData, predictDurData } = useMetricsWS();
  const { alerts } = useAlertsWS();

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
