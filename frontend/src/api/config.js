// src/api/config.js
// export const BASE_URL = "/api";  // PRODUCTION, 改成統一使用 Nginx API Gateway 的路徑
export const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";


// WebSocket Gateway
export const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8010/ws";
// export const WS_URL = "/ws";
