import { useEffect, useState } from 'react';

export default function DriftMonitor() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws/stock_monitoring');
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setData((prev) => [...prev, msg].slice(-100)); // 保留最後100筆資料
    };
    return () => ws.close();
  }, []);

  return (
    <div>
      <h2>即時 Prediction Drift 監控</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
