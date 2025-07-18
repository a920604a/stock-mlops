import { useEffect, useState } from 'react';
import { Button } from '@chakra-ui/react';

export default function Production() {
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
      <Button
        as="a"
        href="http://localhost:3002/d/api-metrics/fastapi-metrics-dashboard?orgId=1&from=now-6h&to=now&timezone=browser&refresh=5s"
        target="_blank"
        rel="noopener noreferrer"
        colorScheme="blue"
      >
        開啟監控頁面
      </Button>

      <h2 style={{ marginTop: '20px' }}>即時 Prediction Drift 監控</h2>
      <pre
        style={{
          maxHeight: '400px',
          overflowY: 'auto',
          backgroundColor: '#f0f0f0',
          padding: '10px',
          borderRadius: '6px',
        }}
      >
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
