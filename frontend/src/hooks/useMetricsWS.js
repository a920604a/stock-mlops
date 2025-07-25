import { useEffect, useState } from "react";

export function useMetricsWS(maxPoints = 50) {
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
            // console.log("Received metrics data:", data);
            const timeLabel = new Date(data.timestamp * 1000).toLocaleTimeString();
            const m = data.metrics || {};

            if (typeof m.cpu_usage_seconds_total === "number") {
                setCpuData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.cpu_usage_seconds_total] }));
            }
            if (typeof m.memory_resident_bytes === "number") {
                setMemData((prev) => addDataPoint(prev, { name: timeLabel, value: [timeLabel, m.memory_resident_bytes / (1024 * 1024)] }));
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

        ws.onopen = () => console.log("WebSocket connected (metrics)");
        ws.onclose = () => console.log("WebSocket disconnected (metrics)");

        return () => ws.close();
    }, [maxPoints]);

    return { cpuData, memData, httpReqData, httpDurData, predictSuccData, predictFailData, predictDurData };
}
